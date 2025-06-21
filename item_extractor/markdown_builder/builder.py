from pathlib import Path
import os
import re
import typing

from jinja2 import Environment, FileSystemLoader, select_autoescape

from item_extractor.models import ItemData
from item_extractor.logger import logger

class MarkdownBuilder:
    def __init__(self, vault_root: str = "./vault") -> None:
        self.vault_root = vault_root
        # assume you have a `templates/` directory next to this file
        self.env = Environment(
            loader=FileSystemLoader(str(Path(__file__).parent)),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.template = self.env.get_template("template.j2.md")
        logger.info("MarkdownBuilder initialized - {vault_root}", vault_root=vault_root)

    def _sanitize_name(self, name: str) -> str:
        return re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_").lower()

    def _get_md_path(self, item: ItemData) -> str:
        subcat = item.type.split("(")[0].strip().lower()
        dir_path = os.path.join(self.vault_root, "Items", subcat)
        os.makedirs(dir_path, exist_ok=True)
        filename = self._sanitize_name(item.name) + ".md"
        return os.path.join(dir_path, filename)

    def save(self, item: ItemData, image_filename: typing.Optional[str] = None) -> str:
        md_path = self._get_md_path(item)

        # derive the same “subcategory” you did before
        subcategory = item.type.split("(")[0].strip().capitalize()

        # compute a relative path for the image, if any
        image_relpath = None
        if image_filename:
            image_relpath = os.path.relpath(
                image_filename,
                start=os.path.dirname(md_path),
            )

        # render the template
        content = self.template.render(
            item=item,
            subcategory=subcategory,
            image_relpath=image_relpath,
        )

        with open(md_path, "w", encoding="utf-8") as md_file:
            md_file.write(content)
        logger.info("Saved markdown - {path}", path=md_path)
        return md_path
