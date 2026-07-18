package net.claustra01.iaftfc.worldgen;

import java.util.Set;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.state.BlockState;

/** Maps TFC natural terrain to IaF CE breath-damaged blocks without losing it to Vanilla reversion. */
public final class DragonBreathBlockTransformation {
    private static final Set<String> SOIL_FORMS = Set.of(
        "dirt", "coarse_dirt", "rooted_dirt", "mud", "farmland"
    );
    private static final Set<String> STONE_FORMS = Set.of("raw", "hardened");
    private static final Set<String> COBBLE_FORMS = Set.of("cobble", "mossy_cobble");

    private DragonBreathBlockTransformation() {
    }

    public static BlockState fire(BlockState original) {
        return transform(original, "chared");
    }

    public static BlockState ice(BlockState original) {
        return transform(original, "frozen");
    }

    public static BlockState lightning(BlockState original) {
        return transform(original, "crackled");
    }

    private static BlockState transform(BlockState original, String effect) {
        final ResourceLocation originalId = BuiltInRegistries.BLOCK.getKey(original.getBlock());
        if (!originalId.getNamespace().equals("tfc")) {
            return null;
        }

        final TerrainForm form = classify(originalId.getPath());
        if (form == null) {
            return null;
        }

        final ResourceLocation transformedId = ResourceLocation.fromNamespaceAndPath(
            "iceandfire",
            effect + "_" + form.suffix
        );
        return BuiltInRegistries.BLOCK.getOptional(transformedId)
            .map(block -> block.defaultBlockState())
            .orElse(null);
    }

    private static TerrainForm classify(String path) {
        final String[] segments = path.split("/");
        if (segments.length == 2) {
            if (segments[0].equals("grass")) {
                return TerrainForm.GRASS;
            }
            if (segments[0].equals("grass_path")) {
                return TerrainForm.DIRT_PATH;
            }
            if (SOIL_FORMS.contains(segments[0])) {
                return TerrainForm.DIRT;
            }
            return null;
        }

        if (segments.length == 3 && segments[0].equals("rock")) {
            if (segments[1].equals("gravel")) {
                return TerrainForm.GRAVEL;
            }
            if (COBBLE_FORMS.contains(segments[1])) {
                return TerrainForm.COBBLESTONE;
            }
            if (STONE_FORMS.contains(segments[1])) {
                return TerrainForm.STONE;
            }
        }
        return null;
    }

    private enum TerrainForm {
        GRASS("grass"),
        DIRT("dirt"),
        DIRT_PATH("dirt_path"),
        GRAVEL("gravel"),
        COBBLESTONE("cobblestone"),
        STONE("stone");

        private final String suffix;

        TerrainForm(String suffix) {
            this.suffix = suffix;
        }
    }
}
