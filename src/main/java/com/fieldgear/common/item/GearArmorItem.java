package com.fieldgear.common.item;

import com.fieldgear.client.renderer.GearArmorRenderer;
import com.fieldgear.common.gear.GoggleSystem;
import com.fieldgear.common.gear.PlateSystem;
import net.minecraft.ChatFormatting;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraftforge.client.extensions.common.IClientItemExtensions;
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.animatable.client.RenderProvider;
import software.bernie.geckolib.constant.DataTickets;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.renderer.GeoArmorRenderer;
import software.bernie.geckolib.util.GeckoLibUtil;

import javax.annotation.Nullable;
import java.util.List;
import java.util.function.Consumer;
import java.util.function.Supplier;

/**
 * A piece of armour rendered from a GeckoLib model rather than a flat texture
 * layer.
 *
 * All the per-piece variation — which .geo.json to draw, whether the visor
 * moves, whether goggles can be fitted — is data on the item instance or on the
 * stack's NBT, so one class covers the whole set.
 */
public class GearArmorItem extends ArmorItem implements GeoItem {

    private static final RawAnimation VISOR_OPEN =
            RawAnimation.begin().thenPlayAndHold("helmet_open");
    private static final RawAnimation VISOR_CLOSED =
            RawAnimation.begin().thenPlayAndHold("helmet_closed");
    private static final RawAnimation NVG_DOWN =
            RawAnimation.begin().thenPlayAndHold("nvg_down");
    private static final RawAnimation NVG_UP =
            RawAnimation.begin().thenPlayAndHold("nvg_up");

    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private final Supplier<Object> renderProvider = GeoItem.makeRenderer(this);

    /** Basename of the .geo.json / .png under geo|textures/item/armor/. */
    private final String modelName;
    /** Whether this piece ships an .animation.json at all. */
    private final boolean animated;

    public GearArmorItem(ArmorMaterial material, Type type, Properties properties,
                         String modelName, boolean animated) {
        super(material, type, properties);
        this.modelName = modelName;
        this.animated = animated;
    }

    public String getModelName() {
        return this.modelName;
    }

    public boolean isAnimated() {
        return this.animated;
    }

    // ------------------------------------------------------------ rendering --

    @Override
    public void createRenderer(Consumer<Object> consumer) {
        consumer.accept(new RenderProvider() {
            private GeoArmorRenderer<?> renderer;

            @Override
            public HumanoidModel<?> getHumanoidArmorModel(LivingEntity living, ItemStack stack,
                                                          EquipmentSlot slot,
                                                          HumanoidModel<?> original) {
                if (this.renderer == null) {
                    this.renderer = new GearArmorRenderer();
                }
                this.renderer.prepForRender(living, stack, slot, original);
                return this.renderer;
            }
        });
    }

    @Override
    public Supplier<Object> getRenderProvider() {
        return this.renderProvider;
    }

    @Override
    public void initializeClient(Consumer<IClientItemExtensions> consumer) {
        consumer.accept(new IClientItemExtensions() {
            @Override
            public HumanoidModel<?> getHumanoidArmorModel(LivingEntity living, ItemStack stack,
                                                          EquipmentSlot slot,
                                                          HumanoidModel<?> original) {
                Object provider = GearArmorItem.this.getRenderProvider().get();
                if (provider instanceof RenderProvider rp) {
                    return rp.getHumanoidArmorModel(living, stack, slot, original);
                }
                return original;
            }
        });
    }

    // ----------------------------------------------------------- animations --

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "visor", 0, this::visorState));
        controllers.add(new AnimationController<>(this, "nvg", 0, this::nvgState));
    }

    private PlayState visorState(AnimationState<GearArmorItem> state) {
        ItemStack stack = state.getData(DataTickets.ITEMSTACK);
        if (stack == null || !GoggleSystem.hasVisor(stack)) {
            return PlayState.STOP;
        }
        state.setAnimation(GoggleSystem.isVisorOpen(stack) ? VISOR_OPEN : VISOR_CLOSED);
        return PlayState.CONTINUE;
    }

    private PlayState nvgState(AnimationState<GearArmorItem> state) {
        ItemStack stack = state.getData(DataTickets.ITEMSTACK);
        if (stack == null || !GoggleSystem.isInstalled(stack)) {
            return PlayState.STOP;
        }
        state.setAnimation(GoggleSystem.isDown(stack) ? NVG_DOWN : NVG_UP);
        return PlayState.CONTINUE;
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return this.cache;
    }

    // ------------------------------------------------------------- tooltips --

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip,
                                TooltipFlag flag) {
        if (PlateSystem.accepts(stack)) {
            List<PlateSystem.Fitted> plates = PlateSystem.get(stack);
            if (plates.isEmpty()) {
                tooltip.add(Component.translatable("fieldgear.tooltip.no_plates")
                        .withStyle(ChatFormatting.DARK_GRAY));
            } else {
                tooltip.add(Component.translatable("fieldgear.tooltip.plates",
                                plates.size(), PlateSystem.MAX_PLATES)
                        .withStyle(ChatFormatting.GRAY));
                for (PlateSystem.Fitted f : plates) {
                    tooltip.add(Component.translatable("fieldgear.tooltip.plate_slot",
                                    f.item.getDescription().getString(),
                                    Math.round(f.condition() * 100.0F))
                            .withStyle(conditionColour(f.condition())));
                }
            }
        }

        if (GoggleSystem.hasMount(stack)) {
            Item installed = GoggleSystem.getInstalled(stack);
            if (installed == null) {
                tooltip.add(Component.translatable("fieldgear.tooltip.goggles_empty")
                        .withStyle(ChatFormatting.DARK_GRAY));
            } else {
                tooltip.add(Component.translatable("fieldgear.tooltip.goggles",
                                installed.getDescription().getString())
                        .withStyle(ChatFormatting.AQUA));
            }
        }

        if (GoggleSystem.hasVisor(stack)) {
            tooltip.add(Component.translatable("fieldgear.tooltip.visor")
                    .withStyle(ChatFormatting.DARK_GRAY));
        }
    }

    private static ChatFormatting conditionColour(float condition) {
        if (condition > 0.6F) {
            return ChatFormatting.GREEN;
        }
        return condition > 0.25F ? ChatFormatting.YELLOW : ChatFormatting.RED;
    }
}
