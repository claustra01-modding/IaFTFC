#!/usr/bin/env python3
"""Regenerate TFC knapping data and GUI textures for IaF Dragon Scale armor."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZipFile


COLORS = (
    "amethyst", "black", "blue", "bronze", "copper", "electric",
    "gray", "green", "red", "sapphire", "silver", "white",
)
PARTS = ("helmet", "chestplate", "leggings", "boots")
SCALE_COST = 5


def read_json(archive: ZipFile, name: str) -> dict:
    try:
        return json.loads(archive.read(name))
    except KeyError as error:
        raise ValueError(f"Required JAR resource does not exist: {name}") from error


def write_json(root: Path, relative: str, value: object) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_bytes(root: Path, relative: str, value: bytes) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value)


def source_recipe_name(color: str, part: str) -> str:
    # IaF CE keeps the historical typo in recipe IDs only.
    recipe_color = "amythest" if color == "amethyst" else color
    return f"armor_{recipe_color}_{part}"


def load_patterns(tfc: ZipFile) -> dict[str, dict]:
    patterns: dict[str, dict] = {}
    for part in PARTS:
        source = read_json(tfc, f"data/tfc/recipe/knapping/leather_{part}.json")
        if source.get("type") != "tfc:knapping" or source.get("knapping_type") != "tfc:leather":
            raise ValueError(f"TFC leather {part} recipe is not a leather knapping recipe")
        patterns[part] = {
            "pattern": source["pattern"],
            **({"default_on": source["default_on"]} if "default_on" in source else {}),
        }
    return patterns


def validate_iaf_recipes(iaf: ZipFile) -> None:
    for color in COLORS:
        scale = f"iceandfire:dragonscales_{color}"
        for part in PARTS:
            recipe_name = source_recipe_name(color, part)
            source = read_json(iaf, f"data/iceandfire/recipe/{recipe_name}.json")
            expected_result = f"iceandfire:armor_{color}_{part}"
            if source.get("type") != "minecraft:crafting_shaped":
                raise ValueError(f"IaF recipe is not shaped crafting: {recipe_name}")
            if source.get("key", {}).get("#", {}).get("item") != scale:
                raise ValueError(f"IaF recipe uses an unexpected scale: {recipe_name}")
            if source.get("result", {}).get("id") != expected_result:
                raise ValueError(f"IaF recipe has an unexpected result: {recipe_name}")


def generate(root: Path, tfc_jar: Path, iaf_jar: Path) -> None:
    with ZipFile(tfc_jar) as tfc, ZipFile(iaf_jar) as iaf:
        patterns = load_patterns(tfc)
        validate_iaf_recipes(iaf)

        # KnappingScreen always resolves button textures in TFC's namespace from
        # the input item path. Supply those paths using IaF's scale block faces,
        # which read as a continuous material across the 5x5 knapping grid.
        for color in COLORS:
            source = f"assets/iceandfire/textures/block/dragonscale_{color}.png"
            try:
                texture = iaf.read(source)
            except KeyError as error:
                raise ValueError(f"Required IaF scale block texture does not exist: {source}") from error
            write_bytes(root, f"assets/tfc/textures/gui/knapping/dragonscales_{color}.png", texture)

    # One type gives JEI one tab. Recipe-level ingredients retain strict color
    # matching, following the same mechanism used by TFC's shared rock type.
    write_json(root, "data/iaftfc/tags/item/dragon_scales.json", {
        "replace": False,
        "values": [f"iceandfire:dragonscales_{color}" for color in COLORS],
    })
    write_json(root, "data/iaftfc/tfc/knapping_type/dragon_scale.json", {
        "click_sound": "tfc:item.knapping.leather",
        "consume_after_complete": True,
        "has_off_texture": False,
        "icon": {"count": 1, "id": "iceandfire:dragonscales_red"},
        "input": {"count": SCALE_COST, "tag": "iaftfc:dragon_scales"},
        "spawns_particles": False,
    })

    lang_path = root / "assets/iaftfc/lang/en_us.json"
    language = json.loads(lang_path.read_text(encoding="utf-8")) if lang_path.exists() else {}
    # TFC builds JEI category keys as tfc.jei.<knapping type path>_knapping.
    language["tfc.jei.dragon_scale_knapping"] = "Dragon Scale Knapping Recipe"
    write_json(root, "assets/iaftfc/lang/en_us.json", dict(sorted(language.items())))

    type_dir = root / "data/iaftfc/tfc/knapping_type"
    for color in COLORS:
        stale_type = type_dir / f"dragon_scale_{color}.json"
        if stale_type.exists():
            stale_type.unlink()

    for color in COLORS:
        scale = f"iceandfire:dragonscales_{color}"
        for part in PARTS:
            recipe_name = source_recipe_name(color, part)
            pattern = patterns[part]
            recipe = {
                "type": "tfc:knapping",
                "ingredient": {"item": scale},
                "knapping_type": "iaftfc:dragon_scale",
                "pattern": pattern["pattern"],
                "result": {"count": 1, "id": f"iceandfire:armor_{color}_{part}"},
            }
            if "default_on" in pattern:
                recipe["default_on"] = pattern["default_on"]
            write_json(root, f"data/iceandfire/recipe/{recipe_name}.json", recipe)

    print(
        f"Generated one Dragon Scale knapping type, {len(COLORS) * len(PARTS)} armor recipes, "
        f"{len(COLORS)} GUI textures, and the JEI category translation"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tfc_jar", type=Path)
    parser.add_argument("iaf_jar", type=Path)
    parser.add_argument("--root", type=Path, default=Path("src/main/resources"))
    args = parser.parse_args()
    generate(args.root, args.tfc_jar, args.iaf_jar)


if __name__ == "__main__":
    main()
