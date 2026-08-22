package com.fieldgear.client.renderer;

import com.fieldgear.client.model.GearArmorModel;
import com.fieldgear.common.item.GearArmorItem;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import software.bernie.geckolib.renderer.GeoItemRenderer;

/**
 * Draws the helmet as its 3D model when held, dropped, in an item frame, or in
 * an inventory slot, instead of a flat sprite.
 *
 * Reached through {@code IClientItemExtensions.getCustomRenderer()}, which
 * Minecraft only consults when the item's model has {@code builtin/entity} as
 * its parent — that is what {@code models/item/gear_base.json} sets up.
 *
 * <h2>Why the translate</h2>
 *
 * The geometry is authored where the armour has to sit: on the head, spanning
 * roughly y 24..34 in model units. That is about 1.8 blocks above the origin
 * the item renderer draws around, so rendered as an item it floats up out of
 * the slot instead of sitting in it.
 *
 * The fix has to happen <em>here</em> rather than as a {@code translation} in
 * the model's display block. Vanilla builds the display transform as
 * {@code T * R * S}, so a point is scaled, then rotated <em>about the origin</em>,
 * and only then translated — with the model still 1.8 blocks up when the
 * rotation happens, any GUI rotation swings it through a wide arc and the
 * translation needed to bring it back depends on the angle. A translate applied
 * inside {@code renderByItem} lands innermost, in model space, so the geometry
 * is centred on the origin <em>before</em> the display rotation is applied and
 * every context's transform can then be written normally.
 *
 * {@code verify_mod.py} checks {@link #MODEL_CENTRE_Y} against the actual
 * geometry, so regenerating the models cannot silently leave this stale.
 */
public class GearItemRenderer extends GeoItemRenderer<GearArmorItem> {

    /**
     * Height of the geometry's centre above the model origin, in model units
     * (16 per block). All three helmets sit within a tenth of a unit of this.
     */
    public static final float MODEL_CENTRE_Y = 28.80F;

    public GearItemRenderer() {
        super(new GearArmorModel());
    }

    @Override
    public void renderByItem(ItemStack stack, ItemDisplayContext context, PoseStack poseStack,
                             MultiBufferSource bufferSource, int packedLight, int packedOverlay) {
        poseStack.pushPose();
        poseStack.translate(0.0F, -MODEL_CENTRE_Y / 16.0F, 0.0F);
        super.renderByItem(stack, context, poseStack, bufferSource, packedLight, packedOverlay);
        poseStack.popPose();
    }
}
