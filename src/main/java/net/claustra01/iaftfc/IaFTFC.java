package net.claustra01.iaftfc;

import com.mojang.logging.LogUtils;
import org.slf4j.Logger;

import net.claustra01.iaftfc.worldgen.DragonWorldgen;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;

/**
 * Entry point for the TerraFirmaCraft and Ice and Fire CE world-generation
 * compatibility mod.
 */
@Mod(IaFTFC.MOD_ID)
public final class IaFTFC {
    public static final String MOD_ID = "iaftfc";
    public static final Logger LOGGER = LogUtils.getLogger();

    public IaFTFC(IEventBus modEventBus, ModContainer modContainer) {
        DragonWorldgen.registerDiagnostics();
        LOGGER.info("IaFTFC initialized");
    }
}
