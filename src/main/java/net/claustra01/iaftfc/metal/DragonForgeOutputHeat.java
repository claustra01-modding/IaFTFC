package net.claustra01.iaftfc.metal;

import net.dries007.tfc.common.component.heat.HeatCapability;
import net.dries007.tfc.common.component.heat.IHeat;
import net.minecraft.world.item.ItemStack;

/** Applies a recipe-defined temperature to a Dragon Forge output. */
public final class DragonForgeOutputHeat {
    private DragonForgeOutputHeat() {
    }

    public static void apply(ItemStack stack, float temperature) {
        if (stack.isEmpty() || temperature <= 0.0F) {
            return;
        }
        final IHeat heat = HeatCapability.get(stack);
        if (heat != null) {
            heat.setHeatCapacity(0.0F);
            heat.setTemperature(temperature);
        }
    }

    public static void applyDisplay(ItemStack stack, float temperature) {
        if (stack.isEmpty() || temperature <= 0.0F) {
            return;
        }
        final IHeat heat = HeatCapability.get(stack);
        if (heat != null) {
            heat.setHeatCapacity(Float.MAX_VALUE);
            heat.setTemperature(temperature);
        }
    }
}
