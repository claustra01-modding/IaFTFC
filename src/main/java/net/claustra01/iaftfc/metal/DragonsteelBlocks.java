package net.claustra01.iaftfc.metal;

import java.util.Collections;
import java.util.EnumMap;
import java.util.Map;

import net.claustra01.iaftfc.IaFTFC;
import net.dries007.tfc.common.blockentities.TFCBlockEntities;
import net.dries007.tfc.util.Metal;
import net.minecraft.world.level.block.Block;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.event.BlockEntityTypeAddBlocksEvent;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class DragonsteelBlocks {
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(IaFTFC.MOD_ID);
    public static final Map<DragonsteelMetal, DeferredBlock<Block>> BLOCKS_BY_METAL = register(Metal.BlockType.BLOCK, "block", "");
    public static final Map<DragonsteelMetal, DeferredBlock<Block>> SLABS_BY_METAL = register(Metal.BlockType.BLOCK_SLAB, "block", "_slab");
    public static final Map<DragonsteelMetal, DeferredBlock<Block>> STAIRS_BY_METAL = register(Metal.BlockType.BLOCK_STAIRS, "block", "_stairs");
    public static final Map<DragonsteelMetal, DeferredBlock<Block>> ANVILS_BY_METAL = register(Metal.BlockType.ANVIL, "anvil", "");

    private DragonsteelBlocks() {
    }

    public static void register(IEventBus modEventBus) {
        BLOCKS.register(modEventBus);
        modEventBus.addListener(DragonsteelBlocks::addBlockEntityValidBlocks);
    }

    private static void addBlockEntityValidBlocks(BlockEntityTypeAddBlocksEvent event) {
        final Block[] anvils = ANVILS_BY_METAL.values().stream()
            .map(DeferredBlock::get)
            .toArray(Block[]::new);
        event.modify(TFCBlockEntities.ANVIL.holder().get(), anvils);
    }

    private static Map<DragonsteelMetal, DeferredBlock<Block>> register(Metal.BlockType type, String form, String suffix) {
        final EnumMap<DragonsteelMetal, DeferredBlock<Block>> blocks = new EnumMap<>(DragonsteelMetal.class);
        for (DragonsteelMetal metal : DragonsteelMetal.values()) {
            final String id = "metal/" + form + "/" + metal.getSerializedName() + suffix;
            blocks.put(metal, BLOCKS.register(id, type.create(metal)));
        }
        return Collections.unmodifiableMap(blocks);
    }
}
