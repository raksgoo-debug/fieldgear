package com.fieldgear.common.init;

import com.fieldgear.FieldGear;
import com.fieldgear.common.item.GearArmorItem;
import com.fieldgear.common.item.GearMaterial;
import com.fieldgear.common.item.GogglesItem;
import com.fieldgear.common.item.PlateItem;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.ArrayList;
import java.util.List;

public final class ModItems {

    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, FieldGear.MODID);
    public static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, FieldGear.MODID);

    /** Everything registered here, in the order it should appear in the tab. */
    private static final List<RegistryObject<? extends Item>> TAB_ORDER = new ArrayList<>();

    private ModItems() {
    }

    // ------------------------------------------------------------ materials --

    public static final RegistryObject<Item> RAW_FIBRE = simple("raw_fibre");
    public static final RegistryObject<Item> WOVEN_ARAMID = simple("woven_aramid");
    public static final RegistryObject<Item> CERAMIC_TILE = simple("ceramic_tile");
    public static final RegistryObject<Item> STEEL_BILLET = simple("steel_billet");

    // --------------------------------------------------------------- plates --

    public static final RegistryObject<PlateItem> STEEL_PLATE_III =
            plate("steel_plate_iii", 3, 260);
    public static final RegistryObject<PlateItem> CERAMIC_PLATE_IV =
            plate("ceramic_plate_iv", 4, 200);
    public static final RegistryObject<PlateItem> ARAMID_PLATE_IIIA =
            plate("aramid_plate_iiia", 2, 320);

    // -------------------------------------------------------------- goggles --

    public static final RegistryObject<GogglesItem> NVG_GOGGLES =
            goggles("nvg_goggles", GogglesItem.Vision.NIGHT_VISION);
    public static final RegistryObject<GogglesItem> THERMAL_GOGGLES =
            goggles("thermal_goggles", GogglesItem.Vision.THERMAL);

    // --------------------------------------------------------------- armour --

    public static final RegistryObject<GearArmorItem> BASTION_HELMET =
            armour("bastion_helmet", GearMaterial.COMPOSITE, ArmorItem.Type.HELMET, "bastion", true);
    public static final RegistryObject<GearArmorItem> K63_HELMET =
            armour("k63_helmet", GearMaterial.STEEL, ArmorItem.Type.HELMET, "k63", true);
    public static final RegistryObject<GearArmorItem> UNTAR_HELMET =
            armour("untar_helmet", GearMaterial.ARAMID, ArmorItem.Type.HELMET, "untar", false);

    // ------------------------------------------------------------------ tab --

    public static final RegistryObject<CreativeModeTab> GEAR_TAB = TABS.register("gear",
            () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.fieldgear.gear"))
                    .icon(() -> new ItemStack(BASTION_HELMET.get()))
                    .displayItems((params, output) -> {
                        for (RegistryObject<? extends Item> item : TAB_ORDER) {
                            output.accept(new ItemStack(item.get()));
                        }
                    })
                    .build());

    // ------------------------------------------------------------- builders --

    private static RegistryObject<Item> simple(String name) {
        RegistryObject<Item> obj = ITEMS.register(name, () -> new Item(new Item.Properties()));
        TAB_ORDER.add(obj);
        return obj;
    }

    private static RegistryObject<PlateItem> plate(String name, int level, int durability) {
        RegistryObject<PlateItem> obj = ITEMS.register(name,
                () -> new PlateItem(new Item.Properties().durability(durability),
                        level, durability));
        TAB_ORDER.add(obj);
        return obj;
    }

    private static RegistryObject<GogglesItem> goggles(String name, GogglesItem.Vision vision) {
        RegistryObject<GogglesItem> obj = ITEMS.register(name,
                () -> new GogglesItem(new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON),
                        vision));
        TAB_ORDER.add(obj);
        return obj;
    }

    private static RegistryObject<GearArmorItem> armour(String name, GearMaterial material,
                                                        ArmorItem.Type type, String model,
                                                        boolean animated) {
        RegistryObject<GearArmorItem> obj = ITEMS.register(name,
                () -> new GearArmorItem(material, type, new Item.Properties(), model, animated));
        TAB_ORDER.add(obj);
        return obj;
    }
}
