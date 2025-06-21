import os
import uuid
from PIL import Image
from typing import Optional

from item_extractor.protocols import CropperProtocol
from item_extractor.models import BoundingBox



class PILCropper(CropperProtocol):
    """
    Crops regions from an image and returns the PIL Image object.
    Use _save() to persist the image to disk.
    """
    def crop(
        self,
        image_path: str,
        region: BoundingBox,
    ) -> Image.Image:
        img = Image.open(image_path)
        crop_img = img.crop((region.left, region.upper, region.right, region.lower))
       
        return crop_img

    def _save(
        self,
        crop_img: Image.Image,
        output_dir: str,
        prefix: Optional[str] = None,
    ) -> str:
        os.makedirs(output_dir, exist_ok=True)
        base = prefix or str(uuid.uuid4())
        output_path = os.path.join(output_dir, f"{base}.png")
        crop_img.save(output_path)

        return output_path
    
    def crop_save(
        self,
        image_path: str,
        region: BoundingBox,
        output_dir: str,
        prefix: Optional[str] = None,
    )-> str:
        cropped = self.crop(image_path, region)
        return self._save(cropped, output_dir, prefix)