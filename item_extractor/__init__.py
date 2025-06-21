
import pathlib
import multiprocessing as mp 
from typing import Optional
import traceback

from PIL import Image
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
and the cycle begins anew, forcing you to continue
making Wisdom saving throws for every 5
increments as before.

‘The curse can only be lifted ifthe armor is submerged
in holy water for 24 hours while a cleric or paladin of
‘9th level or higher performs a cleansing ritual

“Tue Fonsworn
Bastion

###### Output ###########

{ "name": "Forsworn Bastion", "description": "Armor (plate), very rare (requires attunement by a Paladin)\n\nForsworn Bastion is a suit of plate armor forged from jagged, blackened steel that seems to absorb light. Crimson runes pulse faintly across its surface, and a cold mist rises from the joints. Etched into the chestplate are the ominous words, 'Strength I claimed, not given. Prove your dominance, or be consumed.'\n\nWhile wearing this armor, you gain a +2 bonus to AC and resistance to necrotic damage. Additionally, you can add your Charisma modifier to your Strength saving throws.", "rarity": "Very Rare", "attunement": true, "attunement_condition": "Paladin", "curse": "The armor is haunted by the spirit of a fallen paladin who abandoned their oath for power. It constantly urges you to prove your strength through relentless violence.\n\n+ Possession Counter: The counter starts at 0. Each time you take damage, increase it by 1. When the counter reaches 5, you must make a DC 12 Wisdom saving throw. Every additional 5 points (10, 15, etc.), you must repeat the save, with the DC increasing by 2 each time. On a failure—or if the counter reaches 20—you become possessed.\n\n+ Possession: While possessed, the spirit fully takes over your body for 1 minute, forcing you to attack the nearest creature (ally or enemy) on each of your turns. You remain aware of your actions but cannot resist them.\n\n+ After the Possession Ends: The counter resets to 0, and the cycle begins anew, forcing you to continue making Wisdom saving throws for every 5 increments as before.\n\nThe curse can only be lifted if the armor is submerged in holy water for 24 hours while a cleric or paladin of 9th level or higher performs a cleansing ritual.", "subtype": "PLATE", "dex_bonus": "NONE", "strength_req": "15", "stealth_option": "DIS" }

########### End Example ########### 

########### Input ###########
"""


@retry.retry(tries=3)
def process_item(image_path: pathlib.Path, vault_root: pathlib.Path, port: int = 11434) -> None:
    # Initialize components
    ocr: OCRProtocol = TesseractOCR(lang="eng")
    llm_client: LLMServerProtocol = LMStudioClient(
        endpoint=f"http://localhost:{port}",
         model= "qwen3:1.7b"         
        )
    parser: ParserProtocol = ItemParser(llm_client=llm_client,
                                        system_prompt=SYSTEM_PROMPT,)
    art_detector: ArtDetectorProtocol = ArtworkDetector()
    cropper: CropperProtocol = PILCropper()
    md_builder = MarkdownBuilder(vault_root=vault_root)

    # OCR
    text = ocr.extract_text(Image.open(image_path))

    # Parse item data
    item = parser.parse(text)

    # Artwork cropping
    bboxe = art_detector.detect(image_path)
    image_file: Optional[str] = None
    image_file = cropper.crop_save(image_path, bboxe, vault_root)

    # Generate Markdown
    md_path = md_builder.save(item, image_file)
    print(f"Markdown saved to {md_path}")

def move_file(file_path: pathlib.Path, target_folder):                                                                                                                                                                                                                                                                     
    try:
        file_path.rename(target_folder / file_path.name)                                                                                                                                                                                                                                     
    except Exception as e:                                                                                                                                                                                                                                                                                   
        print(f"Failed to move {file_path} to {target_folder}: {e}") 


def worker(file_queue, vault, port):
    while not file_queue.empty():
        try:
            file: pathlib.Path = file_queue.get()
            process_item(file, vault, port)
            move_file(file, pathlib.Path("success"))   
        except mp.queues.Empty:                                                                                                                                                                                                                                                                              
            break  
        except Exception as e:
            print(f"Error due to - {e}")
            print(traceback.format_exc())
            move_file(file, pathlib.Path("error"))  


def list_image_files(folder):
    images = [path for path in pathlib.Path(folder).rglob('*.png')]
    images.extend([path for path in pathlib.Path(folder).rglob('*.jpg')])
    return images
