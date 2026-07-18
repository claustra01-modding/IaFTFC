package net.claustra01.iaftfc.metal;

import java.util.Collections;
import java.util.EnumMap;
import java.util.Map;

import net.dries007.tfc.common.fluids.FluidHolder;
import net.dries007.tfc.common.fluids.MoltenFluid;
import net.dries007.tfc.util.registry.RegistrationHelpers;
import net.minecraft.core.registries.Registries;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.pathfinder.PathType;
import net.neoforged.neoforge.common.SoundActions;
import net.neoforged.neoforge.fluids.BaseFlowingFluid;
import net.neoforged.neoforge.fluids.FluidType;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

public final class DragonsteelFluids {
    public static final DeferredRegister<FluidType> FLUID_TYPES = DeferredRegister.create(NeoForgeRegistries.FLUID_TYPES, "tfc");
    public static final DeferredRegister<Fluid> FLUIDS = DeferredRegister.create(Registries.FLUID, "tfc");
    public static final Map<DragonsteelMetal, FluidHolder<BaseFlowingFluid>> METALS = registerMetalFluids();

    private DragonsteelFluids() {
    }

    private static Map<DragonsteelMetal, FluidHolder<BaseFlowingFluid>> registerMetalFluids() {
        final EnumMap<DragonsteelMetal, FluidHolder<BaseFlowingFluid>> fluids = new EnumMap<>(DragonsteelMetal.class);
        for (DragonsteelMetal metal : DragonsteelMetal.values()) {
            final String source = "metal/" + metal.getSerializedName();
            final String flowing = "metal/flowing_" + metal.getSerializedName();
            fluids.put(metal, RegistrationHelpers.registerFluid(
                FLUID_TYPES,
                FLUIDS,
                source,
                source,
                flowing,
                properties -> { },
                () -> new FluidType(properties().descriptionId("fluid.tfc.metal." + metal.getSerializedName()).rarity(metal.rarity())),
                MoltenFluid.Source::new,
                MoltenFluid.Flowing::new
            ));
        }
        return Collections.unmodifiableMap(fluids);
    }

    private static FluidType.Properties properties() {
        return FluidType.Properties.create()
            .adjacentPathType(PathType.LAVA)
            .sound(SoundActions.BUCKET_FILL, SoundEvents.BUCKET_FILL)
            .sound(SoundActions.BUCKET_EMPTY, SoundEvents.BUCKET_EMPTY_LAVA)
            .lightLevel(15)
            .density(3000)
            .viscosity(6000)
            .temperature(2000)
            .canConvertToSource(false)
            .canDrown(false)
            .canExtinguish(false)
            .canHydrate(false)
            .canPushEntity(false)
            .canSwim(false)
            .supportsBoating(false);
    }
}
