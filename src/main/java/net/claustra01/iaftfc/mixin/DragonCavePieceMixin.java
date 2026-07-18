package net.claustra01.iaftfc.mixin;

import net.claustra01.iaftfc.worldgen.DragonNestBlockReplacements;
import net.minecraft.world.level.block.Block;
import org.objectweb.asm.Opcodes;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

@Mixin(targets = "com.iafenvoy.iceandfire.world.structure.DragonCaveStructure$DragonCavePiece", remap = false)
public abstract class DragonCavePieceMixin {
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
}
