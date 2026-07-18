package net.claustra01.iaftfc.metal;

import net.dries007.tfc.common.LevelTier;
import net.dries007.tfc.util.Metal;
import net.dries007.tfc.util.registry.RegistryMetal;
import net.minecraft.core.Holder;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.material.MapColor;

public enum DragonsteelMetal implements RegistryMetal {
    FIRE("dragonsteel_fire", 0x6E211B),
    ICE("dragonsteel_ice", 0x6BADC9),
    LIGHTNING("dragonsteel_lightning", 0x4D3A69);

    private final String serializedName;
    private final int color;

    DragonsteelMetal(String serializedName, int color) {
        this.serializedName = serializedName;
        this.color = color;
    }

    @Override
    public String getSerializedName() {
        return serializedName;
    }

    public int color() {
        return color;
    }

    @Override
    public LevelTier toolTier() {
        return DragonsteelTier.INSTANCE;
    }

    @Override
    public Holder<ArmorMaterial> armorMaterial() {
        throw unsupported("armorMaterial");
    }

    @Override
    public int armorDurability(ArmorItem.Type type) {
        throw unsupported("armorDurability");
    }

    @Override
    public Block getBlock(Metal.BlockType type) {
        if (type == Metal.BlockType.BLOCK) {
            return DragonsteelBlocks.BLOCKS_BY_METAL.get(this).get();
        }
        if (type == Metal.BlockType.BLOCK_SLAB) {
            return DragonsteelBlocks.SLABS_BY_METAL.get(this).get();
        }
        if (type == Metal.BlockType.BLOCK_STAIRS) {
            return DragonsteelBlocks.STAIRS_BY_METAL.get(this).get();
        }
        if (type == Metal.BlockType.ANVIL) {
            return DragonsteelBlocks.ANVILS_BY_METAL.get(this).get();
        }
        throw unsupported("getBlock(" + type.name() + ")");
    }

    @Override
    public MapColor mapColor() {
        return MapColor.METAL;
    }

    @Override
    public Rarity rarity() {
        return Rarity.EPIC;
    }

    @Override
    public float weatheringResistance() {
        return -1.0F;
    }

    private UnsupportedOperationException unsupported(String method) {
        return new UnsupportedOperationException(method + " is not used by IaFTFC Dragonsteel: " + serializedName);
    }
}
