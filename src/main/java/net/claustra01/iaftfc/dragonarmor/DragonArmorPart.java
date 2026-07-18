package net.claustra01.iaftfc.dragonarmor;

public enum DragonArmorPart {
    HEAD,
    NECK,
    BODY,
    TAIL;

    public String serializedName() {
        return name().toLowerCase(java.util.Locale.ROOT);
    }
}
