from abc import abstractmethod
from typing import Protocol, runtime_checkable, List

from .models import ItemData, BoundingBox

@runtime_checkable
class OCRProtocol(Protocol):
    @abstractmethod
    def extract_text(self, image_path: str) -> str:
        ...

@runtime_checkable
class LLMServerProtocol(Protocol):
    @abstractmethod
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        ...

@runtime_checkable
class ParserProtocol(Protocol):
    @abstractmethod
    def parse(self, raw_text: str) -> ItemData:
        ...


@runtime_checkable
class ArtDetectorProtocol(Protocol):
    def detect_artwork_regions(self, image_path: str) -> List[BoundingBox]:
        """
        Analyze the image and return bounding boxes for artwork regions.
        """
        ...

@runtime_checkable
class CropperProtocol(Protocol):
    def crop_and_save(
        self,
        image_path: str,
        region: BoundingBox,
        output_path: str
    ) -> str:
        """
        Crop the given region from image_path and save to output_path.
        Returns the path of the saved crop.
        """
        ...