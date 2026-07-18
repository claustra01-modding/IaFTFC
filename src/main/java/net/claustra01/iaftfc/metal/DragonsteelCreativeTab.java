package net.claustra01.iaftfc.metal;

import java.util.Comparator;

import net.claustra01.iaftfc.IaFTFC;
import net.dries007.tfc.util.Metal;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class DragonsteelCreativeTab {
    public static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, IaFTFC.MOD_ID);
    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> DRAGONSTEEL = TABS.register("dragonsteel",
        () -> CreativeModeTab.builder()
            .title(Component.translatable("itemGroup.iaftfc.dragonsteel"))
            .icon(() -> DragonsteelItems.METAL_ITEMS.get(DragonsteelMetal.FIRE).get(Metal.ItemType.INGOT).get().getDefaultInstance())
            .displayItems((parameters, output) -> DragonsteelItems.ITEMS.getEntries().stream()
                .sorted(Comparator.comparing(entry -> entry.getId().toString()))
                .map(entry -> entry.get())
                .forEach(output::accept))
            .build());

    private DragonsteelCreativeTab() {
    }
}
