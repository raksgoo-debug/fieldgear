package com.fieldgear.common.gear;

import com.fieldgear.common.item.PlateItem;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.ArrayList;
import java.util.List;

/**
 * Ballistic plates carried inside a chestplate's NBT.
 *
 * Storing them on the stack rather than in a capability means they ride along
 * with the item for free — chests, ender chests, death drops and client sync
 * all just work, which is what makes the system safe in multiplayer.
 */
public final class PlateSystem {

    public static final String TAG_PLATES = "FieldGearPlates";
    private static final String KEY_ID = "id";
    private static final String KEY_DURABILITY = "dur";
    private static final String KEY_MAX = "max";

    /** Front and back. */
    public static final int MAX_PLATES = 2;

    private PlateSystem() {
    }

    /** One fitted plate. */
    public static final class Fitted {
        public final Item item;
        public int durability;
        public final int max;

        public Fitted(Item item, int durability, int max) {
            this.item = item;
            this.durability = durability;
            this.max = max;
        }

        public float condition() {
            return this.max <= 0 ? 0.0F : (float) this.durability / (float) this.max;
        }
    }

    public static boolean accepts(ItemStack armour) {
        return !armour.isEmpty() && armour.is(GearTags.PLATE_COMPATIBLE);
    }

    public static List<Fitted> get(ItemStack armour) {
        List<Fitted> out = new ArrayList<>();
        CompoundTag tag = armour.getTag();
        if (tag == null || !tag.contains(TAG_PLATES, Tag.TAG_LIST)) {
            return out;
        }
        ListTag list = tag.getList(TAG_PLATES, Tag.TAG_COMPOUND);
        for (int i = 0; i < list.size(); i++) {
            CompoundTag entry = list.getCompound(i);
            Item item = ForgeRegistries.ITEMS.getValue(new ResourceLocation(entry.getString(KEY_ID)));
            if (item == null) {
                continue;   // plate item from a mod that is no longer installed
            }
            out.add(new Fitted(item, entry.getInt(KEY_DURABILITY), entry.getInt(KEY_MAX)));
        }
        return out;
    }

    private static void save(ItemStack armour, List<Fitted> plates) {
        if (plates.isEmpty()) {
            if (armour.getTag() != null) {
                armour.getTag().remove(TAG_PLATES);
            }
            return;
        }
        ListTag list = new ListTag();
        for (Fitted f : plates) {
            ResourceLocation id = ForgeRegistries.ITEMS.getKey(f.item);
            if (id == null) {
                continue;
            }
            CompoundTag entry = new CompoundTag();
            entry.putString(KEY_ID, id.toString());
            entry.putInt(KEY_DURABILITY, f.durability);
            entry.putInt(KEY_MAX, f.max);
            list.add(entry);
        }
        armour.getOrCreateTag().put(TAG_PLATES, list);
    }

    /** @return true if the plate was fitted. */
    public static boolean insert(ItemStack armour, ItemStack plateStack) {
        if (!accepts(armour) || !(plateStack.getItem() instanceof PlateItem plate)) {
            return false;
        }
        List<Fitted> plates = get(armour);
        if (plates.size() >= MAX_PLATES) {
            return false;
        }
        plates.add(new Fitted(plate, plate.getPlateDurability(), plate.getPlateDurability()));
        save(armour, plates);
        return true;
    }

    /** Pops the most recently fitted plate back out, carrying its wear with it. */
    public static ItemStack removeLast(ItemStack armour) {
        List<Fitted> plates = get(armour);
        if (plates.isEmpty()) {
            return ItemStack.EMPTY;
        }
        Fitted removed = plates.remove(plates.size() - 1);
        save(armour, plates);

        ItemStack out = new ItemStack(removed.item);
        if (removed.item instanceof PlateItem && removed.durability < removed.max) {
            // carry wear across as vanilla item damage so it reads in a tooltip
            int maxDamage = out.getMaxDamage();
            if (maxDamage > 0) {
                float lost = 1.0F - removed.condition();
                out.setDamageValue(Math.min(maxDamage - 1, (int) (maxDamage * lost)));
            }
        }
        return out;
    }

    /**
     * Runs incoming damage through the fitted plates.
     *
     * Plates soak first and wear down doing it; whatever they cannot take passes
     * through to the wearer. Returns the damage still to be applied.
     */
    public static float absorb(ItemStack armour, float damage) {
        if (damage <= 0.0F || !accepts(armour)) {
            return damage;
        }
        List<Fitted> plates = get(armour);
        if (plates.isEmpty()) {
            return damage;
        }

        float remaining = damage;
        boolean changed = false;
        for (int i = plates.size() - 1; i >= 0 && remaining > 0.0F; i--) {
            Fitted f = plates.get(i);
            if (f.durability <= 0) {
                continue;
            }
            int level = (f.item instanceof PlateItem p) ? p.getProtectionLevel() : 1;
            // a plate can take a share of the hit proportional to its level
            float capacity = Math.min(remaining, level * 1.5F);
            float taken = Math.min(capacity, f.durability);
            f.durability -= (int) Math.ceil(taken);
            remaining -= taken;
            changed = true;
        }

        if (changed) {
            plates.removeIf(f -> f.durability <= 0);
            save(armour, plates);
        }
        return Math.max(0.0F, remaining);
    }

    public static int countIntact(ItemStack armour) {
        int n = 0;
        for (Fitted f : get(armour)) {
            if (f.durability > 0) {
                n++;
            }
        }
        return n;
    }
}
