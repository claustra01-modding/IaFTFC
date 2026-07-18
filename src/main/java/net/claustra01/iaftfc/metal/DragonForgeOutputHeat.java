package net.claustra01.iaftfc.metal;

import net.dries007.tfc.common.component.heat.HeatCapability;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;

/** Applies the temperature at which IaFTFC Dragonsteel leaves a Dragon Forge. */
public final class DragonForgeOutputHeat {
    public static final float OUTPUT_TEMPERATURE = 1600.0F;

    private DragonForgeOutputHeat() {
    }

    public static void apply(ItemStack stack) {
        if (stack.isEmpty()) {
            return;
        }

        final ResourceLocation itemId = BuiltInRegistries.ITEM.getKey(stack.getItem());
        if (itemId.getNamespace().equals("iaftfc")
            && itemId.getPath().startsWith("metal/ingot/dragonsteel_")) {
            HeatCapability.setTemperature(stack, OUTPUT_TEMPERATURE);
        }
    }
}
