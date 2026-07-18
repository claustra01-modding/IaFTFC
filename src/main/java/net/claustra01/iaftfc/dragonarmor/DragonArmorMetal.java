package net.claustra01.iaftfc.dragonarmor;

public enum DragonArmorMetal {
    STEEL("steel", 3.5),
    BLACK_STEEL("black_steel", 5.5),
    RED_STEEL("red_steel", 7.5),
    BLUE_STEEL("blue_steel", 7.5);

    private final String serializedName;
    private final double protection;

    DragonArmorMetal(String serializedName, double protection) {
        this.serializedName = serializedName;
        this.protection = protection;
    }

    public String serializedName() {
        return serializedName;
    }

    public double protection() {
        return protection;
    }
}
