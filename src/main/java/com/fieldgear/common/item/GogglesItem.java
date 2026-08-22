package com.fieldgear.common.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

import javax.annotation.Nullable;
import java.util.List;

/** Goggles that clip onto a helmet's shroud. */
public class GogglesItem extends Item {

    /** What lowering the goggles gives you. */
    public enum Vision {
        NIGHT_VISION,
        /** Night vision plus highlighting of nearby living entities. */
        THERMAL
    }

    private final Vision vision;

    public GogglesItem(Properties properties, Vision vision) {
        super(properties);
        this.vision = vision;
    }

    public Vision getVision() {
        return this.vision;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip,
                                TooltipFlag flag) {
        tooltip.add(Component.literal(this.vision == Vision.THERMAL ? "Thermal imaging" : "Image intensifier")
                .withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.literal("Right-click while wearing a helmet with a shroud")
                .withStyle(ChatFormatting.DARK_GRAY));
    }
}
