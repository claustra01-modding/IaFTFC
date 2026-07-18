#!/usr/bin/env python3
"""Regenerate TFC-compatible IaF CE dragon chest loot tables."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZipFile


DRAGONS = ("fire", "ice", "lightning")
TABLE_KINDS = ("dragon_roost", "dragon_female_cave", "dragon_male_cave")
ATTRIBUTE_METALS = {"fire": "gold", "ice": "silver", "lightning": "copper"}
ATTRIBUTE_GEMS = {"fire": "ruby", "ice": "sapphire", "lightning": "topaz"}
ATTRIBUTE_GEM_SOURCES = {
    "minecraft:emerald",
    "iceandfire:sapphire_gem",
    "minecraft:amethyst_shard",
}
ATTRIBUTE_INGOT_SOURCES = {
    "minecraft:gold_ingot",
    "iceandfire:silver_ingot",
    "minecraft:copper_ingot",
}
ATTRIBUTE_NUGGET_SOURCES = {
    "minecraft:gold_nugget",
    "iceandfire:silver_nugget",
    "iceandfire:copper_nugget",
}
COMMON_EQUIPMENT_PREFIXES = (
    "minecraft:iron_",
    "iceandfire:silver_",
    "iceandfire:armor_silver_metal_",
    "iceandfire:copper_",
    "iceandfire:armor_copper_metal_",
)
RARE_EQUIPMENT_PREFIX = "minecraft:diamond_"
EQUIPMENT_SUFFIXES = ("sword", "helmet", "chestplate", "leggings", "boots")


def write_json(root: Path, relative: str, value: object) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def set_uniform_count(entry: dict, minimum: int, maximum: int) -> None:
    functions = entry.setdefault("functions", [])
    set_count = next((fn for fn in functions if fn.get("function") == "minecraft:set_count"), None)
    if set_count is None:
        set_count = {"function": "minecraft:set_count"}
        functions.insert(0, set_count)
    set_count["count"] = {
        "type": "minecraft:uniform",
        "min": minimum,
        "max": maximum,
    }


def item_entry(entry: dict, item: str) -> None:
    entry["type"] = "minecraft:item"
    entry["name"] = item
    entry.pop("expand", None)
    entry.pop("value", None)


def shared_equipment_entry(entry: dict, rarity: str) -> None:
    entry["type"] = "minecraft:loot_table"
    entry["value"] = f"iaftfc:shared/equipment_{rarity}"
    entry.pop("name", None)
    entry.pop("expand", None)


def is_equipment(item: str, prefixes: tuple[str, ...]) -> bool:
    return item.endswith(EQUIPMENT_SUFFIXES) and item.startswith(prefixes)


def transform_entry(entry: dict, dragon: str, male: bool) -> None:
    item = entry.get("name")
    if not isinstance(item, str) or entry.get("type") not in ("item", "minecraft:item"):
        return

    if item == "minecraft:diamond":
        item_entry(entry, "tfc:gem/diamond")
        return
    if item in ATTRIBUTE_GEM_SOURCES:
        item_entry(entry, f"tfc:gem/{ATTRIBUTE_GEMS[dragon]}")
        return
    if item == "minecraft:iron_ingot":
        item_entry(entry, "tfc:metal/ingot/wrought_iron")
        set_uniform_count(entry, 2 if male else 1, 6 if male else 4)
        return
    if item in ATTRIBUTE_INGOT_SOURCES:
        item_entry(entry, f"tfc:metal/ingot/{ATTRIBUTE_METALS[dragon]}")
        set_uniform_count(entry, 2 if male else 1, 6 if male else 4)
        return
    if item in ATTRIBUTE_NUGGET_SOURCES:
        item_entry(entry, f"tfc:powder/native_{ATTRIBUTE_METALS[dragon]}")
        set_uniform_count(entry, 6 if male else 4, 16 if male else 12)
        return
    if is_equipment(item, (RARE_EQUIPMENT_PREFIX,)):
        shared_equipment_entry(entry, "rare")
        return
    if is_equipment(item, COMMON_EQUIPMENT_PREFIXES):
        shared_equipment_entry(entry, "common")


def write_supporting_data(root: Path) -> None:
    equipment_forms = ("sword", "helmet", "chestplate", "greaves", "boots")
    common_metals = ("bronze", "bismuth_bronze", "wrought_iron")
    common_equipment = [
        f"tfc:metal/{form}/{metal}"
        for metal in common_metals
        for form in equipment_forms
    ]
    rare_equipment = [f"tfc:metal/{form}/steel" for form in equipment_forms]

    generated_tag_root = root / "data/iaftfc/tags/item/loot"
    if generated_tag_root.exists():
        for path in sorted(generated_tag_root.rglob("*"), reverse=True):
            path.unlink() if path.is_file() else path.rmdir()
        generated_tag_root.rmdir()

    for rarity, equipment in (("common", common_equipment), ("rare", rare_equipment)):
        write_json(root, f"data/iaftfc/loot_table/shared/equipment_{rarity}.json", {
            "type": "minecraft:chest",
            "pools": [{
                "rolls": 1,
                "entries": [
                    {"type": "minecraft:item", "name": item}
                    for item in equipment
                ],
            }],
        })


def generate(root: Path, iaf_jar: Path) -> None:
    write_supporting_data(root)
    with ZipFile(iaf_jar) as archive:
        for dragon in DRAGONS:
            for kind in TABLE_KINDS:
                table_name = f"{dragon}_{kind}"
                source = f"data/iceandfire/loot_table/chest/{table_name}.json"
                table = json.loads(archive.read(source))
                male = kind == "dragon_male_cave"
                for pool in table.get("pools", []):
                    for entry in pool.get("entries", []):
                        transform_entry(entry, dragon, male)
                write_json(root, source, table)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("iaf_jar", type=Path)
    parser.add_argument("--root", type=Path, default=Path("src/main/resources"))
    args = parser.parse_args()
    generate(args.root, args.iaf_jar)


if __name__ == "__main__":
    main()
