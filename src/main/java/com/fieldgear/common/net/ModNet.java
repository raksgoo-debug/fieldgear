package com.fieldgear.common.net;

import com.fieldgear.FieldGear;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.simple.SimpleChannel;

public final class ModNet {

    private static final String VERSION = "1";

    public static final SimpleChannel CHANNEL = NetworkRegistry.ChannelBuilder
            .named(new ResourceLocation(FieldGear.MODID, "main"))
            .networkProtocolVersion(() -> VERSION)
            .clientAcceptedVersions(VERSION::equals)
            .serverAcceptedVersions(VERSION::equals)
            .simpleChannel();

    private ModNet() {
    }

    public static void register() {
        CHANNEL.messageBuilder(GearActionPacket.class, 0, NetworkDirection.PLAY_TO_SERVER)
                .encoder(GearActionPacket::encode)
                .decoder(GearActionPacket::decode)
                .consumerMainThread(GearActionPacket::handle)
                .add();
    }

    public static void sendToServer(GearActionPacket packet) {
        CHANNEL.sendToServer(packet);
    }
}
