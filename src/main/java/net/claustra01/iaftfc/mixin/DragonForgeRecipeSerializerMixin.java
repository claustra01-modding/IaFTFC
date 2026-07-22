package net.claustra01.iaftfc.mixin;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.function.Function;
import net.claustra01.iaftfc.metal.DragonForgeHeatRecipe;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(targets = "com.iafenvoy.iceandfire.recipe.DragonForgeRecipe$Serializer", remap = false)
public abstract class DragonForgeRecipeSerializerMixin {
    private static final String OUTPUT_TEMPERATURE = "output_temperature";

    @Inject(method = "codec", at = @At("RETURN"), cancellable = true, require = 1, remap = false)
    private void iaftfc$addOutputTemperatureCodec(CallbackInfoReturnable<MapCodec<?>> callback) {
        @SuppressWarnings("unchecked")
        final MapCodec<Object> original = (MapCodec<Object>) callback.getReturnValue();
        final MapCodec<Object> wrapped = RecordCodecBuilder.mapCodec(instance -> instance.group(
            original.forGetter(Function.identity()),
            Codec.floatRange(0.0F, Float.MAX_VALUE)
                .optionalFieldOf(OUTPUT_TEMPERATURE, 0.0F)
                .forGetter(recipe -> ((DragonForgeHeatRecipe) recipe).iaftfc$getOutputTemperature())
        ).apply(instance, (recipe, temperature) -> {
            ((DragonForgeHeatRecipe) recipe).iaftfc$setOutputTemperature(temperature);
            return recipe;
        }));
        callback.setReturnValue(wrapped);
    }

    @Inject(method = "streamCodec", at = @At("RETURN"), cancellable = true, require = 1, remap = false)
    private void iaftfc$addOutputTemperatureStreamCodec(
        CallbackInfoReturnable<StreamCodec<RegistryFriendlyByteBuf, ?>> callback
    ) {
        @SuppressWarnings("unchecked")
        final StreamCodec<RegistryFriendlyByteBuf, Object> original =
            (StreamCodec<RegistryFriendlyByteBuf, Object>) callback.getReturnValue();
        callback.setReturnValue(new StreamCodec<>() {
            @Override
            public Object decode(RegistryFriendlyByteBuf buffer) {
                final Object recipe = original.decode(buffer);
                ((DragonForgeHeatRecipe) recipe).iaftfc$setOutputTemperature(buffer.readFloat());
                return recipe;
            }

            @Override
            public void encode(RegistryFriendlyByteBuf buffer, Object recipe) {
                original.encode(buffer, recipe);
                buffer.writeFloat(((DragonForgeHeatRecipe) recipe).iaftfc$getOutputTemperature());
            }
        });
    }
}
