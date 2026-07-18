package net.claustra01.iaftfc.worldgen;

import java.util.List;

import net.claustra01.iaftfc.IaFTFC;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.levelgen.structure.StructureSet;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.server.ServerStartedEvent;

/**
 * Registry keys and startup validation for IaFTFC's data-driven dragon
 * structure integration.
 */
public final class DragonWorldgen {
    private static final String ICE_AND_FIRE = "iceandfire";
    private static final String TFC = "tfc";

    private static final TagKey<Biome> DRAGON_STRUCTURE_LAND = TagKey.create(
            Registries.BIOME,
            id(IaFTFC.MOD_ID, "dragon_structure_land")
    );

    private static final List<DragonDefinition> DRAGONS = List.of(
            new DragonDefinition("fire", ICE_AND_FIRE, "dragon_roost", "dragon_cave"),
            new DragonDefinition("ice", IaFTFC.MOD_ID, "ice_dragon_roost", "ice_dragon_cave"),
            new DragonDefinition("lightning", IaFTFC.MOD_ID, "lightning_dragon_roost", "lightning_dragon_cave")
    );

    private DragonWorldgen() {
    }

    public static void registerDiagnostics() {
        NeoForge.EVENT_BUS.addListener(DragonWorldgen::onServerStarted);
    }

    private static void onServerStarted(ServerStartedEvent event) {
        RegistryAccess registries = event.getServer().registryAccess();
        Registry<Biome> biomes = registries.registryOrThrow(Registries.BIOME);
        Registry<StructureSet> structureSets = registries.registryOrThrow(Registries.STRUCTURE_SET);

        long landBiomeCount = countTfcBiomes(biomes, DRAGON_STRUCTURE_LAND);
        boolean valid = landBiomeCount > 0;
        if (!valid) {
            IaFTFC.LOGGER.error("IaFTFC land biome tag contains no TFC biomes");
        }

        for (DragonDefinition dragon : DRAGONS) {
            long dragonBiomeCount = countTfcBiomes(biomes, dragon.biomeTag());
            boolean roostPresent = structureSets.containsKey(dragon.roostSet());
            boolean cavePresent = structureSets.containsKey(dragon.caveSet());

            if (dragonBiomeCount == 0) {
                IaFTFC.LOGGER.error("No TFC biomes are enabled for {} dragon structures", dragon.name());
                valid = false;
            }
            if (!roostPresent || !cavePresent) {
                IaFTFC.LOGGER.error(
                        "Missing {} dragon climate structure sets (roost: {}, cave: {})",
                        dragon.name(), roostPresent, cavePresent
                );
                valid = false;
            }
        }

        if (valid) {
            IaFTFC.LOGGER.info(
                    "IaFTFC world generation ready: {} TFC land biomes and {} climate-filtered dragon structure sets",
                    landBiomeCount,
                    DRAGONS.size() * 2
            );
        }
    }

    private static long countTfcBiomes(Registry<Biome> biomes, TagKey<Biome> tag) {
        return biomes.getTag(tag)
                .stream()
                .flatMap(holders -> holders.stream())
                .map(Holder::unwrapKey)
                .flatMap(java.util.Optional::stream)
                .filter(key -> key.location().getNamespace().equals(TFC))
                .count();
    }

    private static ResourceLocation id(String namespace, String path) {
        return ResourceLocation.fromNamespaceAndPath(namespace, path);
    }

    private record DragonDefinition(String name, String structureSetNamespace, String roostSetPath, String caveSetPath) {
        private TagKey<Biome> biomeTag() {
            return TagKey.create(Registries.BIOME, id(ICE_AND_FIRE, "structure_gen/" + name));
        }

        private ResourceLocation roostSet() {
            return id(structureSetNamespace, roostSetPath);
        }

        private ResourceLocation caveSet() {
            return id(structureSetNamespace, caveSetPath);
        }
    }
}
