import io
import json
from typing import Optional

from item_extractor.protocols import ParserProtocol, LLMServerProtocol
from item_extractor.models import ItemData, Curse
from item_extractor.logger import logger

class ItemParser(ParserProtocol):
    def __init__(self, llm_client: LLMServerProtocol, system_prompt: str) -> None:
        self.llm_client = llm_client
        self.system_prompt = system_prompt
        logger.info("ItemParser initialized - {system_prompt}", system_prompt=self.system_prompt)

    def parse(self, raw_text: str) -> ItemData:
        logger.info("{step} | Start - {raw}", step="Parse", raw= raw_text)
        content = self.llm_client.chat(self.system_prompt, raw_text)
        # Remove any inner thought markup
        json_text = content.split(r"</think>")[-1].strip()
        try:
            parsed = json.load(io.StringIO(json_text))
        except json.JSONDecodeError as e:
            logger.error("JSON decode failed due -  {e}", error=str(e))
            logger.error("JSON decode failed at - {json_text}", json_text=json_text)
            raise
        logger.info("{step} | JSON decoded", step="Parse")
        curse_data = parsed.get('curse', None) 

        if type(curse_data) == dict and curse_data.get("description"):
            curse = curse_data.get("description", None)
        elif type(curse_data) == dict:
            curse = "\n".join([f"\n **{key}** \n\n {value} " for key, value in curse_data.items()])
        elif type(curse_data) == str:
            curse = curse_data
        else:
            curse = None 

        item = ItemData(
            name=parsed['name'],
            type=parsed['subtype'],
            rarity=parsed['rarity'],
            attunement=parsed.get('attunement', False),
            curse=curse,
            description=parsed['description'],
            image_path=None,
        )
        logger.info("{step} | ItemData parsed - {name}", name=item.name, step="Pars")
        return item