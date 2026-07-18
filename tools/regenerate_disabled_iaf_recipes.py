#!/usr/bin/env python3
"""Regenerate IaF CE recipe overrides disabled in favor of TFC systems."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DISABLED_RECIPES = (
    "armor_silver_metal_boots",
    "armor_silver_metal_chestplate",
    "armor_silver_metal_helmet",
    "armor_silver_metal_leggings",
    "furnace/deepslate_silver_ingot",
    "furnace/deepslate_silver_ingot_blasting",
    "furnace/sapphire",
    "furnace/sapphire_blasting",
    "furnace/silver_ingot",
    "furnace/silver_ingot_blasting",
    "furnace/silver_nugget",
    "furnace/silver_nugget_blasting",
    "raw_silver_block_to_raw_silver",
    "raw_silver_to_raw_silver_block",
    "sapphire_block_to_sapphire_gem",
    "sapphire_gem_to_sapphire_block",
    "silver_axe",
    "silver_block_to_silver_ingot",
    "silver_hoe",
    "silver_ingot_from_blasting_raw_silver",
    "silver_ingot_from_smelting_raw_silver",
    "silver_ingot_to_silver_block",
    "silver_ingot_to_silver_nugget",
    "silver_nugget_to_silver_ingot",
    "silver_pickaxe",
    "silver_pile",
    "silver_shovel",
    "silver_sword",
    *(f"dragonarmor_{material}_{part}" for material in ("copper", "diamond", "gold", "netherite", "silver") for part in ("head", "neck", "body", "tail")),
)

DISABLED_RECIPE = {
    "neoforge:conditions": [
        {"type": "neoforge:false"},
    ],
}


def generate(root: Path) -> None:
    for recipe in DISABLED_RECIPES:
        path = root / f"data/iceandfire/recipe/{recipe}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(DISABLED_RECIPE, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("src/main/resources"))
    args = parser.parse_args()
    generate(args.root)


if __name__ == "__main__":
    main()
