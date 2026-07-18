package net.claustra01.iaftfc.metal;

import net.dries007.tfc.common.LevelTier;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.block.Block;

/** The tier used by Dragonsteel anvils. It is one level above TFC red/blue steel. */
public final class DragonsteelTier implements LevelTier {
    public static final DragonsteelTier INSTANCE = new DragonsteelTier();

    private DragonsteelTier() {
    }

    @Override
    public int level() {
        return 7;
    }

    @Override
    public int getUses() {
        return 8000;
    }

    @Override
    public float getSpeed() {
        return 13.0F;
    }

    @Override
    public float getAttackDamageBonus() {
        return 10.0F;
    }

    @Override
    public TagKey<Block> getIncorrectBlocksForDrops() {
        return BlockTags.INCORRECT_FOR_NETHERITE_TOOL;
    }

    @Override
    public int getEnchantmentValue() {
        return 24;
    }

    @Override
    public Ingredient getRepairIngredient() {
        return Ingredient.EMPTY;
    }
}
