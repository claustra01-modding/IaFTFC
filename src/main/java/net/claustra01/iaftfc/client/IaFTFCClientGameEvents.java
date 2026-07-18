package net.claustra01.iaftfc.client;

import java.util.Set;
import net.claustra01.iaftfc.IaFTFC;
import net.minecraft.ChatFormatting;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.player.ItemTooltipEvent;

@SuppressWarnings("removal")
@EventBusSubscriber(modid = IaFTFC.MOD_ID, value = Dist.CLIENT, bus = EventBusSubscriber.Bus.GAME)
public final class IaFTFCClientGameEvents {
    private static final Set<ResourceLocation> DISABLED_ITEMS = Set.of(
        item("silver_ingot"),
        item("silver_nugget"),
        item("silver_block"),
        item("raw_silver"),
        item("raw_silver_block"),
        item("silver_ore"),
        item("deepslate_silver_ore"),
        item("silver_axe"),
        item("silver_hoe"),
        item("silver_pickaxe"),
        item("silver_shovel"),
        item("silver_sword"),
        item("armor_silver_metal_helmet"),
        item("armor_silver_metal_chestplate"),
        item("armor_silver_metal_leggings"),
        item("armor_silver_metal_boots"),
        item("sapphire_gem"),
        item("sapphire_block"),
        item("sapphire_ore"),
        item("dragonsteel_fire_ingot"),
        item("dragonsteel_ice_ingot"),
        item("dragonsteel_lightning_ingot"),
        item("dragonsteel_fire_block"),
        item("dragonsteel_ice_block"),
        item("dragonsteel_lightning_block"),
        item("dragonarmor_copper_head"),
        item("dragonarmor_copper_neck"),
        item("dragonarmor_copper_body"),
        item("dragonarmor_copper_tail"),
        item("dragonarmor_diamond_head"),
        item("dragonarmor_diamond_neck"),
        item("dragonarmor_diamond_body"),
        item("dragonarmor_diamond_tail"),
        item("dragonarmor_gold_head"),
        item("dragonarmor_gold_neck"),
        item("dragonarmor_gold_body"),
        item("dragonarmor_gold_tail"),
        item("dragonarmor_netherite_head"),
        item("dragonarmor_netherite_neck"),
        item("dragonarmor_netherite_body"),
        item("dragonarmor_netherite_tail"),
        item("dragonarmor_silver_head"),
        item("dragonarmor_silver_neck"),
        item("dragonarmor_silver_body"),
        item("dragonarmor_silver_tail"),
        item("dragonsteel_fire_axe"),
        item("dragonsteel_fire_hoe"),
        item("dragonsteel_fire_pickaxe"),
        item("dragonsteel_fire_shovel"),
        item("dragonsteel_ice_axe"),
        item("dragonsteel_ice_hoe"),
        item("dragonsteel_ice_pickaxe"),
        item("dragonsteel_ice_shovel"),
        item("dragonsteel_lightning_axe"),
        item("dragonsteel_lightning_hoe"),
        item("dragonsteel_lightning_pickaxe"),
        item("dragonsteel_lightning_shovel")
    );

    private IaFTFCClientGameEvents() {
    }

    @SubscribeEvent
    public static void addItemTooltip(ItemTooltipEvent event) {
        final ResourceLocation itemId = BuiltInRegistries.ITEM.getKey(event.getItemStack().getItem());
        if (DISABLED_ITEMS.contains(itemId)) {
            event.getToolTip().add(Component.literal("[DISABLED]").withStyle(ChatFormatting.DARK_RED));
        }
    }

    private static ResourceLocation item(String path) {
        return ResourceLocation.fromNamespaceAndPath("iceandfire", path);
    }
}
