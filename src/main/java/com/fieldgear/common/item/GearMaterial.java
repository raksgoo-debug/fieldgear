package com.fieldgear.common.item;

import com.fieldgear.FieldGear;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.Ingredient;

import java.util.EnumMap;
import java.util.Map;

/**
 * Armour tiers for the set.
 *
 * Defence values are deliberately modest: the plate system is where most of the
 * protection comes from, so a bare chestplate should feel light.
 */
public enum GearMaterial implements ArmorMaterial {

    SCRAP("scrap", 15, protection(2, 5, 4, 1), 9, 0.0F, 0.0F,
            SoundEvents.ARMOR_EQUIP_IRON, () -> Ingredient.of(Items.IRON_INGOT)),

    STEEL("steel", 22, protection(3, 6, 5, 2), 9, 1.0F, 0.0F,
            SoundEvents.ARMOR_EQUIP_IRON, () -> Ingredient.of(Items.IRON_INGOT)),

    ARAMID("aramid", 20, protection(3, 6, 5, 2), 12, 0.5F, 0.0F,
            SoundEvents.ARMOR_EQUIP_LEATHER, () -> Ingredient.of(Items.LEATHER)),

    COMPOSITE("composite", 30, protection(4, 7, 6, 2), 14, 2.0F, 0.05F,
            SoundEvents.ARMOR_EQUIP_NETHERITE, () -> Ingredient.of(Items.NETHERITE_SCRAP));

    private static final int[] BASE_DURABILITY = {13, 15, 16, 11};

    private final String name;
    private final int durabilityMultiplier;
    private final Map<ArmorItem.Type, Integer> defence;
    private final int enchantmentValue;
    private final float toughness;
    private final float knockbackResistance;
    private final SoundEvent equipSound;
    private final IngredientSupplier repairIngredient;

    /** Kept as a tiny interface so the enum constants can stay lazy. */
    public interface IngredientSupplier {
        Ingredient get();
    }

    GearMaterial(String name, int durabilityMultiplier, Map<ArmorItem.Type, Integer> defence,
                 int enchantmentValue, float toughness, float knockbackResistance,
                 SoundEvent equipSound, IngredientSupplier repairIngredient) {
        this.name = name;
        this.durabilityMultiplier = durabilityMultiplier;
        this.defence = defence;
        this.enchantmentValue = enchantmentValue;
        this.toughness = toughness;
        this.knockbackResistance = knockbackResistance;
        this.equipSound = equipSound;
        this.repairIngredient = repairIngredient;
    }

    private static Map<ArmorItem.Type, Integer> protection(int helmet, int chest, int legs, int boots) {
        Map<ArmorItem.Type, Integer> map = new EnumMap<>(ArmorItem.Type.class);
        map.put(ArmorItem.Type.HELMET, helmet);
        map.put(ArmorItem.Type.CHESTPLATE, chest);
        map.put(ArmorItem.Type.LEGGINGS, legs);
        map.put(ArmorItem.Type.BOOTS, boots);
        return map;
    }

    @Override
    public int getDurabilityForType(ArmorItem.Type type) {
        return BASE_DURABILITY[type.ordinal()] * this.durabilityMultiplier;
    }

    @Override
    public int getDefenseForType(ArmorItem.Type type) {
        return this.defence.get(type);
    }

    @Override
    public int getEnchantmentValue() {
        return this.enchantmentValue;
    }

    @Override
    public SoundEvent getEquipSound() {
        return this.equipSound;
    }

    @Override
    public Ingredient getRepairIngredient() {
        return this.repairIngredient.get();
    }

    @Override
    public String getName() {
        return FieldGear.MODID + ":" + this.name;
    }

    @Override
    public float getToughness() {
        return this.toughness;
    }

    @Override
    public float getKnockbackResistance() {
        return this.knockbackResistance;
    }
}
