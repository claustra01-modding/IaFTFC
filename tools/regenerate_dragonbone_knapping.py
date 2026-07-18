#!/usr/bin/env python3
"""Regenerate Dragon Bone knapping, tool-part recipes, models, and textures."""

from __future__ import annotations

import argparse
import json
from bisect import bisect_left, bisect_right
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from PIL import Image


TOOL_SPECS = {
    "axe": {"part": "axe_head", "tfc_pattern": "axe_head"},
    "hoe": {"part": "hoe_head", "tfc_pattern": "hoe_head"},
    "pickaxe": {
        "part": "pickaxe_head",
        "tfc_mold_pattern": "unfired_pickaxe_head_mold",
    },
    "shovel": {"part": "shovel_head", "tfc_pattern": "shovel_head"},
    "sword": {
        "part": "sword_blade",
        "tfc_mold_pattern": "unfired_sword_blade_mold",
    },
}
FLUTE_PATTERN = ["#####", "# # #", "##  #", "#  ##", "#####"]
PRESERVED_RECIPES = (
    "dragonbone_arrow",
    "dragonbone_bow",
    "dragonbone_sword_fire",
    "dragonbone_sword_ice",
    "dragonbone_sword_lightning",
)
TFC_TEXTURE_TEMPLATES = {
    "axe_head": "assets/tfc/textures/item/stone/axe_head.png",
    "hoe_head": "assets/tfc/textures/item/stone/hoe_head.png",
    "pickaxe_head": "assets/tfc/textures/item/metal/pickaxe_head/wrought_iron.png",
    "shovel_head": "assets/tfc/textures/item/stone/shovel_head.png",
    "sword_blade": "assets/tfc/textures/item/metal/sword_blade/wrought_iron.png",
}
DISPLAY_NAMES = {
    "axe_head": "Dragon Bone Axe Head",
    "hoe_head": "Dragon Bone Hoe Head",
    "pickaxe_head": "Dragon Bone Pickaxe Head",
    "shovel_head": "Dragon Bone Shovel Head",
    "sword_blade": "Dragon Bone Sword Blade",
}


def read_json(archive: ZipFile, member: str) -> dict:
    try:
        return json.loads(archive.read(member))
    except KeyError as error:
        raise ValueError(f"Required JAR resource does not exist: {member}") from error


def write_json(root: Path, relative: str, value: object) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_rgba(archive: ZipFile, member: str) -> Image.Image:
    try:
        raw = archive.read(member)
    except KeyError as error:
        raise ValueError(f"Required JAR texture does not exist: {member}") from error
    with Image.open(BytesIO(raw)) as image:
        rgba = image.convert("RGBA")
        if rgba.size != (16, 16):
            raise ValueError(f"Expected a 16x16 texture: {member} is {rgba.size}")
        return rgba.copy()


def luminance(pixel: tuple[int, int, int, int]) -> float:
    return (0.2126 * pixel[0] + 0.7152 * pixel[1] + 0.0722 * pixel[2]) / 255


def transfer_palette(template: Image.Image, source: Image.Image) -> Image.Image:
    base = list(template.get_flattened_data())
    palette = sorted((pixel for pixel in source.get_flattened_data() if pixel[3]), key=lambda pixel: (luminance(pixel), pixel[:3]))
    levels = sorted(luminance(pixel) for pixel in base if pixel[3])
    if not palette or not levels:
        raise ValueError("Cannot transfer an empty texture palette")
    output: list[tuple[int, int, int, int]] = []
    for pixel in base:
        if not pixel[3]:
            output.append((0, 0, 0, 0))
            continue
        low = bisect_left(levels, luminance(pixel))
        high = bisect_right(levels, luminance(pixel)) - 1
        percentile = 0.5 if len(levels) == 1 else ((low + high) / 2) / (len(levels) - 1)
        position = percentile * (len(palette) - 1)
        lower = int(position)
        upper = min(lower + 1, len(palette) - 1)
        amount = position - lower
        rgb = tuple(round(palette[lower][i] + (palette[upper][i] - palette[lower][i]) * amount) for i in range(3))
        output.append((*rgb, pixel[3]))
    image = Image.new("RGBA", template.size)
    image.putdata(output)
    return image


def save_png(path: Path, image: Image.Image) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)


def validate_pattern(name: str, pattern: list[str]) -> None:
    if not 1 <= len(pattern) <= 5 or any(not 1 <= len(row) <= 5 for row in pattern):
        raise ValueError(f"Invalid 5x5 knapping pattern for {name}: {pattern}")
    if any(character not in " #" for row in pattern for character in row):
        raise ValueError(f"Unexpected character in knapping pattern for {name}")


def expand_pattern(pattern: list[str], default_on: bool = False) -> list[str]:
    """Center a compact TFC pattern in an explicit 5x5 grid."""
    width = len(pattern[0])
    height = len(pattern)
    offset_x = (5 - width) // 2
    offset_y = (5 - height) // 2
    expanded = [["#" if default_on else " " for _ in range(5)] for _ in range(5)]
    for y, row in enumerate(pattern):
        for x, character in enumerate(row):
            expanded[offset_y + y][offset_x + x] = character
    return ["".join(row) for row in expanded]


def invert_mold_pattern(source: dict) -> list[str]:
    """Return the material occupying the cavity removed from a 5x5 clay mold."""
    mold = source["pattern"]
    width = len(mold[0])
    height = len(mold)
    default_on = source.get("default_on", False)
    inverted: list[str] = []
    for y in range(5):
        row = []
        for x in range(5):
            mold_on = mold[y][x] != " " if x < width and y < height else default_on
            row.append(" " if mold_on else "#")
        inverted.append("".join(row))
    return inverted


def validate_iaf_recipes(iaf: ZipFile) -> None:
    for tool in TOOL_SPECS:
        recipe = read_json(iaf, f"data/iceandfire/recipe/dragonbone_{tool}.json")
        if recipe.get("type") != "minecraft:crafting_shaped":
            raise ValueError(f"IaF dragonbone_{tool} is no longer a shaped recipe")
        if recipe.get("result", {}).get("id") != f"iceandfire:dragonbone_{tool}":
            raise ValueError(f"IaF dragonbone_{tool} has an unexpected result")
    flute = read_json(iaf, "data/iceandfire/recipe/dragon_flute.json")
    if flute.get("result", {}).get("id") != "iceandfire:dragon_flute":
        raise ValueError("IaF Dragon Flute recipe has an unexpected result")
    for recipe_name in PRESERVED_RECIPES:
        read_json(iaf, f"data/iceandfire/recipe/{recipe_name}.json")


def load_patterns(tfc: ZipFile) -> dict[str, dict]:
    patterns: dict[str, dict] = {}
    for tool, spec in TOOL_SPECS.items():
        tfc_part = spec.get("tfc_pattern")
        if tfc_part:
            source = read_json(tfc, f"data/tfc/recipe/knapping/stone/{tfc_part}/sedimentary.json")
            if source.get("type") != "tfc:knapping" or source.get("knapping_type") != "tfc:rock":
                raise ValueError(f"TFC {tfc_part} source is no longer a rock knapping recipe")
        else:
            mold = spec["tfc_mold_pattern"]
            source = read_json(tfc, f"data/tfc/recipe/knapping/ceramic/{mold}.json")
            if source.get("type") != "tfc:knapping" or source.get("knapping_type") != "tfc:clay":
                raise ValueError(f"TFC {mold} source is no longer a clay knapping recipe")
        if tfc_part:
            patterns[tool] = {
                "pattern": expand_pattern(source["pattern"], source.get("default_on", False)),
            }
        else:
            # A mold recipe keeps '#': its spaces are the carved cavity. A bone
            # head must keep that cavity's shape, so expand then invert it.
            patterns[tool] = {"pattern": invert_mold_pattern(source)}
        validate_pattern(tool, patterns[tool]["pattern"])
    validate_pattern("dragon_flute", FLUTE_PATTERN)
    return patterns


def generate_data(root: Path, patterns: dict[str, dict]) -> None:
    write_json(root, "data/iaftfc/tfc/knapping_type/dragonbone.json", {
        "amount_to_consume": 1,
        "click_sound": "tfc:item.knapping.stone",
        "consume_after_complete": False,
        "has_off_texture": False,
        "icon": {"count": 1, "id": "iceandfire:dragonbone"},
        "input": {"count": 2, "item": "iceandfire:dragonbone"},
        "spawns_particles": True,
    })

    part_items: list[dict[str, str]] = []
    for tool, spec in TOOL_SPECS.items():
        part = spec["part"]
        part_id = f"iaftfc:dragonbone/{part}"
        part_items.append({"item": part_id})
        recipe = {
            "type": "tfc:knapping",
            "knapping_type": "iaftfc:dragonbone",
            "pattern": patterns[tool]["pattern"],
            "result": {"count": 1, "id": part_id},
        }
        write_json(root, f"data/iaftfc/recipe/knapping/dragonbone/{part}.json", recipe)
        write_json(root, f"data/iceandfire/recipe/dragonbone_{tool}.json", {
            "type": "minecraft:crafting_shaped",
            "category": "equipment",
            "key": {
                "S": {"tag": "c:bones/wither"},
                "X": {"item": part_id},
            },
            "pattern": ["X", "S"],
            "result": {"count": 1, "id": f"iceandfire:dragonbone_{tool}"},
        })

    write_json(root, "data/iceandfire/recipe/dragon_flute.json", {
        "type": "tfc:knapping",
        "knapping_type": "iaftfc:dragonbone",
        "pattern": FLUTE_PATTERN,
        "result": {"count": 1, "id": "iceandfire:dragon_flute"},
    })
    write_json(root, "data/tfc/tfc/item_size/iaftfc_dragonbone_parts.json", {
        "ingredient": part_items,
        "size": "large",
        "weight": "medium",
    })


def generate_assets(root: Path, tfc: ZipFile, iaf: ZipFile) -> None:
    source = load_rgba(iaf, "assets/iceandfire/textures/item/dragonbone.png")
    for part, template_path in TFC_TEXTURE_TEMPLATES.items():
        texture = transfer_palette(load_rgba(tfc, template_path), source)
        save_png(root / f"assets/iaftfc/textures/item/dragonbone/{part}.png", texture)
        write_json(root, f"assets/iaftfc/models/item/dragonbone/{part}.json", {
            "parent": "item/generated",
            "textures": {"layer0": f"iaftfc:item/dragonbone/{part}"},
        })

    # KnappingScreen derives this TFC-namespaced path from iceandfire:dragonbone.
    save_png(
        root / "assets/tfc/textures/gui/knapping/dragonbone.png",
        load_rgba(iaf, "assets/iceandfire/textures/block/dragon_bone_block_side.png"),
    )

    lang_path = root / "assets/iaftfc/lang/en_us.json"
    language = json.loads(lang_path.read_text(encoding="utf-8")) if lang_path.exists() else {}
    for part, display_name in DISPLAY_NAMES.items():
        language[f"item.iaftfc.dragonbone.{part}"] = display_name
    language["tfc.jei.dragonbone_knapping"] = "Dragon Bone Knapping Recipe"
    write_json(root, "assets/iaftfc/lang/en_us.json", dict(sorted(language.items())))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tfc_jar", type=Path)
    parser.add_argument("iaf_jar", type=Path)
    parser.add_argument("--root", type=Path, default=Path("src/main/resources"))
    args = parser.parse_args()

    with ZipFile(args.tfc_jar) as tfc, ZipFile(args.iaf_jar) as iaf:
        validate_iaf_recipes(iaf)
        patterns = load_patterns(tfc)
        generate_data(args.root, patterns)
        generate_assets(args.root, tfc, iaf)
    print("Generated Dragon Bone knapping, five tool parts, five assembly recipes, and the direct Flute recipe")


if __name__ == "__main__":
    main()
