package com.fieldgear.client.renderer;

import com.fieldgear.client.model.GearArmorModel;
import com.fieldgear.common.item.GearArmorItem;
import software.bernie.geckolib.renderer.GeoArmorRenderer;

/**
 * One renderer serves every piece in the set — {@link GearArmorModel} picks the
 * geometry and texture from the item it is handed.
 */
public class GearArmorRenderer extends GeoArmorRenderer<GearArmorItem> {

    public GearArmorRenderer() {
        super(new GearArmorModel());
    }
}
