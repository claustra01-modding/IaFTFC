package net.claustra01.iaftfc.metal;

import java.util.Collections;
import java.util.EnumMap;
import java.util.Map;

import net.claustra01.iaftfc.IaFTFC;
import net.dries007.tfc.util.Metal;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class DragonsteelItems {
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(IaFTFC.MOD_ID);

    private static final Metal.ItemType[] ITEM_TYPES = {
        Metal.ItemType.INGOT,
        Metal.ItemType.DOUBLE_INGOT,
        Metal.ItemType.SHEET,
        Metal.ItemType.DOUBLE_SHEET,
        Metal.ItemType.ROD,
        Metal.ItemType.AXE_HEAD,
        Metal.ItemType.HOE_HEAD,
        Metal.ItemType.PICKAXE_HEAD,
        Metal.ItemType.SHOVEL_HEAD,
        Metal.ItemType.SWORD_BLADE,
        Metal.ItemType.UNFINISHED_HELMET,
        Metal.ItemType.UNFINISHED_CHESTPLATE,
        Metal.ItemType.UNFINISHED_GREAVES,
        Metal.ItemType.UNFINISHED_BOOTS
    };

    public static final Map<DragonsteelMetal, Map<Metal.ItemType, DeferredItem<Item>>> METAL_ITEMS = registerMetalItems();
    public static final Map<DragonsteelMetal, DeferredItem<?>> METAL_BLOCK_ITEMS = registerBlockItems(DragonsteelBlocks.BLOCKS_BY_METAL, "block", "");
    public static final Map<DragonsteelMetal, DeferredItem<?>> METAL_SLAB_ITEMS = registerBlockItems(DragonsteelBlocks.SLABS_BY_METAL, "block", "_slab");
    public static final Map<DragonsteelMetal, DeferredItem<?>> METAL_STAIRS_ITEMS = registerBlockItems(DragonsteelBlocks.STAIRS_BY_METAL, "block", "_stairs");
    public static final Map<DragonsteelMetal, DeferredItem<?>> METAL_ANVIL_ITEMS = registerBlockItems(DragonsteelBlocks.ANVILS_BY_METAL, "anvil", "");

    private DragonsteelItems() {
    }

    private static Map<DragonsteelMetal, Map<Metal.ItemType, DeferredItem<Item>>> registerMetalItems() {
        final EnumMap<DragonsteelMetal, Map<Metal.ItemType, DeferredItem<Item>>> allItems = new EnumMap<>(DragonsteelMetal.class);
        for (DragonsteelMetal metal : DragonsteelMetal.values()) {
            final EnumMap<Metal.ItemType, DeferredItem<Item>> items = new EnumMap<>(Metal.ItemType.class);
            for (Metal.ItemType type : ITEM_TYPES) {
                final String form = type.name().toLowerCase(java.util.Locale.ROOT);
                items.put(type, ITEMS.register("metal/" + form + "/" + metal.getSerializedName(), () -> type.create(metal)));
            }
            allItems.put(metal, Collections.unmodifiableMap(items));
        }
        return Collections.unmodifiableMap(allItems);
    }

    private static Map<DragonsteelMetal, DeferredItem<?>> registerBlockItems(
        Map<DragonsteelMetal, ? extends java.util.function.Supplier<? extends Block>> blocks,
        String form,
        String suffix
    ) {
        final EnumMap<DragonsteelMetal, DeferredItem<?>> items = new EnumMap<>(DragonsteelMetal.class);
        for (DragonsteelMetal metal : DragonsteelMetal.values()) {
            final String id = "metal/" + form + "/" + metal.getSerializedName() + suffix;
            items.put(metal, ITEMS.registerSimpleBlockItem(id, blocks.get(metal)));
        }
        return Collections.unmodifiableMap(items);
    }
}
