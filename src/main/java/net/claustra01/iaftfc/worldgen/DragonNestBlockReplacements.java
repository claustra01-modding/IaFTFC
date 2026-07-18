package net.claustra01.iaftfc.worldgen;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;

/** Attribute-aware block substitutions used only while IaF CE generates dragon nests. */
public final class DragonNestBlockReplacements {
    private static final Block FIRE_CHEST = block("wood/chest/chestnut");
    private static final Block ICE_CHEST = block("wood/chest/white_cedar");
    private static final Block LIGHTNING_CHEST = block("wood/chest/blackwood");

    private DragonNestBlockReplacements() {
    }

    public static Block chestFor(Object structurePiece) {
        final String pieceClass = structurePiece.getClass().getSimpleName();
        if (pieceClass.startsWith("FireDragon")) {
            return FIRE_CHEST;
        }
        if (pieceClass.startsWith("IceDragon")) {
            return ICE_CHEST;
        }
        if (pieceClass.startsWith("LightningDragon")) {
            return LIGHTNING_CHEST;
        }
        return Blocks.CHEST;
    }

    private static Block block(String path) {
        return BuiltInRegistries.BLOCK
            .getOptional(ResourceLocation.fromNamespaceAndPath("tfc", path))
            .orElse(Blocks.CHEST);
    }
}
