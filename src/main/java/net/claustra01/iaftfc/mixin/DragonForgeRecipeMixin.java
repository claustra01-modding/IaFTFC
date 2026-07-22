package net.claustra01.iaftfc.mixin;

import net.claustra01.iaftfc.metal.DragonForgeHeatRecipe;
import net.claustra01.iaftfc.metal.DragonForgeOutputHeat;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;

@Mixin(targets = "com.iafenvoy.iceandfire.recipe.DragonForgeRecipe", remap = false)
public abstract class DragonForgeRecipeMixin implements DragonForgeHeatRecipe {
    @Unique
    private float iaftfc$outputTemperature;

    @Shadow(remap = false)
    public abstract ItemStack getResultItem();

    @Override
    public float iaftfc$getOutputTemperature() {
        return iaftfc$outputTemperature;
    }

    @Override
    public void iaftfc$setOutputTemperature(float temperature) {
        iaftfc$outputTemperature = temperature;
        DragonForgeOutputHeat.applyDisplay(getResultItem(), temperature);
    }
}
