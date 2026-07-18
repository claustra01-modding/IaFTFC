package net.claustra01.iaftfc.client;

import net.claustra01.iaftfc.metal.DragonsteelFluids;
import net.claustra01.iaftfc.metal.DragonsteelMetal;
import net.dries007.tfc.client.extensions.FluidRendererExtension;
import net.dries007.tfc.util.Helpers;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.extensions.common.RegisterClientExtensionsEvent;

public final class IaFTFCClientEvents {
    private static final ResourceLocation MOLTEN_STILL = Helpers.identifier("block/molten_still");
    private static final ResourceLocation MOLTEN_FLOW = Helpers.identifier("block/molten_flow");

    private IaFTFCClientEvents() {
    }

    public static void register(IEventBus modEventBus) {
        modEventBus.addListener(IaFTFCClientEvents::registerExtensions);
    }

    private static void registerExtensions(RegisterClientExtensionsEvent event) {
        for (DragonsteelMetal metal : DragonsteelMetal.values()) {
            event.registerFluidType(
                new FluidRendererExtension(0xFF000000 | metal.color(), MOLTEN_STILL, MOLTEN_FLOW, null, null),
                DragonsteelFluids.METALS.get(metal).getType()
            );
        }
    }
}
