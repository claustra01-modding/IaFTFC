#!/usr/bin/env python3
"""Regenerate TFC physical damage types and resistances for IaF equipment and dragons."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile


DRAGONS = ("fire_dragon", "ice_dragon", "lightning_dragon")
ARMOR_PARTS = ("helmet", "chestplate", "leggings", "boots")
DRAGON_ARMOR_PARTS = ("head", "neck", "body", "tail")
DRAGON_SCALE_COLORS = (
    "amethyst", "black", "blue", "bronze", "copper", "electric",
    "gray", "green", "red", "sapphire", "silver", "white",
)
TIDE_COLORS = ("blue", "bronze", "deepblue", "green", "purple", "red", "teal")


@dataclass(frozen=True)
class Resistance:
    piercing: float
    slashing: float
    crushing: float


REFERENCE_FILES = {
    "leather": "leather_armor",
    "copper": "copper_armor",
    "bronze": "bronze_armor",
    "wrought_iron": "wrought_iron_armor",
    "steel": "steel_armor",
    "black_steel": "black_steel_armor",
    "red_steel": "red_steel_armor",
    "blue_steel": "blue_steel_armor",
}
DRAGONSTEEL = Resistance(75.0, 75.0, 75.0)
DRAGON = Resistance(200.0, 200.0, 200.0)


def read_json(archive: ZipFile, name: str) -> dict:
    try:
        return json.loads(archive.read(name))
    except KeyError as error:
        raise ValueError(f"Required JAR resource does not exist: {name}") from error


def write_json(root: Path, relative: str, value: object) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def model_ids(archive: ZipFile) -> set[str]:
    prefix = "assets/iceandfire/models/item/"
    return {
        name.removeprefix(prefix).removesuffix(".json")
        for name in archive.namelist()
        if name.startswith(prefix) and name.endswith(".json") and "/" not in name.removeprefix(prefix)
    }


def resistance_from_json(value: dict) -> Resistance:
    return Resistance(
        float(value.get("piercing", 0.0)),
        float(value.get("slashing", 0.0)),
        float(value.get("crushing", 0.0)),
    )


def load_references(tfc_jar: Path) -> dict[str, Resistance]:
    with ZipFile(tfc_jar) as archive:
        return {
            name: resistance_from_json(read_json(archive, f"data/tfc/tfc/item_damage_resistance/{path}.json"))
            for name, path in REFERENCE_FILES.items()
        }


def item(name: str, namespace: str = "iceandfire") -> dict:
    return {"item": f"{namespace}:{name}"}


def armor_set(prefix: str, parts: tuple[str, ...] = ARMOR_PARTS) -> list[dict]:
    return [item(f"{prefix}_{part}") for part in parts]


def player_armor_groups() -> dict[str, tuple[Resistance | str, list[dict]]]:
    leather = (
        [item("blindfold"), item("earplugs")]
        + armor_set("sheep")
    )
    robust_hide = (
        [entry for color in ("red", "white", "yellow") for entry in armor_set(f"deathworm_{color}")]
        + [entry for kind in ("forest", "frost", "mountain") for entry in armor_set(f"{kind}_troll_leather")]
    )
    dragon_scale = (
        [entry for color in DRAGON_SCALE_COLORS for entry in armor_set(f"armor_{color}")]
        + [entry for color in TIDE_COLORS for entry in armor_set(f"tide_{color}")]
    )
    dragonsteel = [
        entry
        for element in ("fire", "ice", "lightning")
        for entry in armor_set(f"dragonsteel_{element}")
    ]
    return {
        "leather_like": ("leather", leather),
        "copper_metal": ("copper", armor_set("armor_copper_metal")),
        "silver_metal": ("bronze", armor_set("armor_silver_metal")),
        "robust_hide": ("wrought_iron", robust_hide),
        "dragon_scale": ("black_steel", dragon_scale),
        "dragonsteel": (DRAGONSTEEL, dragonsteel),
        "hippogryph_iron": ("wrought_iron", [item("iron_hippogryph_armor")]),
        "hippogryph_gold": ("bronze", [item("gold_hippogryph_armor")]),
        "hippogryph_diamond": ("steel", [item("diamond_hippogryph_armor")]),
        "hippogryph_netherite": ("black_steel", [item("netherite_hippogryph_armor")]),
    }


def dragon_armor_groups() -> dict[str, tuple[Resistance | str, list[dict]]]:
    groups: dict[str, tuple[Resistance | str, list[dict]]] = {}
    material_tiers = {
        "copper": "copper",
        "gold": "bronze",
        "silver": "bronze",
        "iron": "wrought_iron",
        "diamond": "steel",
        "netherite": "black_steel",
    }
    for material, tier in material_tiers.items():
        groups[f"dragon_armor_{material}"] = (
            tier,
            armor_set(f"dragonarmor_{material}", DRAGON_ARMOR_PARTS),
        )
    for element in ("fire", "ice", "lightning"):
        groups[f"dragon_armor_dragonsteel_{element}"] = (
            DRAGONSTEEL,
            armor_set(f"dragonarmor_dragon_steel_{element}", DRAGON_ARMOR_PARTS),
        )
    return groups


def iaftfc_dragon_armor_groups() -> dict[str, tuple[Resistance | str, list[dict]]]:
    return {
        f"iaftfc_dragon_armor_{metal}": (
            metal,
            [item(f"dragonarmor_{metal}_{part}", "iaftfc") for part in DRAGON_ARMOR_PARTS],
        )
        for metal in ("steel", "black_steel", "red_steel", "blue_steel")
    }


def damage_items(models: set[str]) -> dict[str, list[str]]:
    result = {"slashing": [], "piercing": [], "crushing": []}
    for name in sorted(models):
        if (
            name.endswith(("_axe", "_hoe", "_macuahuitl", "_sword"))
            or name.startswith("dragonbone_sword_")
        ):
            result["slashing"].append(name)
        elif (
            name.endswith(("_bow", "_dagger", "_pickaxe", "_spear", "_trident"))
            or name.startswith("dragonbone_bow_pulling_")
            or name in {"tide_trident_inventory", "tide_trident_throwing"}
        ):
            result["piercing"].append(name)
        elif (
            name.endswith(("_shovel", "_slapper"))
            or "_gauntlet_" in name
            or name.startswith("troll_weapon")
        ):
            result["crushing"].append(name)
    overlap = set(result["slashing"]) & set(result["piercing"])
    overlap |= set(result["slashing"]) & set(result["crushing"])
    overlap |= set(result["piercing"]) & set(result["crushing"])
    if overlap:
        raise ValueError("Items assigned multiple physical damage types: " + ", ".join(sorted(overlap)))
    return result


def resistance_json(entries: list[dict], resistance: Resistance) -> dict:
    return {
        "ingredient": entries,
        "piercing": resistance.piercing,
        "slashing": resistance.slashing,
        "crushing": resistance.crushing,
    }


def generate(root: Path, iaf_jar: Path, tfc_jar: Path) -> None:
    references = load_references(tfc_jar)
    with ZipFile(iaf_jar) as archive:
        models = model_ids(archive)
        resources = set(archive.namelist())

    item_groups = player_armor_groups() | dragon_armor_groups() | iaftfc_dragon_armor_groups()
    all_armor_ids = [entry["item"] for _, entries in item_groups.values() for entry in entries]
    missing_armor = sorted(
        name
        for item_id in all_armor_ids
        if item_id.startswith("iceandfire:")
        for name in [item_id.removeprefix("iceandfire:")]
        if name not in models
    )
    if missing_armor:
        raise ValueError("IaF armor models do not exist: " + ", ".join(missing_armor))
    missing_iaftfc_armor = sorted(
        item_id
        for item_id in all_armor_ids
        if item_id.startswith("iaftfc:")
        and not (root / f"assets/iaftfc/models/item/{item_id.removeprefix('iaftfc:')}.json").is_file()
    )
    if missing_iaftfc_armor:
        raise ValueError("IaFTFC armor models do not exist: " + ", ".join(missing_iaftfc_armor))

    damage = damage_items(models)
    expected_dragonbone = {
        "dragonbone_axe", "dragonbone_bow", "dragonbone_hoe", "dragonbone_pickaxe",
        "dragonbone_shovel", "dragonbone_sword", "dragonbone_sword_fire",
        "dragonbone_sword_ice", "dragonbone_sword_lightning",
    }
    assigned = set().union(*map(set, damage.values()))
    if not expected_dragonbone <= assigned:
        raise ValueError("Dragonbone tools are missing physical damage types")

    for kind, values in damage.items():
        write_json(root, f"data/tfc/tags/item/deals_{kind}_damage.json", {
            "replace": False,
            "values": [{"id": f"iceandfire:{name}", "required": False} for name in values],
        })

    resistance_root = root / "data/iaftfc/tfc/item_damage_resistance"
    resistance_root.mkdir(parents=True, exist_ok=True)
    for stale in resistance_root.glob("iaf_*.json"):
        stale.unlink()
    for name, (tier, entries) in item_groups.items():
        resistance = references[tier] if isinstance(tier, str) else tier
        write_json(root, f"data/iaftfc/tfc/item_damage_resistance/iaf_{name}.json", resistance_json(entries, resistance))

    dragon_ids = [f"iceandfire:{name}" for name in DRAGONS]
    for dragon in DRAGONS:
        if f"data/iceandfire/loot_table/entities/dragon/{dragon}_female.json" not in resources:
            # Entity loot tables are stable registry-backed evidence in the target JAR.
            raise ValueError(f"IaF dragon entity resource does not exist: iceandfire:{dragon}")
    write_json(root, "data/iaftfc/tags/entity_type/dragons.json", {"replace": False, "values": dragon_ids})
    write_json(root, "data/tfc/tags/entity_type/deals_slashing_damage.json", {
        "replace": False,
        "values": ["#iaftfc:dragons"],
    })
    write_json(root, "data/iaftfc/tfc/entity_damage_resistance/dragons.json", {
        "entity": "iaftfc:dragons",
        "piercing": DRAGON.piercing,
        "slashing": DRAGON.slashing,
        "crushing": DRAGON.crushing,
    })

    print(
        f"Generated physical damage for {sum(map(len, damage.values()))} IaF weapon models, "
        f"{len(all_armor_ids)} armor items, and {len(DRAGONS)} dragons"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("iaf_jar", type=Path)
    parser.add_argument("tfc_jar", type=Path)
    parser.add_argument("--root", type=Path, default=Path("src/main/resources"))
    args = parser.parse_args()
    generate(args.root, args.iaf_jar, args.tfc_jar)


if __name__ == "__main__":
    main()
