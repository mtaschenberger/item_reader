from PIL import Image
import pathlib
import multiprocessing as mp
from typing import Optional

import retry

from item_extractor.protocols import (
    LLMServerProtocol, ParserProtocol,
    OCRProtocol, ArtDetectorProtocol, CropperProtocol
)
from item_extractor.text_extractor import (
    LMStudioClient, ItemParser, TesseractOCR
)
from item_extractor.art_extractor import ArtworkDetector, PILCropper

from item_extractor.markdown_builder.builder import MarkdownBuilder

VAULT_PATH = "/Users/marvintaschenberger/Projects/Vaults/PhandalinHomebrew/Generator"

SYSTEM_PROMPT = """
########### Instructions ###########
Parse the following RPG item description into JSON with keys depending on the item type.

########### Format ###########
        general item: name (str), description (str), rarity (str), attunement (bool), curse (str|none), subtype (str, one of:[WONDROUS, ROD, SCROLL, STAFF, WAND, RING, POITION]), attunement (bool) attunement_condition (str), curse (object | none),

        armor: name (str), descriptiom (str), rarity, attunement (bool), curse (str|none) subtype(str, one of: [BREAST_PLATE,CHAIN_MAIL,CHAIN_SHIRT ,HALF_PLATE, HIDE, LEATHER,PADDED, PLATE, RING_MAIL, SCALE_MAIL, SHIELD, SPIKED_ARMOR, SPLINT, STUDDED_LEATHER], ),
                dex_bonus (str, one of: [NONE, MAX, FULL]), strength_req (str), stealth_option (str,  one of: [NONE, DIS])

        weapon: name (str), descriptiom (str), rarity, attunement (bool), curse (str|none), subtype(str, one of: [    "Antimatter Rifle", "Battleaxe", "Blowgun", "Boomerang", "Club",
                                    "Crossbow, Hand", "Crossbow, Heavy", "Crossbow, Light", "Dagger",
                                    "Dart", "Double-Bladed Scimitar", "Flail", "Glaive", "Greataxe",
                                    "Greatclub", "Greatsword", "Halberd", "Handaxe", "Javelin", "Lance",
                                    "Laser Pistol", "Laser Rifle", "Light Hammer", "Longbow", "Longsword",
                                    "Mace", "Maul", "Morningstar", "Musket", "Net", "Pike", "Pistol",
                                    "Pistol, Automatic", "Quarterstaff", "Rapier", "Revolver",
                                    "Rifle, Automatic", "Rifle, Hunting", "Scimitar", "Semiautomatic Pistol",
                                    "Shortbow", "Shortsword", "Shotgun", "Sickle", "Sling", "Spear",
                                    "Trident", "War Pick", "Warhammer", "Whip", "Yklwa"])
        ---

####### Example ###########

####### Input ###########

‘Tue ForswoRN Bastion

Armor (plate), very rare (requires attunement by a
Paladin)

Forsworn Bastion is a suit of plate armor forged from
jagged, blackened steel that seems to absorb light
Crimson runes pulse faintly across its surface, and a
‘cold mist rises from the joints. Etched into the
chestplate are the ominous words, “Strength i claimed,
‘not given. Prove your dominance, or be consumed.”

While wearing this armor, you gain a +2 bonus to AC
and resistance to necrotic damage. Additionally, you can
‘add your Charisma modifier to your Strength saving
throws.

Curse. The armor is haunted by the spirit ofa fallen
paladin who abandoned their oath for power. It
constantly urges you to prove your strength through
relentless violence.

+ Possession Couinter. The counter starts at 0. Each
time you take damage, increase it by 1. When the
counter reaches 5, you must make a DC 12 Wisdom
saving throw. Every additional 5 points (10,15, etc),
you must repeat the save, with the DC increasing by
*2each time. On a failure—or ifthe counter reaches
20--you become possessed,

+ Possession. While possessed, the sprit fully takes
‘ver your body for 1 minute, forcing you to attack the
nearest creature (ally or enemy) on each of your
turns, You remain aware of your actions but eannot
resist them,

+ After the Possession Ends: The counter resets to 0,
and the cycle begins anew, forcing you to make a new
saving throw. If you fail, you are still possessed.

+ Artifact Bonus. While wearing this armor, you gain
a +2 bonus to your AC and resistance to necrotic damage.
Additionally, you can add your Charisma modifier to
your Strength saving throws.

####### Output ###########

{
    "name": "ForswoRN Bastion",
    "description": "Armor (plate), very rare (requires attunement by a Paladin)\n\nForsworn Bastion is a suit of plate armor forged from jagged, blackened steel that seems to absorb light. Crimson runes pulse faintly across its surface, and a cold mist rises from the joints. Etched into the chestplate are the ominous words, “Strength i claimed, not given. Prove your dominance, or be consumed.”\n\nWhile wearing this armor, you gain a +2 bonus to AC and resistance to necrotic damage. Additionally, you can add your Charisma modifier to your Strength saving throws.\n\nCurse. The armor is haunted by the spirit ofa fallen paladin who abandoned their oath for power. It constantly urges you to prove your strength through relentless violence.",
    "rarity": "very rare",
    "attunement": true,
    "curse": true,
    "subtype": "plate",
    "dex_bonus": "NONE",
    "strength_req": 15,
    "stealth_option": "DIS"
}

####### End of Example ###########

Please parse the following RPG item description into JSON with keys depending on the item type.

########### End of Instructions ###########
"""

@retry.retry(Exception, delay=2, tries=3)
def process_item(file_queue, vault, port):
    image_path = file_queue.get()
    try:
        # OCR
        text = ocr.extract_text(Image.open(image_path))

        # Parse item data
        item = parser.parse(text)

        # Artwork cropping
        bboxe = art_detector.detect(image_path)
        image_file: Optional[str] = None
        image_file = cropper.crop_save(image_path, bboxe, vault)

        # Generate Markdown
        md_path = md_builder.save(item, image_file)
        print(f"Markdown saved to {md_path}")
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

def worker(*args):
    file_queue = args[0]
    vault: str = args[1]
    port = args[2]
    try:
        process_item(file_queue, vault, port)
    except Exception as e:
        print(f"Error due to - {e}")
    finally:
        q.put(port)

def list_image_files(folder):
    return [str(path) for path in pathlib.Path(folder).rglob('*.png') | pathlib.Path(folder).rglob('*.jpg')]

if __name__ == "__main__":
    import sys

    folder = sys.argv[1]
    files = list_image_files(folder)

    output = "/Users/marvintaschenberger/Projects/DnD/item_reader/out/"
    process = []
    q = mp.Queue()
    ports = [11435, 11436, 11437, 11438, 11439, 11440, 11441, 11442]
    [q.put(i) for i in files]

    for port in ports:
        p = mp.Process(target=worker, args=(q, output, port))
        p.start()
        process.append(p)

    for p in process:
        p.join()

    print("Done")
