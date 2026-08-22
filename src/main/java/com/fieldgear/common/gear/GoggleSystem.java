package com.fieldgear.common.gear;

import com.fieldgear.common.item.GogglesItem;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.ForgeRegistries;

import javax.annotation.Nullable;

/**
 * Goggles fitted to a helmet's shroud, plus their raised/lowered state.
 *
 * Both live in the helmet stack's NBT, which is what lets the renderer show or
 * hide the NVG bone per-stack from a single shared model.
 */
public final class GoggleSystem {

    public static final String TAG_GOGGLES = "FieldGearGoggles";
    public static final String TAG_ACTIVE = "FieldGearGogglesDown";
    public static final String TAG_VISOR = "FieldGearVisorOpen";

    private GoggleSystem() {
    }

    // ---------------------------------------------------------------- mount --

    public static boolean hasMount(ItemStack helmet) {
        return !helmet.isEmpty() && helmet.is(GearTags.GOGGLE_MOUNT);
    }

    public static boolean isInstalled(ItemStack helmet) {
        return getInstalled(helmet) != null;
    }

    @Nullable
    public static Item getInstalled(ItemStack helmet) {
        CompoundTag tag = helmet.getTag();
        if (tag == null || !tag.contains(TAG_GOGGLES)) {
            return null;
        }
        return ForgeRegistries.ITEMS.getValue(new ResourceLocation(tag.getString(TAG_GOGGLES)));
    }

    public static boolean install(ItemStack helmet, ItemStack goggles) {
        if (!hasMount(helmet) || isInstalled(helmet) || !(goggles.getItem() instanceof GogglesItem)) {
            return false;
        }
        ResourceLocation id = ForgeRegistries.ITEMS.getKey(goggles.getItem());
        if (id == null) {
            return false;
        }
        helmet.getOrCreateTag().putString(TAG_GOGGLES, id.toString());
        helmet.getOrCreateTag().putBoolean(TAG_ACTIVE, false);
        return true;
    }

    public static ItemStack remove(ItemStack helmet) {
        Item installed = getInstalled(helmet);
        if (installed == null) {
            return ItemStack.EMPTY;
        }
        CompoundTag tag = helmet.getTag();
        if (tag != null) {
            tag.remove(TAG_GOGGLES);
            tag.remove(TAG_ACTIVE);
        }
        return new ItemStack(installed);
    }

    // -------------------------------------------------------------- lowered --

    /** True when the goggles are down over the eyes rather than stowed up. */
    public static boolean isDown(ItemStack helmet) {
        CompoundTag tag = helmet.getTag();
        return tag != null && tag.getBoolean(TAG_ACTIVE);
    }

    public static void setDown(ItemStack helmet, boolean down) {
        helmet.getOrCreateTag().putBoolean(TAG_ACTIVE, down);
    }

    // ----------------------------------------------------------------- visor --

    public static boolean hasVisor(ItemStack helmet) {
        return !helmet.isEmpty() && helmet.is(GearTags.HAS_VISOR);
    }

    public static boolean isVisorOpen(ItemStack helmet) {
        CompoundTag tag = helmet.getTag();
        return tag != null && tag.getBoolean(TAG_VISOR);
    }

    public static void setVisorOpen(ItemStack helmet, boolean open) {
        helmet.getOrCreateTag().putBoolean(TAG_VISOR, open);
    }

    /** The vision mode the fitted goggles provide, or null if none are fitted. */
    @Nullable
    public static GogglesItem.Vision activeVision(ItemStack helmet) {
        if (!isDown(helmet)) {
            return null;
        }
        Item installed = getInstalled(helmet);
        return installed instanceof GogglesItem g ? g.getVision() : null;
    }
}
