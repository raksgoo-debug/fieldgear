package com.fieldgear.common.net;

import com.fieldgear.common.gear.GoggleSystem;
import com.fieldgear.common.gear.PlateSystem;
import com.fieldgear.compat.FracturePointCompat;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/**
 * The one packet the mod sends: the player pressed a gear key.
 *
 * Deciding what the key means is left entirely to the server, so the client
 * never needs to agree about what is fitted — it just reports the keypress.
 */
public class GearActionPacket {

    public enum Action {
        /** Raise/lower the visor, or stow/deploy fitted goggles. */
        TOGGLE,
        /** Pull out goggles, or failing that the last fitted plate. */
        REMOVE
    }

    private final Action action;

    public GearActionPacket(Action action) {
        this.action = action;
    }

    public static void encode(GearActionPacket msg, FriendlyByteBuf buf) {
        buf.writeEnum(msg.action);
    }

    public static GearActionPacket decode(FriendlyByteBuf buf) {
        return new GearActionPacket(buf.readEnum(Action.class));
    }

    public static void handle(GearActionPacket msg, Supplier<NetworkEvent.Context> ctx) {
        NetworkEvent.Context context = ctx.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            if (player == null) {
                return;
            }
            if (msg.action == Action.TOGGLE) {
                toggle(player);
            } else {
                remove(player);
            }
        });
        context.setPacketHandled(true);
    }

    private static void toggle(ServerPlayer player) {
        ItemStack helmet = player.getItemBySlot(EquipmentSlot.HEAD);
        if (helmet.isEmpty()) {
            return;
        }
        if (GoggleSystem.hasVisor(helmet)) {
            boolean open = !GoggleSystem.isVisorOpen(helmet);
            GoggleSystem.setVisorOpen(helmet, open);
            click(player, open ? 1.2F : 0.9F);
        } else if (GoggleSystem.isInstalled(helmet)) {
            boolean down = !GoggleSystem.isDown(helmet);
            GoggleSystem.setDown(helmet, down);
            click(player, down ? 1.4F : 1.0F);
        }
    }

    private static void remove(ServerPlayer player) {
        if (!FracturePointCompat.useOwnGearSystems()) {
            return;     // FP owns removal (its plate screen and slot mounting)
        }
        ItemStack helmet = player.getItemBySlot(EquipmentSlot.HEAD);
        ItemStack goggles = GoggleSystem.remove(helmet);
        if (!goggles.isEmpty()) {
            give(player, goggles);
            player.displayClientMessage(Component.translatable("fieldgear.msg.goggles_removed"), true);
            click(player, 0.8F);
            return;
        }

        ItemStack chest = player.getItemBySlot(EquipmentSlot.CHEST);
        ItemStack plate = PlateSystem.removeLast(chest);
        if (!plate.isEmpty()) {
            give(player, plate);
            player.displayClientMessage(Component.translatable("fieldgear.msg.plate_removed"), true);
            click(player, 0.7F);
        }
    }

    private static void give(ServerPlayer player, ItemStack stack) {
        if (!player.getInventory().add(stack)) {
            player.drop(stack, false);
        }
    }

    private static void click(ServerPlayer player, float pitch) {
        player.level().playSound(null, player.blockPosition(), SoundEvents.ARMOR_EQUIP_IRON,
                SoundSource.PLAYERS, 0.5F, pitch);
    }
}
