package com.fieldgear.client.renderer;

import com.fieldgear.client.model.GearArmorModel;
import com.fieldgear.common.item.GearArmorItem;
import software.bernie.geckolib.renderer.GeoItemRenderer;

/**
 * Draws the helmet as its 3D model when held, dropped, or in an item frame,
 * instead of a flat sprite.
 *
 * Reached through {@code IClientItemExtensions.getCustomRenderer()}, which
 * Minecraft only consults when the item's model has {@code builtin/entity} as
 * its parent — that is what {@code models/item/gear_base.json} sets up.
 */
public class GearItemRenderer extends GeoItemRenderer<GearArmorItem> {

    public GearItemRenderer() {
        super(new GearArmorModel());
    }
}
