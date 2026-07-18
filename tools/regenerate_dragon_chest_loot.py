#!/usr/bin/env python3
"""Regenerate IaF CE dragon chest loot as category-preserving TFC loot."""

from __future__ import annotations

import argparse
import copy
import json
import shutil
from pathlib import Path
from zipfile import ZipFile


MOD_ID = "iaftfc"
DRAGONS = ("fire", "ice", "lightning")
TABLE_KINDS = ("dragon_roost", "dragon_female_cave", "dragon_male_cave")
PROFILE_BY_KIND = {
    "dragon_roost": "ordinary",
    "dragon_female_cave": "dangerous",
    "dragon_male_cave": "lategame",
}
EQUIPMENT_METALS = {
    "ordinary": ("copper", "bronze", "bismuth_bronze", "black_bronze"),
    "dangerous": ("wrought_iron",),
    "lategame": ("steel",),
}
INGOT_METALS = {
    "ordinary": ("copper", "bronze", "bismuth_bronze", "black_bronze", "wrought_iron"),
    "dangerous": ("wrought_iron", "steel"),
    "lategame": ("steel", "black_steel"),
}
EQUIPMENT_FAMILIES = {
    "sword": (("sword_blade", "javelin_head", "mace_head"), ("sword", "javelin", "mace")),
    "helmet": (("unfinished_helmet",), ("helmet",)),
    "chestplate": (("unfinished_chestplate",), ("chestplate",)),
    "greaves": (("unfinished_greaves",), ("greaves",)),
    "boots": (("unfinished_boots",), ("boots",)),
}
SOURCE_EQUIPMENT_SUFFIXES = {
    "sword": "sword",
    "helmet": "helmet",
    "chestplate": "chestplate",
    "leggings": "greaves",
    "boots": "boots",
}
SOURCE_EQUIPMENT_PREFIXES = (
    "minecraft:iron_",
    "minecraft:diamond_",
    "iceandfire:silver_",
    "iceandfire:copper_",
    "iceandfire:armor_silver_metal_",
    "iceandfire:armor_copper_metal_",
)
ATTRIBUTE_GEMS = {
    "fire": ("minecraft:emerald", "tfc:gem/ruby"),
    "ice": ("iceandfire:sapphire_gem", "tfc:gem/sapphire"),
    "lightning": ("minecraft:amethyst_shard", "tfc:gem/topaz"),
}
GENERIC_GEMS = {
    "minecraft:diamond",
    "minecraft:emerald",
    "minecraft:amethyst_shard",
    "iceandfire:sapphire_gem",
}
ATTRIBUTE_INGOTS = {
    "fire": ("minecraft:gold_ingot", "tfc:metal/ingot/gold"),
    "ice": ("iceandfire:silver_ingot", "tfc:metal/ingot/silver"),
    "lightning": ("minecraft:copper_ingot", "tfc:metal/ingot/copper"),
}
GENERIC_INGOTS = {
    "minecraft:iron_ingot",
    "minecraft:gold_ingot",
    "minecraft:copper_ingot",
    "iceandfire:silver_ingot",
}
SMALL_ORES = {
    "minecraft:gold_nugget": "tfc:ore/small_native_gold",
    "iceandfire:silver_nugget": "tfc:ore/small_native_silver",
    "iceandfire:copper_nugget": "tfc:ore/small_native_copper",
}
GEMS = ("amethyst", "diamond", "emerald", "lapis_lazuli", "opal", "pyrite", "ruby", "sapphire", "topaz")
COAL_LIKE = ("minecraft:charcoal", "tfc:ore/bituminous_coal", "tfc:ore/lignite", "tfc:ore/graphite")
UTILITY = (
    "tfc:powder/flux",
    "minecraft:glass",
    "minecraft:glass_pane",
    "tfc:kaolin_clay",
    "tfc:powder/wood_ash",
    "tfc:powder/saltpeter",
    "tfc:powder/sylvite",
)


def write_json(root: Path, relative: str, value: object) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def function_name(function: dict) -> str:
    return function.get("function", "").removeprefix("minecraft:")


def item(name: str, weight: int | None = None, functions: list[dict] | None = None) -> dict:
    result: dict = {"type": "minecraft:item", "name": name}
    if weight is not None:
        result["weight"] = weight
    if functions:
        result["functions"] = copy.deepcopy(functions)
    return result


def one_pool(entries: list[dict]) -> dict:
    return {"type": "minecraft:generic", "pools": [{"rolls": 1, "entries": entries}]}


def replace_item(source: dict, name: str) -> dict:
    result = copy.deepcopy(source)
    result["type"] = "minecraft:item"
    result["name"] = name
    result.pop("value", None)
    result.pop("expand", None)
    return result


def table_entry(source: dict, value: str, functions: list[dict] | None = None) -> dict:
    result = {key: copy.deepcopy(child) for key, child in source.items() if key not in {"type", "name", "value", "expand", "functions"}}
    result.update({"type": "minecraft:loot_table", "value": value})
    if functions:
        result["functions"] = copy.deepcopy(functions)
    return result


def equipment_family(name: str) -> str | None:
    if not name.startswith(SOURCE_EQUIPMENT_PREFIXES):
        return None
    for suffix, family in SOURCE_EQUIPMENT_SUFFIXES.items():
        if name.endswith("_" + suffix):
            return family
    return None


def split_equipment_functions(functions: list[dict]) -> tuple[list[dict], list[dict]]:
    parent: list[dict] = []
    completed: list[dict] = []
    for function in functions:
        name = function_name(function)
        if name == "set_damage":
            continue
        if name.startswith("enchant"):
            completed.append(copy.deepcopy(function))
        else:
            parent.append(copy.deepcopy(function))
    return parent, completed


def transform_entry(
    source: dict,
    dragon: str,
    profile: str,
    completion_functions: dict[tuple[str, str], list[dict]],
) -> dict:
    if source.get("type") not in {"item", "minecraft:item"} or not isinstance(source.get("name"), str):
        return copy.deepcopy(source)

    name = source["name"]
    attribute_gem, target_gem = ATTRIBUTE_GEMS[dragon]
    if name == attribute_gem:
        return replace_item(source, target_gem)
    if name in GENERIC_GEMS:
        return table_entry(source, f"{MOD_ID}:shared/gems", source.get("functions"))

    attribute_ingot, target_ingot = ATTRIBUTE_INGOTS[dragon]
    if name == attribute_ingot:
        return replace_item(source, target_ingot)
    if name in GENERIC_INGOTS:
        return table_entry(source, f"{MOD_ID}:shared/ingots/{profile}", source.get("functions"))
    if name in SMALL_ORES:
        return replace_item(source, SMALL_ORES[name])

    family = equipment_family(name)
    if family is not None:
        parent, completed = split_equipment_functions(source.get("functions", []))
        key = (profile, family)
        if completed:
            previous = completion_functions.setdefault(key, completed)
            if previous != completed:
                raise ValueError(f"Conflicting completion functions for {profile}/{family}")
        return table_entry(source, f"{MOD_ID}:shared/equipment/{profile}/{family}", parent)

    if name == "minecraft:obsidian":
        return table_entry(source, f"{MOD_ID}:shared/utility", source.get("functions"))
    return copy.deepcopy(source)


def equipment_table(profile: str, family: str, completion_functions: list[dict] | None) -> dict:
    parts, completed = EQUIPMENT_FAMILIES[family]
    entries: list[dict] = []
    for metal in EQUIPMENT_METALS[profile]:
        entries.extend(item(f"tfc:metal/{form}/{metal}", weight=2) for form in parts)
        entries.extend(item(f"tfc:metal/{form}/{metal}", weight=1, functions=completion_functions) for form in completed)
    return one_pool(entries)


def shared_tables(completion_functions: dict[tuple[str, str], list[dict]]) -> dict[str, dict]:
    result = {
        "shared/gems": one_pool([item(f"tfc:gem/{gem}") for gem in GEMS]),
        "shared/coal_like": one_pool([item(name) for name in COAL_LIKE]),
        "shared/utility": one_pool([item(name) for name in UTILITY]),
    }
    for profile, metals in INGOT_METALS.items():
        result[f"shared/ingots/{profile}"] = one_pool([item(f"tfc:metal/ingot/{metal}") for metal in metals])
        for family in EQUIPMENT_FAMILIES:
            result[f"shared/equipment/{profile}/{family}"] = equipment_table(
                profile,
                family,
                completion_functions.get((profile, family)),
            )
    return result


def set_count_functions(entry: dict) -> list[dict]:
    return [function for function in entry.get("functions", []) if function_name(function) == "set_count"]


def validate_entry_translation(source: dict, generated: dict, dragon: str, profile: str, location: str) -> None:
    if source.get("type") not in {"item", "minecraft:item"} or not isinstance(source.get("name"), str):
        if source != generated:
            raise ValueError(f"{location}: unsupported entry changed")
        return
    name = source["name"]
    attribute_gem, target_gem = ATTRIBUTE_GEMS[dragon]
    attribute_ingot, target_ingot = ATTRIBUTE_INGOTS[dragon]
    family = equipment_family(name)
    if name == attribute_gem:
        expected_type, expected_target = "minecraft:item", target_gem
    elif name in GENERIC_GEMS:
        expected_type, expected_target = "minecraft:loot_table", f"{MOD_ID}:shared/gems"
    elif name == attribute_ingot:
        expected_type, expected_target = "minecraft:item", target_ingot
    elif name in GENERIC_INGOTS:
        expected_type, expected_target = "minecraft:loot_table", f"{MOD_ID}:shared/ingots/{profile}"
    elif name in SMALL_ORES:
        expected_type, expected_target = "minecraft:item", SMALL_ORES[name]
        if "/small_" not in expected_target:
            raise ValueError(f"{location}: nugget does not map to a small ore")
    elif family is not None:
        expected_type, expected_target = "minecraft:loot_table", f"{MOD_ID}:shared/equipment/{profile}/{family}"
    elif name == "minecraft:obsidian":
        expected_type, expected_target = "minecraft:loot_table", f"{MOD_ID}:shared/utility"
    else:
        if source != generated:
            raise ValueError(f"{location}: original entry {name} changed unexpectedly")
        return
    target_key = "name" if expected_type == "minecraft:item" else "value"
    if generated.get("type") != expected_type or generated.get(target_key) != expected_target:
        raise ValueError(f"{location}: invalid translation for {name}")
    ignored = {"type", "name", "value", "expand", "functions"}
    source_metadata = {key: value for key, value in source.items() if key not in ignored}
    generated_metadata = {key: value for key, value in generated.items() if key not in ignored}
    if source_metadata != generated_metadata:
        raise ValueError(f"{location}: conditions or entry metadata changed")


def validate_main_table(source: dict, generated: dict, table_name: str, dragon: str, profile: str) -> None:
    source_pools = source.get("pools", [])
    generated_pools = generated.get("pools", [])
    if len(source_pools) != len(generated_pools):
        raise ValueError(f"{table_name}: pool count changed")
    for pool_index, (source_pool, generated_pool) in enumerate(zip(source_pools, generated_pools)):
        for key in ("rolls", "bonus_rolls"):
            if source_pool.get(key) != generated_pool.get(key):
                raise ValueError(f"{table_name} pool {pool_index}: {key} changed")
        source_entries = source_pool.get("entries", [])
        generated_entries = generated_pool.get("entries", [])
        if len(source_entries) != len(generated_entries):
            raise ValueError(f"{table_name} pool {pool_index}: entry count changed")
        for entry_index, (source_entry, generated_entry) in enumerate(zip(source_entries, generated_entries)):
            if source_entry.get("weight", 1) != generated_entry.get("weight", 1):
                raise ValueError(f"{table_name} entry {entry_index}: weight changed")
            if set_count_functions(source_entry) != set_count_functions(generated_entry):
                raise ValueError(f"{table_name} entry {entry_index}: count provider changed")
            validate_entry_translation(
                source_entry,
                generated_entry,
                dragon,
                profile,
                f"{table_name} pool {pool_index} entry {entry_index}",
            )


def walk(value):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def validate_shared_tables(
    tables: dict[str, dict],
    completion_functions: dict[tuple[str, str], list[dict]],
) -> None:
    for profile, metals in INGOT_METALS.items():
        entries = tables[f"shared/ingots/{profile}"]["pools"][0]["entries"]
        actual = tuple(entry["name"].rsplit("/", 1)[1] for entry in entries)
        if actual != metals or any("/ingot/" not in entry["name"] for entry in entries):
            raise ValueError(f"Invalid {profile} ingot table")

    for profile, metals in EQUIPMENT_METALS.items():
        for family, (part_forms, completed_forms) in EQUIPMENT_FAMILIES.items():
            entries = tables[f"shared/equipment/{profile}/{family}"]["pools"][0]["entries"]
            part_entries = [entry for entry in entries if any(f"/{form}/" in entry["name"] for form in part_forms)]
            completed_entries = [entry for entry in entries if any(f"/{form}/" in entry["name"] for form in completed_forms)]
            if not part_entries or not completed_entries:
                raise ValueError(f"Missing equipment branch in {profile}/{family}")
            if len({entry.get("weight", 1) for entry in part_entries}) != 1:
                raise ValueError(f"Unequal part weights in {profile}/{family}")
            if len({entry.get("weight", 1) for entry in completed_entries}) != 1:
                raise ValueError(f"Unequal completed weights in {profile}/{family}")
            part_weight = sum(entry.get("weight", 1) for entry in part_entries)
            completed_weight = sum(entry.get("weight", 1) for entry in completed_entries)
            if part_weight != completed_weight * 2:
                raise ValueError(f"Equipment branch ratio is not 2:1 in {profile}/{family}")
            expected_metals = set(metals)
            actual_metals = {entry["name"].rsplit("/", 1)[1] for entry in entries}
            if actual_metals != expected_metals:
                raise ValueError(f"Invalid equipment metals in {profile}/{family}")
            if any(any(function_name(fn).startswith("enchant") for fn in entry.get("functions", [])) for entry in part_entries):
                raise ValueError(f"Enchantment found on unfinished equipment in {profile}/{family}")
            expected_functions = completion_functions.get((profile, family), [])
            if any(entry.get("functions", []) != expected_functions for entry in completed_entries):
                raise ValueError(f"Completion functions were not preserved in {profile}/{family}")

    all_items = [node["name"] for table in tables.values() for node in walk(table) if isinstance(node, dict) and node.get("type") == "minecraft:item"]
    if any("red_steel" in name or "blue_steel" in name for name in all_items):
        raise ValueError("Red or Blue Steel found in generic loot")
    if any("black_steel" in name for path, table in tables.items() if "/equipment/" in path for node in walk(table) if isinstance(node, dict) for name in [node.get("name", "")]):
        raise ValueError("Black Steel equipment found")
    if "tfc:powder/graphite" in all_items:
        raise ValueError("Graphite powder found in loot")
    for path, table in tables.items():
        if path == "shared/coal_like":
            continue
        if any(node.get("name") == "tfc:ore/graphite" for node in walk(table) if isinstance(node, dict)):
            raise ValueError(f"Graphite found outside coal_like: {path}")
    for path, table in tables.items():
        for node in walk(table):
            if isinstance(node, dict) and len(set_count_functions(node)) > 1:
                raise ValueError(f"Multiple set_count functions in {path}")


def validate_tfc_item_ids(root: Path, tfc_jar: Path) -> None:
    ids: set[str] = set()
    for path in (root / f"data/{MOD_ID}/loot_table/shared").rglob("*.json"):
        table = json.loads(path.read_text(encoding="utf-8"))
        ids.update(
            node["name"].removeprefix("tfc:")
            for node in walk(table)
            if isinstance(node, dict) and node.get("type") == "minecraft:item" and node.get("name", "").startswith("tfc:")
        )
    with ZipFile(tfc_jar) as archive:
        resources = set(archive.namelist())
    missing = [item_id for item_id in sorted(ids) if f"assets/tfc/models/item/{item_id}.json" not in resources]
    if missing:
        raise ValueError("TFC item IDs do not exist: " + ", ".join(f"tfc:{item_id}" for item_id in missing))


def generate(root: Path, iaf_jar: Path, tfc_jar: Path) -> None:
    completion_functions: dict[tuple[str, str], list[dict]] = {}
    generated_tables: list[tuple[str, dict, dict]] = []
    with ZipFile(iaf_jar) as archive:
        for dragon in DRAGONS:
            for kind in TABLE_KINDS:
                table_name = f"{dragon}_{kind}"
                source_path = f"data/iceandfire/loot_table/chest/{table_name}.json"
                source = json.loads(archive.read(source_path))
                generated = copy.deepcopy(source)
                profile = PROFILE_BY_KIND[kind]
                for pool in generated.get("pools", []):
                    pool["entries"] = [
                        transform_entry(entry, dragon, profile, completion_functions)
                        for entry in pool.get("entries", [])
                    ]
                validate_main_table(source, generated, table_name, dragon, profile)
                generated_tables.append((source_path, source, generated))

    tables = shared_tables(completion_functions)
    validate_shared_tables(tables, completion_functions)

    shared_root = root / f"data/{MOD_ID}/loot_table/shared"
    if shared_root.exists():
        shutil.rmtree(shared_root)
    for path, table in tables.items():
        write_json(root, f"data/{MOD_ID}/loot_table/{path}.json", table)
    for source_path, _, generated in generated_tables:
        write_json(root, source_path, generated)
    validate_tfc_item_ids(root, tfc_jar)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("iaf_jar", type=Path)
    parser.add_argument("--tfc-jar", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path("src/main/resources"))
    args = parser.parse_args()
    generate(args.root, args.iaf_jar, args.tfc_jar)


if __name__ == "__main__":
    main()
