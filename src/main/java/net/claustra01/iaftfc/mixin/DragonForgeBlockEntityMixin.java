package net.claustra01.iaftfc.mixin;

import net.claustra01.iaftfc.metal.DragonForgeOutputHeat;
import net.claustra01.iaftfc.metal.DragonForgeHeatRecipe;
import java.util.Optional;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(targets = "com.iafenvoy.iceandfire.item.block.entity.DragonForgeBlockEntity", remap = false)
public abstract class DragonForgeBlockEntityMixin {
    @Unique
    private float iaftfc$pendingOutputTemperature;

    @Shadow(remap = false)
    public abstract ItemStack getItem(int slot);

    @Shadow(remap = false)
    public abstract Optional<?> getCurrentRecipe();

    @Inject(method = "smeltItem", at = @At("HEAD"), require = 1, remap = false)
    private void iaftfc$captureOutputTemperature(CallbackInfo callback) {
        iaftfc$pendingOutputTemperature = getCurrentRecipe()
            .map(recipe -> ((DragonForgeHeatRecipe) recipe).iaftfc$getOutputTemperature())
            .orElse(0.0F);
    }

    @Inject(method = "smeltItem", at = @At("TAIL"), require = 1, remap = false)
    private void iaftfc$heatDragonsteelOutput(CallbackInfo callback) {
        DragonForgeOutputHeat.apply(getItem(2), iaftfc$pendingOutputTemperature);
        iaftfc$pendingOutputTemperature = 0.0F;
    }
}
