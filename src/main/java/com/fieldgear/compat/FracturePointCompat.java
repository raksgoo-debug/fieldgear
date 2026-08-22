package com.fieldgear.compat;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.fml.ModList;

/**
 * Fracture Point integration.
 *
 * Most of FP's gear systems turn out to be data-gated rather than class-gated,
 * so when it is installed this mod hands those systems over to it instead of
 * running duplicates. Verified against 3.0.0-PT2:
 *
 *   ArmorPlateCapabilityHandler  attaches to any ArmorItem of type CHESTPLATE
 *                                -> our rig joins by tag, no code needed
 *   WBArmorItem.canHaveGoggles   is `stack.is(CAN_HAVE_GOGGLES) || config`
 *                                -> our helmet joins by tag
 *   GoggleMounting               no instanceof at all
 *   HelmetBatteryTickHandler     reads NBT via static helpers, no instanceof
 *   HelmetVisionHandler          no instanceof — the vision effect just works
 *
 * The exceptions, which stay ours:
 *
 *   WarbornGoggleMountLayer      instanceof WBArmorItem -> FP will not draw
 *                                goggles on our helmet, so we draw them
 *                                ourselves off FP's NBT
 *   ToggleHelmetTopPacket        instanceof WBArmorItem -> our visor toggle
 *                                stays ours
 *   GoggleTooltip                instanceof WBArmorItem -> cosmetic only
 */
public final class FracturePointCompat {

    public static final String FRACTURE_POINT = "fracturepoint";

    /** NBT key Fracture Point stores mounted goggles under, on the helmet stack. */
    public static final String FP_INSERTED_GOGGLES = "InsertedGoggles";
    /** NBT key for the battery powering them. */
    public static final String FP_INSERTED_BATTERY = "InsertedNVGBattery";

    private static Boolean loaded;

    private FracturePointCompat() {
    }

    public static boolean isLoaded() {
        if (loaded == null) {
            loaded = ModList.get().isLoaded(FRACTURE_POINT);
        }
        return loaded;
    }

    /**
     * True when Fracture Point has goggles mounted on this helmet.
     *
     * Read straight off the stack rather than through FP's classes, so this
     * compiles and runs with or without the mod on the classpath.
     */
    public static boolean hasMountedGoggles(ItemStack helmet) {
        if (helmet.isEmpty()) {
            return false;
        }
        CompoundTag tag = helmet.getTag();
        if (tag == null || !tag.contains(FP_INSERTED_GOGGLES, Tag.TAG_COMPOUND)) {
            return false;
        }
        return !ItemStack.of(tag.getCompound(FP_INSERTED_GOGGLES)).isEmpty();
    }

    /** True when this mod should run its own plate and goggle handling. */
    public static boolean useOwnGearSystems() {
        return !isLoaded();
    }
}
