package com.fieldgear.client;

import com.fieldgear.FieldGear;
import com.fieldgear.common.net.GearActionPacket;
import com.fieldgear.common.net.ModNet;
import net.minecraft.client.Minecraft;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * Turns keypresses into packets. The client never changes gear state itself —
 * it asks the server, which owns the item NBT.
 */
@Mod.EventBusSubscriber(modid = FieldGear.MODID, value = Dist.CLIENT,
        bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class ClientEvents {

    private ClientEvents() {
    }

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.screen != null) {
            return;
        }
        while (ClientSetup.TOGGLE_GEAR.consumeClick()) {
            ModNet.sendToServer(new GearActionPacket(GearActionPacket.Action.TOGGLE));
        }
        while (ClientSetup.REMOVE_GEAR.consumeClick()) {
            ModNet.sendToServer(new GearActionPacket(GearActionPacket.Action.REMOVE));
        }
    }
}
