package com.fieldgear.common.gear;

import com.fieldgear.FieldGear;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.ItemTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;

/**
 * Tags drive which gear supports which feature, so adding a new helmet to the
 * goggle system is a datapack edit rather than a code change.
 */
public final class GearTags {

    /** Chestplates that accept ballistic plates. */
    public static final TagKey<Item> PLATE_COMPATIBLE = tag("plate_compatible");
    /** Helmets with a shroud that goggles can be fitted to. */
    public static final TagKey<Item> GOGGLE_MOUNT = tag("goggle_mount");
    /** Helmets whose visor can be raised. */
    public static final TagKey<Item> HAS_VISOR = tag("has_visor");
    /** Every ballistic plate item. */
    public static final TagKey<Item> PLATES = tag("plates");
    /** Every goggle item. */
    public static final TagKey<Item> GOGGLES = tag("goggles");

    private GearTags() {
    }

    private static TagKey<Item> tag(String name) {
        return ItemTags.create(new ResourceLocation(FieldGear.MODID, name));
    }
}
