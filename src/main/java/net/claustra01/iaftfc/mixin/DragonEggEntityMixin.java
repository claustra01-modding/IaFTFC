package net.claustra01.iaftfc.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import net.dries007.tfc.common.TFCTags;
import net.dries007.tfc.common.blocks.TFCBlocks;
import net.dries007.tfc.common.blocks.devices.CharcoalForgeBlock;
import net.dries007.tfc.common.blocks.devices.FirepitBlock;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Coerce;

@Mixin(targets = "com.iafenvoy.iceandfire.entity.DragonEggEntity", remap = false)
public abstract class DragonEggEntityMixin {
    @WrapOperation(
        method = "lambda$static$0",
        at = @At(
            value = "INVOKE",
            target = "Lcom/iafenvoy/uranus/object/BlockUtil;isBurning(Lnet/minecraft/world/level/block/state/BlockState;)Z"
        ),
        require = 1,
        remap = false
    )
    private static boolean iaftfc$acceptTfcFireDevices(
        BlockState state,
        Operation<Boolean> original,
        @Coerce Object egg,
        Level level,
        BlockPos eggPos,
        boolean mature
    ) {
        return original.call(state)
            || iaftfc$isActiveFireDevice(state)
            || iaftfc$isActiveFireDevice(level.getBlockState(eggPos.below()));
    }

    @WrapOperation(
        method = "lambda$static$1",
        at = @At(
            value = "INVOKE",
            target = "Lnet/minecraft/world/level/block/state/BlockState;is(Lnet/minecraft/world/level/block/Block;)Z"
        ),
        require = 1,
        remap = false
    )
    private static boolean iaftfc$acceptTfcFreshWater(
        BlockState state,
        Block expectedBlock,
        Operation<Boolean> original
    ) {
        return original.call(state, expectedBlock)
            || state.getFluidState().is(TFCTags.Fluids.ANY_FRESH_WATER);
    }

    private static boolean iaftfc$isActiveFireDevice(BlockState state) {
        if (state.is(TFCBlocks.FIREPIT.get())) {
            return state.hasProperty(FirepitBlock.LIT) && state.getValue(FirepitBlock.LIT);
        }
        if (state.is(TFCBlocks.CHARCOAL_FORGE.get())) {
            return state.hasProperty(CharcoalForgeBlock.HEAT) && state.getValue(CharcoalForgeBlock.HEAT) > 0;
        }
        return false;
    }
}
