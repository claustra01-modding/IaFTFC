package net.claustra01.iaftfc.mixin;

import net.claustra01.iaftfc.metal.DragonForgeOutputHeat;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(targets = "com.iafenvoy.iceandfire.item.block.entity.DragonForgeBlockEntity", remap = false)
public abstract class DragonForgeBlockEntityMixin {
    @Shadow(remap = false)
    public abstract ItemStack getItem(int slot);

    @Inject(method = "smeltItem", at = @At("TAIL"), require = 1, remap = false)
    private void iaftfc$heatDragonsteelOutput(CallbackInfo callback) {
        DragonForgeOutputHeat.apply(getItem(2));
    }
}
