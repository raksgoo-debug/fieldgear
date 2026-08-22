package com.fieldgear;

import com.fieldgear.common.event.GearEvents;
import com.fieldgear.common.init.ModItems;
import com.fieldgear.common.net.ModNet;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Entry point.
 *
 * The client half lives in {@link com.fieldgear.client.ClientSetup} and is only
 * touched from client-side event handlers, so the server never classloads
 * rendering code.
 */
@Mod(FieldGear.MODID)
public class FieldGear {

    public static final String MODID = "fieldgear";
    public static final Logger LOGGER = LoggerFactory.getLogger("Field Gear");

    public FieldGear() {
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();

        ModItems.ITEMS.register(modBus);
        ModItems.TABS.register(modBus);

        modBus.addListener(this::commonSetup);
        MinecraftForge.EVENT_BUS.register(GearEvents.class);
    }

    private void commonSetup(final FMLCommonSetupEvent event) {
        event.enqueueWork(ModNet::register);
    }
}
