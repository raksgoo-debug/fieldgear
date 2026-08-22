package com.fieldgear.client.model;

import com.fieldgear.FieldGear;
import com.fieldgear.common.gear.GoggleSystem;
import com.fieldgear.common.item.GearArmorItem;
import com.fieldgear.compat.FracturePointCompat;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import software.bernie.geckolib.constant.DataTickets;
import software.bernie.geckolib.core.animatable.model.CoreGeoBone;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.model.GeoModel;

/**
 * Resolves which geometry, texture and animation file a given armour piece
 * uses, and hides the NVG bone on helmets that have no goggles fitted.
 *
 * Hiding a bone per-stack is what lets one model serve both the bare helmet and
 * the goggled one, instead of shipping two geometries and swapping between them.
 */
public class GearArmorModel extends GeoModel<GearArmorItem> {

    private static final String NVG_BONE = "nvg";

    @Override
    public ResourceLocation getModelResource(GearArmorItem item) {
        return new ResourceLocation(FieldGear.MODID,
                "geo/item/armor/" + item.getModelName() + ".geo.json");
    }

    @Override
    public ResourceLocation getTextureResource(GearArmorItem item) {
        return new ResourceLocation(FieldGear.MODID,
                "textures/item/armor/" + item.getModelName() + ".png");
    }

    @Override
    public ResourceLocation getAnimationResource(GearArmorItem item) {
        return new ResourceLocation(FieldGear.MODID,
                "animations/item/armor/" + item.getModelName() + ".animation.json");
    }

    @Override
    public void setCustomAnimations(GearArmorItem animatable, long instanceId,
                                    AnimationState<GearArmorItem> animationState) {
        super.setCustomAnimations(animatable, instanceId, animationState);

        CoreGeoBone nvg = getAnimationProcessor().getBone(NVG_BONE);
        if (nvg == null) {
            return;     // this piece has no goggle hardware
        }
        ItemStack stack = animationState == null ? null : animationState.getData(DataTickets.ITEMSTACK);
        // Show the hardware for our own goggles or for a set Fracture Point
        // mounted: its render layer is class-gated and will not draw on our
        // helmet, so we draw it off its NBT instead.
        boolean fitted = stack != null
                && (GoggleSystem.isInstalled(stack) || FracturePointCompat.hasMountedGoggles(stack));
        nvg.setHidden(!fitted);
    }
}
