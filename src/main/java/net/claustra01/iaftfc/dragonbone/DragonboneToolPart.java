package net.claustra01.iaftfc.dragonbone;

public enum DragonboneToolPart {
    AXE_HEAD("axe_head"),
    HOE_HEAD("hoe_head"),
    PICKAXE_HEAD("pickaxe_head"),
    SHOVEL_HEAD("shovel_head"),
    SWORD_BLADE("sword_blade");

    private final String serializedName;

    DragonboneToolPart(String serializedName) {
        this.serializedName = serializedName;
    }

    public String serializedName() {
        return serializedName;
    }
}
