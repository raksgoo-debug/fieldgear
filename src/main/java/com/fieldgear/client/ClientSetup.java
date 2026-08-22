package com.fieldgear.client;

import com.fieldgear.FieldGear;
import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.client.settings.KeyConflictContext;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.lwjgl.glfw.GLFW;

/** Client-only registration: keybinds. */
@Mod.EventBusSubscriber(modid = FieldGear.MODID, value = Dist.CLIENT,
        bus = Mod.EventBusSubscriber.Bus.MOD)
public final class ClientSetup {

    public static final String CATEGORY = "key.categories." + FieldGear.MODID;

    public static final KeyMapping TOGGLE_GEAR = new KeyMapping(
            "key." + FieldGear.MODID + ".toggle_visor",
            KeyConflictContext.IN_GAME,
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_V,
            CATEGORY);

    public static final KeyMapping REMOVE_GEAR = new KeyMapping(
            "key." + FieldGear.MODID + ".remove_gear",
            KeyConflictContext.IN_GAME,
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_B,
            CATEGORY);

    private ClientSetup() {
    }

    @SubscribeEvent
    public static void registerKeys(RegisterKeyMappingsEvent event) {
        event.register(TOGGLE_GEAR);
        event.register(REMOVE_GEAR);
    }
}
