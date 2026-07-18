package net.claustra01.iaftfc.dragonbone;

import java.util.Collections;
import java.util.EnumMap;
import java.util.Map;

import net.claustra01.iaftfc.IaFTFC;
import net.minecraft.world.item.Item;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class DragonboneItems {
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(IaFTFC.MOD_ID);
    public static final Map<DragonboneToolPart, DeferredItem<Item>> TOOL_PARTS = registerToolParts();

    private DragonboneItems() {
    }

    private static Map<DragonboneToolPart, DeferredItem<Item>> registerToolParts() {
        final EnumMap<DragonboneToolPart, DeferredItem<Item>> parts = new EnumMap<>(DragonboneToolPart.class);
        for (DragonboneToolPart part : DragonboneToolPart.values()) {
            parts.put(part, ITEMS.registerSimpleItem("dragonbone/" + part.serializedName()));
        }
        return Collections.unmodifiableMap(parts);
    }
}
