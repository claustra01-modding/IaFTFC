#!/usr/bin/env python3
"""Regenerate TFC item size definitions for Ice and Fire CE items."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile


@dataclass(frozen=True)
class Category:
    size: str
    weight: str
    tfc_reference: str | None = None


# References are read from the TFC JAR. The four fallback values come directly
# from TFC 4.2.5 ItemSizeManager; the three user-approved values are intentional
# IaFTFC overrides rather than inferred analogues.
CATEGORIES = {
    "default": Category("very_small", "very_light"),
    "blocks": Category("small", "light"),
    "armor": Category("large", "very_heavy"),
    "tools": Category("very_large", "very_heavy", "tools"),
    "foods": Category("small", "light", "foods"),
    "plants": Category("tiny", "very_light", "plants"),
    "stairs": Category("small", "light", "stairs"),
    "slabs": Category("small", "very_light", "slabs"),
    "logs": Category("very_large", "medium", "logs"),
    "chests": Category("large", "light", "chests"),
    "ingots": Category("large", "medium", "ingots"),
    "ores": Category("small", "medium", "ores"),
    "bottles": Category("normal", "medium", "glass_bottles"),
    "small_tools": Category("large", "medium", "small_tools"),
    "rods": Category("normal", "light", "rods"),
    "sheets": Category("large", "medium", "sheets"),
    "cloth": Category("small", "light", "wool_cloth"),
    "small_light": Category("small", "light", "bowls"),
    "large_vessels": Category("huge", "heavy", "large_vessels"),
    "empty_jars": Category("normal", "medium", "empty_jars"),
    "filled_jars": Category("normal", "heavy", "filled_jars"),
    "furniture": Category("large", "light", "scribing_tables"),
    "dragon_bones": Category("very_large", "medium", "logs"),
    "chains": Category("normal", "heavy", "vessels"),
    "dragon_eggs": Category("very_large", "very_heavy"),
    "dragon_skulls": Category("huge", "very_heavy"),
    # Player-worn armor follows TFC's armor fallback. This is distinct from
    # dragonarmor_* equipment worn by dragons.
    "dragonsteel_armor": Category("large", "very_heavy"),
    "dragon_armor": Category("very_large", "very_heavy"),
}

FOODS = {
    "ambrosia",
    "cannoli",
    "cooked_rice_with_fire_dragon_meat",
    "cooked_rice_with_ice_dragon_meat",
    "cooked_rice_with_lightning_dragon_meat",
    "fire_dragon_flesh",
    "ghost_cream",
    "ice_dragon_flesh",
    "lightning_dragon_flesh",
    "pixie_dust",
    "pixie_dust_milky_tea",
}

SMALL_LIGHT_MATERIAL_PATTERNS = (
    "_feather",
    "_flesh",
    "_heart",
    "_meal",
    "_stew",
    "_wings",
    "chitin_",
)
ROD_MATERIAL_PATTERNS = ("_fang", "_fin", "_talon", "_tounge", "_tusk")
TOOL_SUFFIXES = (
    "_axe",
    "_bow",
    "_dagger",
    "_gauntlet_red",
    "_gauntlet_white",
    "_gauntlet_yellow",
    "_hoe",
    "_macuahuitl",
    "_pickaxe",
    "_shovel",
    "_slapper",
    "_spear",
    "_sword",
    "_trident",
)
SMALL_TOOL_TOKENS = ("_flute", "_scepter", "_seeker", "_staff", "_wand")


def read_json(archive: ZipFile, name: str) -> dict:
    try:
        return json.loads(archive.read(name))
    except KeyError as error:
        raise ValueError(f"Required JAR resource does not exist: {name}") from error


def write_json(root: Path, relative: str, value: object) -> None:
    destination = root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def model_ids(archive: ZipFile) -> set[str]:
    prefix = "assets/iceandfire/models/item/"
    return {
        entry.removeprefix(prefix).removesuffix(".json")
        for entry in archive.namelist()
        if entry.startswith(prefix) and entry.endswith(".json") and "/" not in entry.removeprefix(prefix)
    }


def block_ids(archive: ZipFile) -> set[str]:
    prefix = "assets/iceandfire/blockstates/"
    return {
        entry.removeprefix(prefix).removesuffix(".json")
        for entry in archive.namelist()
        if entry.startswith(prefix) and entry.endswith(".json") and "/" not in entry.removeprefix(prefix)
    }


def is_player_armor(name: str) -> bool:
    armor_part = name.endswith(("_helmet", "_chestplate", "_leggings", "_boots"))
    return armor_part or name in {"blindfold", "earplugs"}


def classify_block(name: str) -> str:
    if name.endswith("stairs"):
        return "stairs"
    if name.endswith("slab"):
        return "slabs"
    if name.endswith("log"):
        return "logs"
    if name.endswith(("leaves", "sapling", "lily")):
        return "plants"
    if name == "ghost_chest":
        return "chests"
    if name == "lectern" or name.startswith("podium_"):
        return "furniture"
    if name == "pixie_jar_empty":
        return "empty_jars"
    if name.startswith("pixie_jar_"):
        return "filled_jars"
    return "blocks"


def classify(name: str, blocks: set[str]) -> str:
    if name in blocks:
        return classify_block(name)
    if name.startswith("dragonegg_"):
        return "dragon_eggs"
    if name.startswith("dragon_skull_"):
        return "dragon_skulls"
    if re.fullmatch(r"dragonsteel_(fire|ice|lightning)_(helmet|chestplate|leggings|boots)", name):
        return "dragonsteel_armor"
    if name.startswith("dragonarmor_"):
        return "dragon_armor"
    if is_player_armor(name) or name.endswith("_hippogryph_armor"):
        return "armor"
    if name in FOODS:
        return "foods"
    if name.endswith("_ingot"):
        return "ingots"
    if name == "raw_silver":
        return "ores"
    if name.endswith(("_blood", "_cream", "_milky_tea")):
        return "bottles"
    if name.endswith("_arrow"):
        return "rods"
    if name == "dragonbone":
        return "dragon_bones"
    if name in {"witherbone", "dragon_horn", "dragon_stick"} or name.endswith(ROD_MATERIAL_PATTERNS):
        return "rods"
    if name.startswith("dragonscales_") or name.startswith("sea_serpent_scales_") or name == "shiny_scales":
        return "sheets"
    if (
        name.startswith(("troll_leather_", "stymphalian_bird_feather"))
        or any(token in name for token in SMALL_LIGHT_MATERIAL_PATTERNS)
    ):
        return "cloth" if "leather" in name or "feather" in name else "small_light"
    if (
        name.startswith(("dragonbone_bow_pulling_", "dragonbone_sword_"))
        or name.endswith("_throwing")
        or name == "tide_trident_inventory"
    ):
        return "tools"
    if name.endswith(TOOL_SUFFIXES) or name.startswith("troll_weapon"):
        return "tools"
    if any(token in name for token in SMALL_TOOL_TOKENS):
        return "small_tools"
    if name == "stymphalian_feather_bundle":
        return "small_tools"
    if name in {"chain", "chain_link", "chain_sticky"}:
        return "chains"
    if name.endswith("_skull") or name in {"stone_statue", "gorgon_head", "cyclops_eye"}:
        return "large_vessels"
    if name.startswith("banner_pattern_"):
        return "default"
    if name.endswith(("_egg", "_egg_giant")) or name.startswith("spawn_egg_"):
        return "small_light"
    return "default"


def validate_tfc_references(tfc_jar: Path) -> None:
    with ZipFile(tfc_jar) as archive:
        for name, category in CATEGORIES.items():
            if category.tfc_reference is None:
                continue
            reference = read_json(archive, f"data/tfc/tfc/item_size/{category.tfc_reference}.json")
            actual = (reference["size"], reference["weight"])
            expected = (category.size, category.weight)
            if actual != expected:
                raise ValueError(f"TFC reference changed for {name}: expected {expected}, found {actual}")


def generate(root: Path, iaf_jar: Path, tfc_jar: Path) -> None:
    validate_tfc_references(tfc_jar)
    with ZipFile(iaf_jar) as archive:
        models = model_ids(archive)
        blocks = block_ids(archive)
    if not models:
        raise ValueError("IaF CE contains no item models")

    categorized: dict[str, list[str]] = {name: [] for name in CATEGORIES}
    for name in sorted(models):
        categorized[classify(name, blocks)].append(name)
    assigned = {name for values in categorized.values() for name in values}
    if assigned != models or sum(map(len, categorized.values())) != len(models):
        raise ValueError("Every IaF item model must be assigned to exactly one size category")

    size_root = root / "data/iaftfc/tfc/item_size"
    tag_root = root / "data/iaftfc/tags/item/item_size"
    for directory in (size_root, tag_root):
        directory.mkdir(parents=True, exist_ok=True)
        for stale in directory.glob("iaf_*.json"):
            stale.unlink()

    for name, category in CATEGORIES.items():
        values = categorized[name]
        if not values:
            continue
        tag_path = f"item_size/iaf_{name}"
        write_json(
            root,
            f"data/iaftfc/tags/item/{tag_path}.json",
            {
                "replace": False,
                "values": [
                    {"id": f"iceandfire:{item}", "required": False}
                    for item in values
                ],
            },
        )
        write_json(
            root,
            f"data/iaftfc/tfc/item_size/iaf_{name}.json",
            {
                "ingredient": {"tag": f"iaftfc:{tag_path}"},
                "size": category.size,
                "weight": category.weight,
            },
        )

    print(f"Generated item size definitions for {len(models)} IaF item models in {sum(bool(v) for v in categorized.values())} categories")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("iaf_jar", type=Path)
    parser.add_argument("tfc_jar", type=Path)
    parser.add_argument("--root", type=Path, default=Path("src/main/resources"))
    args = parser.parse_args()
    generate(args.root, args.iaf_jar, args.tfc_jar)


if __name__ == "__main__":
    main()
