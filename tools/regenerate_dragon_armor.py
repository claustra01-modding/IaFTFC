#!/usr/bin/env python3
"""Regenerate IaFTFC dragon armor recipes, models, language, and textures."""

from __future__ import annotations

import argparse
import json
from bisect import bisect_left, bisect_right
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from PIL import Image


METALS = {
    "steel": "Steel",
    "black_steel": "Black Steel",
    "red_steel": "Red Steel",
    "blue_steel": "Blue Steel",
}
PARTS = {
    "head": ["   ", " ##", "###"],
    "neck": ["   ", "###", " ##"],
    "body": ["###", "###", "# #"],
    "tail": ["   ", "  #", "## "],
}
EXISTING_MATERIALS = {
    "iron": "wrought_iron",
    "dragon_steel_fire": "dragonsteel_fire",
    "dragon_steel_ice": "dragonsteel_ice",
    "dragon_steel_lightning": "dragonsteel_lightning",
}
REFERENCE_MATERIALS = ("iron", "copper", "gold", "silver", "diamond", "netherite")


def write_json(root: Path, relative: str, value: object) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recipe(result: str, ingredient: str, pattern: list[str]) -> dict:
    return {
        "type": "minecraft:crafting_shaped",
        "category": "equipment",
        "key": {"#": {"tag": f"c:double_sheets/{ingredient}"}},
        "pattern": pattern,
        "result": {"id": result},
        "show_notification": True,
    }


def generate_data(root: Path) -> None:
    for material, ingredient in EXISTING_MATERIALS.items():
        for part, pattern in PARTS.items():
            item = f"iceandfire:dragonarmor_{material}_{part}"
            write_json(root, f"data/iceandfire/recipe/dragonarmor_{material}_{part}.json", recipe(item, ingredient, pattern))

    for metal in METALS:
        for part, pattern in PARTS.items():
            item = f"iaftfc:dragonarmor_{metal}_{part}"
            write_json(root, f"data/iaftfc/recipe/dragon_armor/{metal}_{part}.json", recipe(item, metal, pattern))


def load_image(archive: ZipFile, member: str) -> Image.Image:
    with Image.open(BytesIO(archive.read(member))) as image:
        return image.convert("RGBA")


def luminance(pixel: tuple[int, int, int, int]) -> float:
    return (0.2126 * pixel[0] + 0.7152 * pixel[1] + 0.0722 * pixel[2]) / 255


def recolor_metal(base: Image.Image, references: list[Image.Image], palette_image: Image.Image) -> Image.Image:
    base_pixels = list(base.get_flattened_data())
    reference_pixels = [list(image.get_flattened_data()) for image in references]
    metal_mask = [
        pixel[3] > 0 and any(other[index] != pixel for other in reference_pixels)
        for index, pixel in enumerate(base_pixels)
    ]
    source_levels = sorted(luminance(pixel) for pixel, is_metal in zip(base_pixels, metal_mask) if is_metal)
    palette = sorted(
        (pixel for pixel in palette_image.get_flattened_data() if pixel[3]),
        key=lambda pixel: (luminance(pixel), pixel[:3]),
    )
    output: list[tuple[int, int, int, int]] = []
    for pixel, is_metal in zip(base_pixels, metal_mask):
        if not is_metal:
            output.append(pixel)
            continue
        lo = bisect_left(source_levels, luminance(pixel))
        hi = bisect_right(source_levels, luminance(pixel)) - 1
        percentile = 0.5 if len(source_levels) == 1 else ((lo + hi) / 2) / (len(source_levels) - 1)
        position = percentile * (len(palette) - 1)
        lower = int(position)
        upper = min(lower + 1, len(palette) - 1)
        amount = position - lower
        rgb = tuple(round(palette[lower][channel] + (palette[upper][channel] - palette[lower][channel]) * amount) for channel in range(3))
        output.append((*rgb, pixel[3]))
    image = Image.new("RGBA", base.size)
    image.putdata(output)
    return image


def save_image(path: Path, image: Image.Image) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)


def generate_assets(root: Path, tfc_path: Path, iaf_path: Path) -> None:
    lang_path = root / "assets/iaftfc/lang/en_us.json"
    language = json.loads(lang_path.read_text(encoding="utf-8")) if lang_path.exists() else {}

    with ZipFile(tfc_path) as tfc, ZipFile(iaf_path) as iaf:
        palettes = {
            metal: load_image(tfc, f"assets/tfc/textures/item/metal/double_sheet/{metal}.png")
            for metal in METALS
        }
        for metal, english_name in METALS.items():
            language[f"item.iaftfc.dragonarmor_{metal}"] = f"{english_name} Dragon Armor"
            for part in PARTS:
                item_members = [f"assets/iceandfire/textures/item/dragonarmor_{material}_{part}.png" for material in REFERENCE_MATERIALS]
                item_images = [load_image(iaf, member) for member in item_members]
                item_texture = recolor_metal(item_images[0], item_images[1:], palettes[metal])
                save_image(root / f"assets/iaftfc/textures/item/dragonarmor_{metal}_{part}.png", item_texture)
                write_json(root, f"assets/iaftfc/models/item/dragonarmor_{metal}_{part}.json", {
                    "parent": "item/generated",
                    "textures": {"layer0": f"iaftfc:item/dragonarmor_{metal}_{part}"},
                })

                entity_members = [f"assets/iceandfire/textures/entity/dragon_armor/armor_{part}_{material}.png" for material in REFERENCE_MATERIALS]
                entity_images = [load_image(iaf, member) for member in entity_members]
                entity_texture = recolor_metal(entity_images[0], entity_images[1:], palettes[metal])
                save_image(root / f"assets/iceandfire/textures/entity/dragon_armor/armor_{part}_{metal}.png", entity_texture)

    write_json(root, "assets/iaftfc/lang/en_us.json", dict(sorted(language.items())))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("src/main/resources"))
    parser.add_argument("--tfc", type=Path, required=True)
    parser.add_argument("--iaf", type=Path, required=True)
    args = parser.parse_args()
    generate_data(args.root)
    generate_assets(args.root, args.tfc, args.iaf)


if __name__ == "__main__":
    main()
