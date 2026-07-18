package net.claustra01.iaftfc.worldgen;

import java.util.List;
import java.util.Map;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;

/** Converts IaF CE dragon-cave ores to rock-matched TFC ores. */
public final class DragonCaveOreReplacements {
    private static final String DEFAULT_ROCK = "granite";
    private static final int SEARCH_RADIUS = 8;
    private static final int DOWNWARD_SEARCH = 64;

    private static final List<String> COMMON = List.of(
        "rich_native_copper",
        "rich_malachite",
        "rich_tetrahedrite",
        "rich_hematite",
        "rich_magnetite",
        "rich_limonite"
    );
    private static final List<String> UNCOMMON = List.of(
        "rich_cassiterite",
        "rich_bismuthinite",
        "rich_sphalerite"
    );
    private static final List<String> RARE = List.of(
        "rich_native_gold",
        "rich_native_silver",
        "rich_garnierite"
    );

    private DragonCaveOreReplacements() {
    }

    public static BlockState replace(
        Object cavePiece,
        LevelAccessor level,
        BlockPos pos,
        BlockState original,
        OreCategory category,
        Map<BlockPos, String> rockCache
    ) {
        final String ore = switch (category) {
            case COMMON -> select(COMMON, pos);
            case UNCOMMON -> select(UNCOMMON, pos);
            case RARE -> select(RARE, pos);
            case ATTRIBUTE -> attributeOre(cavePiece);
        };
        if (ore == null) {
            return original;
        }

        final BlockPos section = new BlockPos(pos.getX() >> 4, pos.getY() >> 4, pos.getZ() >> 4);
        final String rock = rockCache.computeIfAbsent(section, ignored -> findRock(level, pos));
        final ResourceLocation oreId = ResourceLocation.fromNamespaceAndPath("tfc", "ore/" + ore + "/" + rock);
        return BuiltInRegistries.BLOCK.getOptional(oreId)
            .map(Block::defaultBlockState)
            .orElse(original);
    }

    private static String attributeOre(Object cavePiece) {
        final String pieceClass = cavePiece.getClass().getSimpleName();
        if (pieceClass.startsWith("FireDragon")) {
            return "ruby";
        }
        if (pieceClass.startsWith("IceDragon")) {
            return "sapphire";
        }
        if (pieceClass.startsWith("LightningDragon")) {
            return "topaz";
        }
        return null;
    }

    private static String select(List<String> ores, BlockPos pos) {
        long hash = pos.asLong();
        hash ^= hash >>> 33;
        hash *= 0xff51afd7ed558ccdl;
        hash ^= hash >>> 33;
        return ores.get((int) Math.floorMod(hash, ores.size()));
    }

    private static String findRock(LevelAccessor level, BlockPos origin) {
        final BlockPos.MutableBlockPos cursor = new BlockPos.MutableBlockPos();
        for (int radius = 1; radius <= SEARCH_RADIUS; radius++) {
            for (int x = -radius; x <= radius; x++) {
                for (int y = -radius; y <= radius; y++) {
                    for (int z = -radius; z <= radius; z++) {
                        if (Math.max(Math.max(Math.abs(x), Math.abs(y)), Math.abs(z)) != radius) {
                            continue;
                        }
                        cursor.setWithOffset(origin, x, y, z);
                        if (level.isOutsideBuildHeight(cursor)) {
                            continue;
                        }
                        final String rock = rockName(level.getBlockState(cursor));
                        if (rock != null) {
                            return rock;
                        }
                    }
                }
            }
        }

        cursor.set(origin);
        for (int distance = 1; distance <= DOWNWARD_SEARCH; distance++) {
            cursor.setY(origin.getY() - distance);
            if (level.isOutsideBuildHeight(cursor)) {
                break;
            }
            final String rock = rockName(level.getBlockState(cursor));
            if (rock != null) {
                return rock;
            }
        }
        return DEFAULT_ROCK;
    }

    private static String rockName(BlockState state) {
        final ResourceLocation id = BuiltInRegistries.BLOCK.getKey(state.getBlock());
        if (!id.getNamespace().equals("tfc") || !id.getPath().startsWith("rock/")) {
            return null;
        }
        final int lastSlash = id.getPath().lastIndexOf('/');
        if (lastSlash < 0 || lastSlash == id.getPath().length() - 1) {
            return null;
        }
        String rock = id.getPath().substring(lastSlash + 1);
        rock = stripSuffix(rock, "_stairs");
        rock = stripSuffix(rock, "_slab");
        rock = stripSuffix(rock, "_wall");
        return rock.isEmpty() ? null : rock;
    }

    private static String stripSuffix(String value, String suffix) {
        return value.endsWith(suffix) ? value.substring(0, value.length() - suffix.length()) : value;
    }

    public enum OreCategory {
        COMMON,
        UNCOMMON,
        RARE,
        ATTRIBUTE
    }
}
