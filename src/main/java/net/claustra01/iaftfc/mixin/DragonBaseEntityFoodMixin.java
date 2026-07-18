package net.claustra01.iaftfc.mixin;

import net.dries007.tfc.common.component.food.FoodCapability;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

@Mixin(targets = "com.iafenvoy.iceandfire.entity.DragonBaseEntity", remap = false)
public abstract class DragonBaseEntityFoodMixin {
    @ModifyArg(
        method = "mobInteract",
        at = @At(
            value = "INVOKE",
            target = "Lcom/iafenvoy/uranus/object/item/FoodUtils;getFoodPoints(Lnet/minecraft/world/item/ItemStack;ZZ)I"
        ),
        index = 0,
        require = 1,
        remap = false
    )
    private ItemStack iaftfc$rejectRottenHandFood(ItemStack stack) {
        return FoodCapability.isRotten(stack) ? ItemStack.EMPTY : stack;
    }
}
