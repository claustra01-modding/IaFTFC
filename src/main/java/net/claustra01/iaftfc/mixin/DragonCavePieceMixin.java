package net.claustra01.iaftfc.mixin;

import java.util.HashMap;
import java.util.Map;
import net.claustra01.iaftfc.worldgen.DragonCaveOreReplacements;
import net.claustra01.iaftfc.worldgen.DragonCaveOreReplacements.OreCategory;
import net.claustra01.iaftfc.worldgen.DragonNestBlockReplacements;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import org.objectweb.asm.Opcodes;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

@Mixin(targets = "com.iafenvoy.iceandfire.world.structure.DragonCaveStructure$DragonCavePiece", remap = false)
public abstract class DragonCavePieceMixin {
    @Unique
    private final Map<BlockPos, String> iaftfc$rockBySection = new HashMap<>();
    @Unique
    private OreCategory iaftfc$selectedOreCategory;
    @Unique
    private Block iaftfc$selectedOre;

    @Redirect(
        method = "setGoldPile",
        at = @At(
            value = "FIELD",
            target = "Lnet/minecraft/world/level/block/Blocks;CHEST:Lnet/minecraft/world/level/block/Block;",
            opcode = Opcodes.GETSTATIC
        ),
        require = 1,
        remap = false
    )
    private Block iaftfc$useTfcChest() {
        return DragonNestBlockReplacements.chestFor(this);
    }

    @Redirect(
        method = "lambda$createShell$2",
        at = @At(value = "INVOKE", target = "Ljava/util/List;get(I)Ljava/lang/Object;", ordinal = 0),
        require = 1,
        remap = false
    )
    private Object iaftfc$rememberAttributeOre(java.util.List<?> ores, int index) {
        return iaftfc$rememberOre(ores.get(index), OreCategory.ATTRIBUTE);
    }

    @Redirect(
        method = "lambda$createShell$2",
        at = @At(value = "INVOKE", target = "Ljava/util/List;get(I)Ljava/lang/Object;", ordinal = 1),
        require = 1,
        remap = false
    )
    private Object iaftfc$rememberRareOre(java.util.List<?> ores, int index) {
        return iaftfc$rememberOre(ores.get(index), OreCategory.RARE);
    }

    @Redirect(
        method = "lambda$createShell$2",
        at = @At(value = "INVOKE", target = "Ljava/util/List;get(I)Ljava/lang/Object;", ordinal = 2),
        require = 1,
        remap = false
    )
    private Object iaftfc$rememberUncommonOre(java.util.List<?> ores, int index) {
        return iaftfc$rememberOre(ores.get(index), OreCategory.UNCOMMON);
    }

    @Redirect(
        method = "lambda$createShell$2",
        at = @At(value = "INVOKE", target = "Ljava/util/List;get(I)Ljava/lang/Object;", ordinal = 3),
        require = 1,
        remap = false
    )
    private Object iaftfc$rememberCommonOre(java.util.List<?> ores, int index) {
        return iaftfc$rememberOre(ores.get(index), OreCategory.COMMON);
    }

    @Unique
    private Object iaftfc$rememberOre(Object selected, OreCategory category) {
        if (selected instanceof Block block) {
            iaftfc$selectedOre = block;
            iaftfc$selectedOreCategory = category;
        }
        return selected;
    }

    @Redirect(
        method = "lambda$createShell$2",
        at = @At(
            value = "INVOKE",
            target = "Lnet/minecraft/world/level/LevelAccessor;setBlock(Lnet/minecraft/core/BlockPos;Lnet/minecraft/world/level/block/state/BlockState;I)Z"
        ),
        require = 3,
        remap = false
    )
    private boolean iaftfc$replaceCaveOre(
        LevelAccessor targetLevel,
        BlockPos targetPos,
        BlockState targetState,
        int flags
    ) {
        if (targetState.getBlock() != iaftfc$selectedOre || iaftfc$selectedOreCategory == null) {
            return targetLevel.setBlock(targetPos, targetState, flags);
        }

        final BlockState replacement = DragonCaveOreReplacements.replace(
            this,
            targetLevel,
            targetPos,
            targetState,
            iaftfc$selectedOreCategory,
            iaftfc$rockBySection
        );
        iaftfc$selectedOre = null;
        iaftfc$selectedOreCategory = null;
        return targetLevel.setBlock(targetPos, replacement, flags);
    }
}
