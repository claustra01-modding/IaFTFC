#!/usr/bin/env python3
"""Regenerate IaFTFC Dragonsteel data, models, language files, and textures."""

from __future__ import annotations

import argparse
import json
from bisect import bisect_left, bisect_right
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageEnhance


METALS = {
    "dragonsteel_fire": {"dragon": "fire", "steel": "red_steel", "en": "Fire Dragonsteel"},
    "dragonsteel_ice": {"dragon": "ice", "steel": "blue_steel", "en": "Ice Dragonsteel"},
    "dragonsteel_lightning": {"dragon": "lightning", "steel": "black_steel", "en": "Lightning Dragonsteel"},
}

ITEM_FORMS = (
    "ingot", "double_ingot", "sheet", "double_sheet", "rod",
    "sword_blade",
    "unfinished_helmet", "unfinished_chestplate", "unfinished_greaves", "unfinished_boots",
)
TOOL_PARTS = {
    "sword_blade": ("double_ingots", 200, ["hit_last", "bend_second_last", "bend_third_last"]),
}
UNFINISHED_ARMOR = {
    "unfinished_helmet": ("double_sheets", 400, ["hit_last", "bend_second_last", "bend_third_last"]),
    "unfinished_chestplate": ("double_sheets", 400, ["hit_last", "hit_second_last", "upset_third_last"]),
    "unfinished_greaves": ("double_sheets", 400, ["hit_any", "draw_any", "bend_any"]),
    "unfinished_boots": ("sheets", 200, ["bend_last", "bend_second_last", "shrink_third_last"]),
}
DISABLED_TOOLS = ("axe", "hoe", "pickaxe", "shovel")
OBSOLETE_TOOL_HEADS = ("axe_head", "hoe_head", "pickaxe_head", "shovel_head")
UNFINISHED_TEXTURE_SOURCES = {
    "unfinished_helmet": "helmet",
    "unfinished_chestplate": "chestplate",
    "unfinished_greaves": "leggings",
    "unfinished_boots": "boots",
}
UNFINISHED_SATURATION = 0.55
ARMOR = {
    "helmet": ("unfinished_helmet", "sheets", 600),
    "chestplate": ("unfinished_chestplate", "double_sheets", 800),
    "leggings": ("unfinished_greaves", "sheets", 600),
    "boots": ("unfinished_boots", "sheets", 400),
}
HEAT_CAPACITY_PER_100 = 2.857143
FORGING_TEMPERATURE = 1200
WELDING_TEMPERATURE = 1600
MELT_TEMPERATURE = 2000


def write_json(root: Path, relative: str, value: object) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_tag(root: Path, registry: str, path: str, values: list[object]) -> None:
    write_json(root, f"data/c/tags/{registry}/{path}.json", {"replace": False, "values": values})


def remove_obsolete_tool_support(root: Path) -> None:
    for metal in METALS:
        for head in OBSOLETE_TOOL_HEADS:
            for relative in (
                f"assets/iaftfc/models/item/metal/{head}/{metal}.json",
                f"assets/iaftfc/textures/item/metal/{head}/{metal}.png",
                f"data/iaftfc/recipe/anvil/metal/{head}/{metal}.json",
                f"data/iaftfc/recipe/heating/metal/{head}/{metal}.json",
                f"data/iaftfc/tfc/item_heat/{metal}/{head}.json",
            ):
                (root / relative).unlink(missing_ok=True)
        for tool in DISABLED_TOOLS:
            for relative in (
                f"data/iaftfc/recipe/heating/metal/{tool}/{metal}.json",
                f"data/iaftfc/tfc/item_heat/{metal}/{tool}.json",
            ):
                (root / relative).unlink(missing_ok=True)
    for head in OBSOLETE_TOOL_HEADS:
        for relative in (
            f"assets/iaftfc/models/item/metal/{head}",
            f"assets/iaftfc/textures/item/metal/{head}",
            f"data/iaftfc/recipe/anvil/metal/{head}",
            f"data/iaftfc/recipe/heating/metal/{head}",
        ):
            directory = root / relative
            if directory.exists():
                directory.rmdir()


def heat_capacity(amount: int) -> float:
    return round(HEAT_CAPACITY_PER_100 * amount / 100, 6)


def item_heat(root: Path, metal: str, name: str, ingredient: object, amount: int) -> None:
    write_json(root, f"data/iaftfc/tfc/item_heat/{metal}/{name}.json", {
        "ingredient": ingredient,
        "heat_capacity": heat_capacity(amount),
        "forging_temperature": FORGING_TEMPERATURE,
        "welding_temperature": WELDING_TEMPERATURE,
    })


def heating(root: Path, metal: str, name: str, ingredient: object, amount: int) -> None:
    write_json(root, f"data/iaftfc/recipe/heating/metal/{name}/{metal}.json", {
        "type": "tfc:heating",
        "ingredient": ingredient,
        "result_fluid": {"amount": amount, "id": f"tfc:metal/{metal}"},
        "temperature": MELT_TEMPERATURE,
    })


def self_drop(block: str) -> dict:
    return {
        "type": "minecraft:block",
        "pools": [{
            "name": "loot_pool", "rolls": 1,
            "entries": [{"type": "minecraft:item", "name": block}],
            "conditions": [{"condition": "minecraft:survives_explosion"}],
        }],
    }


def generate_data(root: Path) -> None:
    top_tags: dict[str, list[str]] = {form: [] for form in ("ingots", "double_ingots", "sheets", "double_sheets", "rods", "storage_blocks")}
    anvil_ids: list[str] = []
    mineable: list[str] = []
    block_items: list[dict[str, str]] = []
    slab_items: list[dict[str, str]] = []
    stairs_items: list[dict[str, str]] = []
    parts_items: list[dict[str, str]] = []

    for metal, spec in METALS.items():
        dragon = spec["dragon"]
        steel = spec["steel"]
        ingot = f"iaftfc:metal/ingot/{metal}"
        block = f"iaftfc:metal/block/{metal}"
        slab = f"{block}_slab"
        stairs = f"{block}_stairs"
        anvil = f"iaftfc:metal/anvil/{metal}"
        anvil_ids.append(anvil)
        mineable.extend((block, slab, stairs, anvil))
        block_items.append({"item": block})
        slab_items.append({"item": slab})
        stairs_items.append({"item": stairs})

        per_metal_tags = {
            "ingots": [ingot],
            "double_ingots": [f"iaftfc:metal/double_ingot/{metal}"],
            "sheets": [f"iaftfc:metal/sheet/{metal}"],
            "double_sheets": [f"iaftfc:metal/double_sheet/{metal}"],
            "rods": [f"iaftfc:metal/rod/{metal}"],
            "storage_blocks": [block],
        }
        for form, values in per_metal_tags.items():
            write_tag(root, "item", f"{form}/{metal}", values)
            top_tags[form].append(f"#c:{form}/{metal}")
        write_tag(root, "block", f"storage_blocks/{metal}", [block])

        write_json(root, f"data/iceandfire/recipe/dragonforge/{metal}_ingot.json", {
            "type": "iceandfire:dragonforge", "dragonType": dragon, "cookTime": 1000,
            "input": {"tag": f"c:ingots/{steel}"},
            "blood": {"item": f"iceandfire:{dragon}_dragon_blood"},
            "result": {"id": ingot},
        })
        write_json(root, f"data/iaftfc/recipe/casting/{metal}_ingot.json", {
            "type": "tfc:casting", "mold": {"item": "tfc:ceramic/ingot_mold"},
            "fluid": {"amount": 100, "fluid": f"tfc:metal/{metal}"},
            "result": {"count": 1, "id": ingot}, "break_chance": 0.1,
        })
        write_json(root, f"data/iaftfc/recipe/welding/metal/double_ingot/{metal}.json", {
            "type": "tfc:welding", "first_input": {"tag": f"c:ingots/{metal}"},
            "second_input": {"tag": f"c:ingots/{metal}"},
            "result": {"count": 1, "id": f"iaftfc:metal/double_ingot/{metal}"}, "tier": 6,
        })
        write_json(root, f"data/iaftfc/recipe/anvil/metal/sheet/{metal}.json", {
            "type": "tfc:anvil", "ingredient": {"tag": f"c:double_ingots/{metal}"},
            "result": {"count": 1, "id": f"iaftfc:metal/sheet/{metal}"},
            "rules": ["hit_third_last", "hit_second_last", "hit_last"], "tier": 7,
        })
        write_json(root, f"data/iaftfc/recipe/anvil/metal/rod/{metal}.json", {
            "type": "tfc:anvil", "ingredient": {"tag": f"c:ingots/{metal}"},
            "result": {"count": 2, "id": f"iaftfc:metal/rod/{metal}"},
            "rules": ["hit_last", "hit_second_last", "hit_third_last"], "tier": 7,
        })
        write_json(root, f"data/iaftfc/recipe/welding/metal/double_sheet/{metal}.json", {
            "type": "tfc:welding", "first_input": {"tag": f"c:sheets/{metal}"},
            "second_input": {"tag": f"c:sheets/{metal}"},
            "result": {"count": 1, "id": f"iaftfc:metal/double_sheet/{metal}"}, "tier": 7,
        })
        write_json(root, f"data/iaftfc/recipe/crafting/metal/anvil/{metal}.json", {
            "type": "minecraft:crafting_shaped", "category": "misc",
            "key": {"#": {"tag": f"c:double_ingots/{metal}"}},
            "pattern": ["###", " # ", "###"], "result": {"count": 1, "id": anvil},
        })
        write_json(root, f"data/iceandfire/recipe/{metal}_ingot_to_{metal}_block.json", {
            "type": "tfc:advanced_shaped_crafting", "input_column": 2,
            "pattern": [" SH", "SWS", " S "],
            "key": {"H": {"tag": "c:tools/hammer"}, "S": {"tag": f"c:sheets/{metal}"}, "W": {"tag": "minecraft:planks"}},
            "remainder": {"modifiers": [{"type": "tfc:damage_crafting_remainder"}]},
            "result": {"id": block, "count": 8},
        })
        write_json(root, f"data/iceandfire/recipe/{metal}_block_to_{metal}_ingot.json", {
            "neoforge:conditions": [{"type": "neoforge:false"}],
        })

        for part, (input_form, amount, rules) in TOOL_PARTS.items():
            part_id = f"iaftfc:metal/{part}/{metal}"
            parts_items.append({"item": part_id})
            write_json(root, f"data/iaftfc/recipe/anvil/metal/{part}/{metal}.json", {
                "type": "tfc:anvil", "apply_bonus": True,
                "ingredient": {"tag": f"c:{input_form}/{metal}"},
                "result": {"count": 1, "id": part_id}, "rules": rules, "tier": 7,
            })
            item_heat(root, metal, part, {"item": part_id}, amount)
            heating(root, metal, part, {"item": part_id}, amount)

        output = f"iceandfire:{metal}_sword"
        write_json(root, f"data/iceandfire/recipe/{metal}_sword.json", {
                "type": "tfc:advanced_shaped_crafting",
                "key": {"S": {"tag": "c:rods/wooden"}, "X": {"item": f"iaftfc:metal/sword_blade/{metal}"}},
                "pattern": ["X", "S"],
                "result": {"modifiers": [{"type": "tfc:copy_forging_bonus"}], "stack": {"count": 1, "id": output}},
        })
        item_heat(root, metal, "sword", {"item": output}, 200)
        heating(root, metal, "sword", {"item": output}, 200)
        for tool in DISABLED_TOOLS:
            write_json(root, f"data/iceandfire/recipe/{metal}_{tool}.json", {
                "neoforge:conditions": [{"type": "neoforge:false"}],
            })

        for unfinished, (input_form, amount, rules) in UNFINISHED_ARMOR.items():
            unfinished_id = f"iaftfc:metal/{unfinished}/{metal}"
            parts_items.append({"item": unfinished_id})
            write_json(root, f"data/iaftfc/recipe/anvil/metal/{unfinished}/{metal}.json", {
                "type": "tfc:anvil", "apply_bonus": True,
                "ingredient": {"tag": f"c:{input_form}/{metal}"},
                "result": {"count": 1, "id": unfinished_id}, "rules": rules, "tier": 7,
            })
            item_heat(root, metal, unfinished, {"item": unfinished_id}, amount)
            heating(root, metal, unfinished, {"item": unfinished_id}, amount)

        for armor, (unfinished, second_form, amount) in ARMOR.items():
            output = f"iceandfire:{metal}_{armor}"
            write_json(root, f"data/iceandfire/recipe/{metal}_{armor}.json", {
                "type": "tfc:welding", "bonus": "copy_best",
                "first_input": {"item": f"iaftfc:metal/{unfinished}/{metal}"},
                "second_input": {"tag": f"c:{second_form}/{metal}"},
                "result": {"count": 1, "id": output}, "tier": 7,
            })
            item_heat(root, metal, armor, {"item": output}, amount)
            heating(root, metal, armor, {"item": output}, amount)

        basic_amounts = {"ingot": 100, "double_ingot": 200, "sheet": 200, "double_sheet": 400, "rod": 50}
        for form, amount in basic_amounts.items():
            ingredient = {"tag": f"c:{form + 's' if form != 'double_ingot' else 'double_ingots'}/{metal}"}
            item_heat(root, metal, form, ingredient, amount)
            heating(root, metal, form, ingredient, amount)
        block_amounts = {"block": (block, 100), "block_slab": (slab, 50), "block_stairs": (stairs, 75), "anvil": (anvil, 1400)}
        for name, (item_id, amount) in block_amounts.items():
            ingredient = {"item": item_id}
            item_heat(root, metal, name, ingredient, amount)
            heating(root, metal, name, ingredient, amount)
        for relative in (
            f"data/iaftfc/tfc/item_heat/{metal}/legacy_block.json",
            f"data/iaftfc/recipe/heating/metal/legacy_block/{metal}.json",
        ):
            (root / relative).unlink(missing_ok=True)
        write_json(root, f"data/iaftfc/tfc/fluid_heat/{metal}.json", {
            "fluid": f"tfc:metal/{metal}", "melt_temperature": MELT_TEMPERATURE, "specific_heat_capacity": 0.00857,
        })

        for item_id, is_slab in ((block, False), (slab, True), (stairs, False), (anvil, False)):
            loot = self_drop(item_id)
            if is_slab:
                loot["pools"][0]["entries"][0]["functions"] = [{
                    "function": "minecraft:set_count", "count": 2, "add": False,
                    "conditions": [{"condition": "minecraft:block_state_property", "block": item_id, "properties": {"type": "double"}}],
                }]
            path = item_id.split(":", 1)[1]
            write_json(root, f"data/iaftfc/loot_table/blocks/{path}.json", loot)

    for form, values in top_tags.items():
        write_tag(root, "item", form, values)
    write_json(root, "data/tfc/tags/item/anvils.json", {"replace": False, "values": anvil_ids})
    write_json(root, "data/tfc/tags/block/anvils.json", {"replace": False, "values": anvil_ids})
    molten_metals = [f"tfc:metal/{metal}" for metal in METALS]
    write_json(root, "data/tfc/tags/fluid/molten_metals.json", {"replace": False, "values": molten_metals})
    for metal in METALS:
        write_tag(root, "fluid", f"molten_{metal}", [f"tfc:metal/{metal}"])
    write_json(root, "data/minecraft/tags/block/mineable/pickaxe.json", {"replace": False, "values": mineable})
    write_json(root, "data/tfc/tfc/item_size/iaftfc_metal_blocks.json", {"ingredient": block_items, "size": "small", "weight": "light"})
    write_json(root, "data/tfc/tfc/item_size/iaftfc_metal_slabs.json", {"ingredient": slab_items, "size": "small", "weight": "very_light"})
    write_json(root, "data/tfc/tfc/item_size/iaftfc_metal_stairs.json", {"ingredient": stairs_items, "size": "small", "weight": "light"})
    write_json(root, "data/tfc/tfc/item_size/iaftfc_dragonsteel_parts.json", {"ingredient": parts_items, "size": "large", "weight": "medium"})


def generate_dragon_forge_brick_recipes(root: Path, tfc_path: Path, iaf_path: Path) -> None:
    with ZipFile(tfc_path) as tfc, ZipFile(iaf_path) as iaf:
        fire_bricks = json.loads(tfc.read("data/tfc/recipe/crafting/fire_bricks.json"))
        if fire_bricks.get("result", {}).get("id") != "tfc:fire_bricks":
            raise ValueError("TFC fire brick block recipe has an unexpected result")

        for dragon in ("fire", "ice", "lightning"):
            recipe_name = f"dragonforge_{dragon}_brick"
            source = json.loads(iaf.read(f"data/iceandfire/recipe/{recipe_name}.json"))
            if source.get("type") != "minecraft:crafting_shaped":
                raise ValueError(f"IaF {recipe_name} is no longer a shaped recipe")
            if source.get("key", {}).get("B", {}).get("item") != "minecraft:stone_bricks":
                raise ValueError(f"IaF {recipe_name} no longer uses Stone Bricks as B")
            if source.get("result", {}).get("id") != f"iceandfire:{recipe_name}":
                raise ValueError(f"IaF {recipe_name} has an unexpected result")
            source["key"]["B"] = {"item": "tfc:fire_bricks"}
            write_json(root, f"data/iceandfire/recipe/{recipe_name}.json", source)


def load_png(archive: ZipFile, member: str) -> tuple[tuple[int, int], list[tuple[int, int, int, int]]]:
    with Image.open(BytesIO(archive.read(member))) as image:
        rgba = image.convert("RGBA")
        return rgba.size, list(rgba.get_flattened_data())


def load_desaturated_png(archive: ZipFile, member: str, saturation: float) -> tuple[tuple[int, int], list[tuple[int, int, int, int]]]:
    with Image.open(BytesIO(archive.read(member))) as image:
        rgba = image.convert("RGBA")
        adjusted = ImageEnhance.Color(rgba).enhance(saturation)
        return adjusted.size, list(adjusted.get_flattened_data())


def luminance(pixel: tuple[int, int, int, int]) -> float:
    return (0.2126 * pixel[0] + 0.7152 * pixel[1] + 0.0722 * pixel[2]) / 255


def transfer(base: list[tuple[int, int, int, int]], source: list[tuple[int, int, int, int]], scale: float = 1.0) -> list[tuple[int, int, int, int]]:
    palette = sorted((pixel for pixel in source if pixel[3]), key=lambda pixel: (luminance(pixel), pixel[:3]))
    levels = sorted(luminance(pixel) for pixel in base if pixel[3])
    output = []
    for pixel in base:
        if not pixel[3]:
            output.append((0, 0, 0, 0))
            continue
        lo = bisect_left(levels, luminance(pixel))
        hi = bisect_right(levels, luminance(pixel)) - 1
        percentile = 0.5 if len(levels) == 1 else ((lo + hi) / 2) / (len(levels) - 1)
        percentile = 0.5 + (percentile - 0.5) * scale
        position = percentile * (len(palette) - 1)
        lower = int(position)
        upper = min(lower + 1, len(palette) - 1)
        amount = position - lower
        rgb = tuple(round(palette[lower][i] + (palette[upper][i] - palette[lower][i]) * amount) for i in range(3))
        output.append((*rgb, pixel[3]))
    return output


def save_png(path: Path, size: tuple[int, int], pixels: list[tuple[int, int, int, int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGBA", size)
    image.putdata(pixels)
    image.save(path, optimize=True)


def generate_assets(root: Path, tfc_path: Path, iaf_path: Path) -> None:
    lang_path = root / "assets/iaftfc/lang/en_us.json"
    en = json.loads(lang_path.read_text(encoding="utf-8")) if lang_path.exists() else {}
    for key in tuple(en):
        if key == "itemGroup.iaftfc.dragonsteel" or key.startswith((
            "item.iaftfc.metal.",
            "block.iaftfc.metal.",
            "fluid.tfc.metal.dragonsteel_",
        )):
            del en[key]
    en["itemGroup.iaftfc.dragonsteel"] = "IaFTFC Dragonsteel"
    form_names = {
        "ingot": "Ingot", "double_ingot": "Double Ingot",
        "sheet": "Sheet", "double_sheet": "Double Sheet", "rod": "Rod",
        "axe_head": "Axe Head", "hoe_head": "Hoe Head",
        "pickaxe_head": "Pickaxe Head", "shovel_head": "Shovel Head",
        "sword_blade": "Sword Blade", "unfinished_helmet": "Unfinished Helmet",
        "unfinished_chestplate": "Unfinished Chestplate",
        "unfinished_greaves": "Unfinished Greaves", "unfinished_boots": "Unfinished Boots",
    }
    with ZipFile(tfc_path) as tfc, ZipFile(iaf_path) as iaf:
        stairs_template = json.loads(tfc.read("assets/tfc/blockstates/metal/block/red_steel_stairs.json"))
        for metal, spec in METALS.items():
            _, source = load_png(iaf, f"assets/iceandfire/textures/item/{metal}_ingot.png")
            for form in ITEM_FORMS:
                if form in UNFINISHED_TEXTURE_SOURCES:
                    armor = UNFINISHED_TEXTURE_SOURCES[form]
                    size, pixels = load_desaturated_png(
                        iaf,
                        f"assets/iceandfire/textures/item/{metal}_{armor}.png",
                        UNFINISHED_SATURATION,
                    )
                else:
                    member = f"assets/tfc/textures/item/metal/{form}/{spec['steel']}.png"
                    size, base = load_png(tfc, member)
                    pixels = transfer(base, source)
                save_png(root / f"assets/iaftfc/textures/item/metal/{form}/{metal}.png", size, pixels)
                write_json(root, f"assets/iaftfc/models/item/metal/{form}/{metal}.json", {
                    "parent": "item/generated", "textures": {"layer0": f"iaftfc:item/metal/{form}/{metal}"},
                })
                en[f"item.iaftfc.metal.{form}.{metal}"] = f"{spec['en']} {form_names[form]}"

            for texture, scale in (("block", 0.55), ("smooth", 1.0)):
                size, base = load_png(tfc, f"assets/tfc/textures/block/metal/{texture}/{spec['steel']}.png")
                namespace = "iaftfc" if texture == "block" else "tfc"
                save_png(root / f"assets/{namespace}/textures/block/metal/{texture}/{metal}.png", size, transfer(base, source, scale))

            block_model = f"iaftfc:block/metal/block/{metal}"
            write_json(root, f"assets/iaftfc/blockstates/metal/block/{metal}.json", {"variants": {"": {"model": block_model}}})
            write_json(root, f"assets/iaftfc/models/block/metal/block/{metal}.json", {"parent": "minecraft:block/cube_all", "textures": {"all": block_model}})
            for suffix, parent in (("_slab", "block/slab"), ("_slab_top", "block/slab_top"), ("_stairs", "block/stairs"), ("_stairs_inner", "block/inner_stairs"), ("_stairs_outer", "block/outer_stairs")):
                write_json(root, f"assets/iaftfc/models/block/metal/block/{metal}{suffix}.json", {
                    "parent": parent, "textures": {"bottom": block_model, "top": block_model, "side": block_model},
                })
            write_json(root, f"assets/iaftfc/blockstates/metal/block/{metal}_slab.json", {"variants": {
                "type=bottom": {"model": f"{block_model}_slab"}, "type=top": {"model": f"{block_model}_slab_top"},
                "type=double": {"model": block_model},
            }})
            stairs = json.loads(json.dumps(stairs_template).replace("tfc:block/metal/block/red_steel", block_model))
            write_json(root, f"assets/iaftfc/blockstates/metal/block/{metal}_stairs.json", stairs)
            for suffix in ("", "_slab", "_stairs"):
                write_json(root, f"assets/iaftfc/models/item/metal/block/{metal}{suffix}.json", {"parent": f"{block_model}{suffix}"})

            anvil_model = f"iaftfc:block/metal/anvil/{metal}"
            write_json(root, f"assets/iaftfc/blockstates/metal/anvil/{metal}.json", {"variants": {
                "facing=north": {"model": anvil_model, "y": 90}, "facing=east": {"model": anvil_model, "y": 180},
                "facing=south": {"model": anvil_model, "y": 270}, "facing=west": {"model": anvil_model},
            }})
            write_json(root, f"assets/iaftfc/models/block/metal/anvil/{metal}.json", {
                "parent": "tfc:block/anvil", "textures": {"all": f"tfc:block/metal/smooth/{metal}", "particle": f"tfc:block/metal/smooth/{metal}"},
            })
            write_json(root, f"assets/iaftfc/models/item/metal/anvil/{metal}.json", {"parent": anvil_model})
            write_json(root, f"assets/tfc/blockstates/fluid/metal/{metal}.json", {"variants": {"": {"model": f"tfc:block/fluid/metal/{metal}"}}})
            write_json(root, f"assets/tfc/models/block/fluid/metal/{metal}.json", {"textures": {"particle": "block/lava_still"}})

            en[f"block.iaftfc.metal.block.{metal}"] = f"{spec['en']} Plated Block"
            en[f"block.iaftfc.metal.block.{metal}_slab"] = f"{spec['en']} Plated Slab"
            en[f"block.iaftfc.metal.block.{metal}_stairs"] = f"{spec['en']} Plated Stairs"
            en[f"block.iaftfc.metal.anvil.{metal}"] = f"{spec['en']} Anvil"
            en[f"fluid.tfc.metal.{metal}"] = f"Molten {spec['en']}"

    write_json(root, "assets/iaftfc/lang/en_us.json", dict(sorted(en.items())))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tfc-jar", required=True, type=Path)
    parser.add_argument("--iaf-jar", required=True, type=Path)
    parser.add_argument("--output", default=Path("src/main/resources"), type=Path)
    args = parser.parse_args()
    remove_obsolete_tool_support(args.output)
    generate_data(args.output)
    generate_dragon_forge_brick_recipes(args.output, args.tfc_jar, args.iaf_jar)
    generate_assets(args.output, args.tfc_jar, args.iaf_jar)


if __name__ == "__main__":
    main()
