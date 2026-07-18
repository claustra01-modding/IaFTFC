package net.claustra01.iaftfc.dragonarmor;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.Collections;
import java.util.EnumMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import net.claustra01.iaftfc.IaFTFC;
import net.minecraft.world.item.Item;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * Registers additional armor as real Ice and Fire dragon armor items without
 * making IaF internals part of IaFTFC's compile-time API.
 */
public final class DragonArmorItems {
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(IaFTFC.MOD_ID);
    public static final Map<DragonArmorMetal, Map<DragonArmorPart, DeferredItem<Item>>> ARMOR = registerArmor();

    private DragonArmorItems() {
    }

    private static Map<DragonArmorMetal, Map<DragonArmorPart, DeferredItem<Item>>> registerArmor() {
        final EnumMap<DragonArmorMetal, Map<DragonArmorPart, DeferredItem<Item>>> all = new EnumMap<>(DragonArmorMetal.class);
        for (DragonArmorMetal metal : DragonArmorMetal.values()) {
            final EnumMap<DragonArmorPart, DeferredItem<Item>> parts = new EnumMap<>(DragonArmorPart.class);
            for (DragonArmorPart part : DragonArmorPart.values()) {
                final String id = "dragonarmor_" + metal.serializedName() + "_" + part.serializedName();
                parts.put(part, ITEMS.register(id, () -> IafDragonArmorFactory.create(metal, part)));
            }
            all.put(metal, Collections.unmodifiableMap(parts));
        }
        return Collections.unmodifiableMap(all);
    }

    private static final class IafDragonArmorFactory {
        private static final String MATERIAL_CLASS = "com.iafenvoy.iceandfire.data.DragonArmorMaterial";
        private static final String PART_CLASS = "com.iafenvoy.iceandfire.data.DragonArmorPart";
        private static final String ITEM_CLASS = "com.iafenvoy.iceandfire.item.DragonArmorItem";

        private static final Map<DragonArmorMetal, Object> MATERIALS = new ConcurrentHashMap<>();
        private static final Constructor<?> MATERIAL_CONSTRUCTOR;
        private static final Constructor<?> ITEM_CONSTRUCTOR;
        private static final Class<? extends Enum> PART_ENUM;

        static {
            try {
                final Class<?> materialClass = Class.forName(MATERIAL_CLASS);
                final Class<?> partClass = Class.forName(PART_CLASS);
                final Class<?> itemClass = Class.forName(ITEM_CLASS);
                MATERIAL_CONSTRUCTOR = materialClass.getConstructor(String.class, double.class, boolean.class, boolean.class);
                ITEM_CONSTRUCTOR = itemClass.getConstructor(materialClass, partClass);
                PART_ENUM = partClass.asSubclass(Enum.class);
            } catch (ReflectiveOperationException exception) {
                throw new ExceptionInInitializerError(exception);
            }
        }

        private static Item create(DragonArmorMetal metal, DragonArmorPart part) {
            try {
                final Object material = MATERIALS.computeIfAbsent(metal, IafDragonArmorFactory::createMaterial);
                @SuppressWarnings({"rawtypes", "unchecked"})
                final Object iafPart = Enum.valueOf((Class) PART_ENUM, part.name());
                return (Item) ITEM_CONSTRUCTOR.newInstance(material, iafPart);
            } catch (InstantiationException | IllegalAccessException | InvocationTargetException exception) {
                throw new IllegalStateException("Could not construct Ice and Fire dragon armor", exception);
            }
        }

        private static Object createMaterial(DragonArmorMetal metal) {
            try {
                return MATERIAL_CONSTRUCTOR.newInstance(metal.serializedName(), metal.protection(), false, false);
            } catch (InstantiationException | IllegalAccessException | InvocationTargetException exception) {
                throw new IllegalStateException("Could not construct Ice and Fire dragon armor material " + metal.serializedName(), exception);
            }
        }
    }
}
