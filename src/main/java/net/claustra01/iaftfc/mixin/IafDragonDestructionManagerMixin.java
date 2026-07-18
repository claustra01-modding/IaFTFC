package net.claustra01.iaftfc.mixin;

import net.claustra01.iaftfc.worldgen.DragonBreathBlockTransformation;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(targets = "com.iafenvoy.iceandfire.entity.util.dragon.IafDragonDestructionManager", remap = false)
public abstract class IafDragonDestructionManagerMixin {
    @Inject(method = "transformBlockFire", at = @At("HEAD"), cancellable = true, require = 1, remap = false)
    private static void iaftfc$transformTfcBlockWithFire(
        BlockState original,
        CallbackInfoReturnable<BlockState> callback
    ) {
        replaceIfSupported(DragonBreathBlockTransformation.fire(original), callback);
    }

    @Inject(method = "transformBlockIce", at = @At("HEAD"), cancellable = true, require = 1, remap = false)
    private static void iaftfc$transformTfcBlockWithIce(
        BlockState original,
        CallbackInfoReturnable<BlockState> callback
    ) {
        replaceIfSupported(DragonBreathBlockTransformation.ice(original), callback);
    }

    @Inject(method = "transformBlockLightning", at = @At("HEAD"), cancellable = true, require = 1, remap = false)
    private static void iaftfc$transformTfcBlockWithLightning(
        BlockState original,
        CallbackInfoReturnable<BlockState> callback
    ) {
        replaceIfSupported(DragonBreathBlockTransformation.lightning(original), callback);
    }

    private static void replaceIfSupported(
        BlockState transformed,
        CallbackInfoReturnable<BlockState> callback
    ) {
        if (transformed != null) {
            callback.setReturnValue(transformed);
        }
    }
}
