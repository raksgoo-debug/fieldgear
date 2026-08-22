package com.fieldgear.common.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

import javax.annotation.Nullable;
import java.util.List;

/** A ballistic plate that slots into a compatible chestplate. */
public class PlateItem extends Item {

    private final int protectionLevel;
    private final int plateDurability;

    public PlateItem(Properties properties, int protectionLevel, int plateDurability) {
        super(properties);
        this.protectionLevel = protectionLevel;
        this.plateDurability = plateDurability;
    }

    public int getProtectionLevel() {
        return this.protectionLevel;
    }

    public int getPlateDurability() {
        return this.plateDurability;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip,
                                TooltipFlag flag) {
        tooltip.add(Component.literal("Protection level " + this.protectionLevel)
                .withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.literal("Right-click while wearing a compatible rig to fit")
                .withStyle(ChatFormatting.DARK_GRAY));
    }
}
