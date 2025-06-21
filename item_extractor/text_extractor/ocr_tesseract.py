from PIL import Image, ImageOps
from pytesseract import image_to_string

from item_extractor.protocols import OCRProtocol
from item_extractor.logger import logger

class TesseractOCR:
    def __init__(self, lang: str = 'eng') -> None:
        self.lang = lang
        logger.info("Initialized TesseractOCR - {lang}", lang=self.lang)

    def extract_text(self, image: Image.Image) -> str:
        # Beispiel Preprocessing: invert + enhance contrast
        img = ImageOps.grayscale(image)
        img = ImageOps.invert(img)
        text = image_to_string(img, lang=self.lang)
        logger.debug("OCR extracted - {text}", text=text)
        return text