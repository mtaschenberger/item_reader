import niquests
from typing import Dict

import lmstudio as lms
from item_extractor.logger import logger
from item_extractor.protocols import LLMServerProtocol

class LMStudioClient(LLMServerProtocol):
    def __init__(
        self,
        endpoint: str,
        model: str = 'qwen3-30b-a3b',
    ) -> None:
        self.endpoint = endpoint.rstrip('/')
        self.model = model
        logger.info("LLMStudioClient initialized - {model} ; {endpoint}", endpoint=self.endpoint, model=self.model)

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        payload: Dict[str, object] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "max_tokens": -1,
            "stream": False,
        }
        headers = {"Content-Type": "application/json"}
        url = f"{self.endpoint}/v1/chat/completions"
        resp = niquests.post(url, json=payload, headers=headers, timeout=60*5)
        resp.raise_for_status()
        data = resp.json()
        logger.debug("{step} | LLMStudio chat {response}", response=data, step="chat")
        choices = data.get('choices', [])
        if not choices or 'message' not in choices[0]:
            logger.error("Unexpected chat response structure", data=data)
            raise ValueError("Invalid LLM response")
        content = choices[0]['message']['content']

        logger.info("{step} | Return: {content}", content=content , step="chat")
        return content
    
    def item_question(self, image_path: str, query: str):
        
        image_handle = lms.prepare_image(image_path)
        model = lms.llm("gemma-3-4b-it-qat")
        chat = lms.Chat()
        chat.add_user_message(query, images=[image_handle])
        prediction = model.respond(chat)
        print(prediction)




query = """
### Instructions
You are an OCR Agent - you are reading the text on the Image of a DnD Item description and return it with correction or guessing if necessary
You Will analyze the image an return the following properties: 
### Expect Output
Name of the Item: 
---
Description of the Item: 
---
Item Type: <Armor | Weapons | miscellaneous> 
---
Description: 
---
Curse: <description of the Curse if applicable> 
---
Text Only: < yes | no - whether there is only text in the image or a visual representation

### End Expected Output 
Input:
""" 