package com.fieldgear.common.event;

import com.fieldgear.common.gear.GoggleSystem;
import com.fieldgear.compat.FracturePointCompat;
import com.fieldgear.common.gear.PlateSystem;
import com.fieldgear.common.item.GogglesItem;
import net.minecraft.network.chat.Component;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

import java.util.List;

/**
 * Server-side behaviour for the gear systems.
 *
 * Fitting is done by right-clicking the component while wearing the piece it
 * belongs to, which avoids needing a custom screen while still being
 * discoverable from the item tooltip.
 */
public final class GearEvents {

    private static final int VISION_DURATION = 260;
    private static final int VISION_REFRESH_BELOW = 220;
    private static final double THERMAL_RANGE = 24.0D;
    private static final int THERMAL_GLOW_TICKS = 45;

    private GearEvents() {
    }

    // ------------------------------------------------------------- fitting --

    @SubscribeEvent
    public static void onRightClickItem(PlayerInteractEvent.RightClickItem event) {
        if (!FracturePointCompat.useOwnGearSystems()) {
            return;     // Fracture Point's mounting handles this for our gear too
        }
        Player player = event.getEntity();
        ItemStack held = event.getItemStack();
        if (player.level().isClientSide()) {
            return;
        }

        // goggles onto a helmet with a shroud
        if (held.getItem() instanceof GogglesItem) {
            ItemStack helmet = player.getItemBySlot(EquipmentSlot.HEAD);
            if (!GoggleSystem.hasMount(helmet)) {
                player.displayClientMessage(Component.translatable("fieldgear.msg.no_mount"), true);
                return;
            }
            if (GoggleSystem.install(helmet, held)) {
                held.shrink(1);
                player.displayClientMessage(
                        Component.translatable("fieldgear.msg.goggles_installed"), true);
                finish(event, player);
            }
            return;
        }

        // plates into a compatible chestplate
        ItemStack chest = player.getItemBySlot(EquipmentSlot.CHEST);
        if (PlateSystem.accepts(chest)) {
            if (PlateSystem.get(chest).size() >= PlateSystem.MAX_PLATES) {
                player.displayClientMessage(Component.translatable("fieldgear.msg.plate_full"), true);
                return;
            }
            if (PlateSystem.insert(chest, held)) {
                held.shrink(1);
                player.displayClientMessage(
                        Component.translatable("fieldgear.msg.plate_inserted"), true);
                finish(event, player);
            }
        }
    }

    private static void finish(PlayerInteractEvent.RightClickItem event, Player player) {
        player.swing(InteractionHand.MAIN_HAND, true);
        event.setCancellationResult(InteractionResult.SUCCESS);
        event.setCanceled(true);
    }

    // ------------------------------------------------------------- ballistics --

    /**
     * Plates soak damage before it reaches the wearer, and wear out doing it.
     *
     * Anything that ignores armour outright — falling out of the world, magic —
     * also ignores plates, otherwise a plate carrier would quietly become a
     * universal damage sponge.
     */
    @SubscribeEvent
    public static void onLivingHurt(LivingHurtEvent event) {
        if (!FracturePointCompat.useOwnGearSystems()) {
            return;     // FP's plate capability already absorbs; do not double-dip
        }
        if (event.getSource().is(DamageTypeTags.BYPASSES_ARMOR)
                || event.getSource().is(DamageTypeTags.BYPASSES_INVULNERABILITY)) {
            return;
        }
        LivingEntity entity = event.getEntity();
        if (entity.level().isClientSide()) {
            return;
        }
        ItemStack chest = entity.getItemBySlot(EquipmentSlot.CHEST);
        if (!PlateSystem.accepts(chest) || PlateSystem.countIntact(chest) == 0) {
            return;
        }
        float before = event.getAmount();
        float after = PlateSystem.absorb(chest, before);
        if (after < before) {
            event.setAmount(after);
        }
    }

    // ---------------------------------------------------------------- vision --

    @SubscribeEvent
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || event.player.level().isClientSide()) {
            return;
        }
        if (!FracturePointCompat.useOwnGearSystems()) {
            return;     // FP's HelmetVisionHandler drives vision for our helmets
        }
        Player player = event.player;
        ItemStack helmet = player.getItemBySlot(EquipmentSlot.HEAD);
        GogglesItem.Vision vision = GoggleSystem.activeVision(helmet);
        if (vision == null) {
            return;
        }

        MobEffectInstance current = player.getEffect(MobEffects.NIGHT_VISION);
        if (current == null || current.getDuration() < VISION_REFRESH_BELOW) {
            // ambient, no particles, no HUD icon — it should feel like optics,
            // not like drinking a potion
            player.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION,
                    VISION_DURATION, 0, true, false, false));
        }

        if (vision == GogglesItem.Vision.THERMAL && player.tickCount % 20 == 0) {
            AABB box = player.getBoundingBox().inflate(THERMAL_RANGE);
            List<LivingEntity> nearby = player.level()
                    .getEntitiesOfClass(LivingEntity.class, box, e -> e != player && e.isAlive());
            for (LivingEntity target : nearby) {
                target.addEffect(new MobEffectInstance(MobEffects.GLOWING,
                        THERMAL_GLOW_TICKS, 0, true, false, false));
            }
        }
    }
}
