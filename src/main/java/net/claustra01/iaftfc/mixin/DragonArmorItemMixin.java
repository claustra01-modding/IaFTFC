package net.claustra01.iaftfc.mixin;

import net.claustra01.iaftfc.IaFTFC;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(targets = "com.iafenvoy.iceandfire.item.DragonArmorItem", remap = false)
public abstract class DragonArmorItemMixin {
    private static final String[] PART_SUFFIXES = {"_head", "_neck", "_body", "_tail"};

    @Inject(method = "getDescriptionId", at = @At("HEAD"), cancellable = true)
    private void iaftfc$useIaftfcDescriptionId(CallbackInfoReturnable<String> callback) {
        final ResourceLocation id = BuiltInRegistries.ITEM.getKey((Item) (Object) this);
        if (!IaFTFC.MOD_ID.equals(id.getNamespace())) {
            return;
        }
        String path = id.getPath();
        for (String suffix : PART_SUFFIXES) {
            if (path.endsWith(suffix)) {
                path = path.substring(0, path.length() - suffix.length());
                break;
            }
        }
        callback.setReturnValue("item." + IaFTFC.MOD_ID + "." + path);
    }
}
