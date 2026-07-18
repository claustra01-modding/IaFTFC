package net.claustra01.iaftfc;

import com.mojang.logging.LogUtils;
import org.slf4j.Logger;

import net.claustra01.iaftfc.metal.DragonsteelBlocks;
import net.claustra01.iaftfc.metal.DragonsteelCreativeTab;
import net.claustra01.iaftfc.metal.DragonsteelFluids;
import net.claustra01.iaftfc.metal.DragonsteelItems;
import net.claustra01.iaftfc.worldgen.DragonWorldgen;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.loading.FMLEnvironment;

/**
 * Entry point for TerraFirmaCraft world generation and Dragonsteel integration
 * with Ice and Fire CE.
 */
@Mod(IaFTFC.MOD_ID)
public final class IaFTFC {
    public static final String MOD_ID = "iaftfc";
    public static final Logger LOGGER = LogUtils.getLogger();

    public IaFTFC(IEventBus modEventBus) {
        DragonsteelFluids.FLUID_TYPES.register(modEventBus);
        DragonsteelFluids.FLUIDS.register(modEventBus);
        DragonsteelBlocks.register(modEventBus);
        DragonsteelItems.ITEMS.register(modEventBus);
        DragonsteelCreativeTab.TABS.register(modEventBus);
        if (FMLEnvironment.dist == Dist.CLIENT) {
            net.claustra01.iaftfc.client.IaFTFCClientEvents.register(modEventBus);
        }
        DragonWorldgen.registerDiagnostics();
        LOGGER.info("IaFTFC initialized");
    }
}
