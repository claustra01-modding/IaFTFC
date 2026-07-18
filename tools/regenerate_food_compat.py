#!/usr/bin/env python3
"""Regenerate TFC food definitions and dragon meat compatibility tags."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZipFile


DRAGON_FLESH = ("fire_dragon_flesh", "ice_dragon_flesh", "lightning_dragon_flesh")
DRAGON_RICE = (
    "cooked_rice_with_fire_dragon_meat",
    "cooked_rice_with_ice_dragon_meat",
    "cooked_rice_with_lightning_dragon_meat",
)

TFC_REFERENCE_FOODS = (
    "beef",
    "carrot",
    "cheese",
    "cooked_rice",
    "jam",
    "potato",
    "pumpkin_pie",
    "sugarcane",
)
NUTRIENTS = ("grain", "vegetables", "fruit", "protein", "dairy")
IAF_HUNGER = {
    "dragon_flesh": 8,
    "pixie_dust": 1,
    "ambrosia": 5,
    "cannoli": 20,
    "dragon_rice": 4,
    "delight_drink": 4,
}


def read_tfc_foods(tfc_jar: Path) -> dict[str, dict]:
    foods: dict[str, dict] = {}
    with ZipFile(tfc_jar) as archive:
        for name in TFC_REFERENCE_FOODS:
            entry = f"data/tfc/tfc/food/{name}.json"
            try:
                foods[name] = json.loads(archive.read(entry))
            except KeyError as error:
                raise ValueError(f"TFC reference food does not exist: {entry}") from error
    return foods


def fields(food: dict, *names: str) -> dict[str, float | int]:
    return {name: food[name] for name in names}


def build_foods(tfc: dict[str, dict]) -> dict[str, dict[str, float | int]]:
    # TFC supplies the nutrient and decay scale. IaF's original hunger values and
    # deliberately exceptional foods remain exceptional instead of being flattened
    # to TFC's usual four hunger points.
    raw_meat = fields(tfc["beef"], "hunger", "protein", "decay_modifier")
    raw_meat["hunger"] = IAF_HUNGER["dragon_flesh"]
    raw_meat["saturation"] = tfc["cheese"]["saturation"]
    raw_meat["protein"] = 3.0
    pixie_dust = fields(tfc["sugarcane"], "hunger", "decay_modifier")
    pixie_dust["hunger"] = IAF_HUNGER["pixie_dust"]
    pixie_dust["saturation"] = 0.8

    # The IaF rice meal consumes all four ingredients into one bowl and also grants
    # Saturation. Keep the full TFC ingredient nutrients; it is intentionally much
    # stronger than one of the three servings produced by a normal TFC soup.
    rice = tfc["cooked_rice"]
    potato = tfc["potato"]
    carrot = tfc["carrot"]
    rice_dish = {
        "hunger": IAF_HUNGER["dragon_rice"],
        "water": 20.0,
        "saturation": 1.5,
        "grain": round(rice.get("grain", 0.0) + potato.get("grain", 0.0), 1),
        "vegetables": round(
            potato.get("vegetables", 0.0) + carrot.get("vegetables", 0.0),
            1,
        ),
        "protein": raw_meat["protein"],
        "decay_modifier": 3.5,
    }

    pumpkin_pie = tfc["pumpkin_pie"]
    cheese = tfc["cheese"]
    jam = tfc["jam"]
    prepared_dairy = {
        "hunger": IAF_HUNGER["delight_drink"],
        "water": 10.0,
        "saturation": 1.5,
        "dairy": 2.0,  # TFC FoodData.MILK
        "decay_modifier": pumpkin_pie["decay_modifier"],
    }

    return {
        **{name: dict(raw_meat) for name in DRAGON_FLESH},
        "pixie_dust": pixie_dust,
        "ambrosia": {
            "hunger": IAF_HUNGER["ambrosia"],
            "saturation": 1.5,
            "fruit": jam["fruit"],
            "dairy": pumpkin_pie["dairy"],
            "decay_modifier": pumpkin_pie["decay_modifier"],
        },
        "cannoli": {
            "hunger": IAF_HUNGER["cannoli"],
            "saturation": 5.0,
            "grain": rice["grain"],
            "dairy": cheese["dairy"],
            "decay_modifier": pumpkin_pie["decay_modifier"],
        },
        **{name: dict(rice_dish) for name in DRAGON_RICE},
        "ghost_cream": dict(prepared_dairy),
        "pixie_dust_milky_tea": {
            **prepared_dairy,
            "water": 20.0,
        },
    }


def write_json(root: Path, relative: str, value: object) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def tag(values: list[str]) -> dict:
    return {"replace": False, "values": values}


def validate(iaf_jar: Path, foods: dict[str, dict[str, float | int]]) -> None:
    allowed_fields = {
        "hunger", "water", "saturation", "intoxication",
        "grain", "vegetables", "fruit", "protein", "dairy", "decay_modifier",
    }
    with ZipFile(iaf_jar) as archive:
        resources = set(archive.namelist())
    for name, food in foods.items():
        if f"assets/iceandfire/models/item/{name}.json" not in resources:
            raise ValueError(f"IaF CE item does not exist: iceandfire:{name}")
        unknown = set(food) - allowed_fields
        if unknown:
            raise ValueError(f"Unknown food fields for {name}: {sorted(unknown)}")
        if food.get("hunger", 0) <= 0 or food.get("decay_modifier", 0) <= 0:
            raise ValueError(f"Food must have positive hunger and decay modifier: {name}")
        if name != "pixie_dust" and not any(nutrient in food for nutrient in NUTRIENTS):
            raise ValueError(f"Food has no TFC nutrients: {name}")


def generate(root: Path, iaf_jar: Path, tfc_jar: Path) -> None:
    foods = build_foods(read_tfc_foods(tfc_jar))
    validate(iaf_jar, foods)
    food_root = root / "data/iaftfc/tfc/food"
    expected_food_files = {f"{name}.json" for name in foods}
    if food_root.exists():
        for existing in food_root.glob("*.json"):
            if existing.name not in expected_food_files:
                existing.unlink()

    for name, food in foods.items():
        definition = {"ingredient": {"item": f"iceandfire:{name}"}, **food}
        write_json(root, f"data/iaftfc/tfc/food/{name}.json", definition)

    all_foods = [f"iceandfire:{name}" for name in foods]
    write_json(root, "data/c/tags/item/foods.json", tag(all_foods))
    write_json(root, "data/c/tags/item/foods/raw_meat.json", tag([f"iceandfire:{name}" for name in DRAGON_FLESH]))
    write_json(root, "data/minecraft/tags/item/meat.json", tag(["#c:foods/meat"]))
    write_json(root, "data/iceandfire/tags/item/dragon_food_meat.json", tag(["#minecraft:meat", "#c:foods/meat"]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("iaf_jar", type=Path)
    parser.add_argument("tfc_jar", type=Path)
    parser.add_argument("--root", type=Path, default=Path("src/main/resources"))
    args = parser.parse_args()
    generate(args.root, args.iaf_jar, args.tfc_jar)


if __name__ == "__main__":
    main()
