package net.claustra01.iaftfc.mixin;

import net.dries007.tfc.common.component.food.FoodCapability;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyArg;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(targets = "com.iafenvoy.iceandfire.entity.ai.DragonAITargetItemsGoal", remap = false)
public abstract class DragonAITargetItemsGoalFoodMixin {
    @Shadow(remap = false)
    protected ItemEntity targetEntity;

    @ModifyArg(
        method = "lambda$new$0",
        at = @At(
            value = "INVOKE",
            target = "Lcom/iafenvoy/uranus/object/item/FoodUtils;getFoodPoints(Lnet/minecraft/world/item/ItemStack;ZZ)I"
        ),
        index = 0,
        require = 1,
        remap = false
    )
    private ItemStack iaftfc$rejectRottenTargetFood(ItemStack stack) {
        return FoodCapability.isRotten(stack) ? ItemStack.EMPTY : stack;
    }

    @Inject(method = "canContinueToUse", at = @At("HEAD"), cancellable = true, require = 1, remap = false)
    private void iaftfc$stopTargetingRottenFood(CallbackInfoReturnable<Boolean> callback) {
        if (iaftfc$isTargetRotten()) {
            callback.setReturnValue(false);
        }
    }

    @Inject(method = "tick", at = @At("HEAD"), cancellable = true, require = 1, remap = false)
    private void iaftfc$neverConsumeRottenFood(CallbackInfo callback) {
        if (iaftfc$isTargetRotten()) {
            callback.cancel();
        }
    }

    private boolean iaftfc$isTargetRotten() {
        return targetEntity != null && FoodCapability.isRotten(targetEntity.getItem());
    }
}
