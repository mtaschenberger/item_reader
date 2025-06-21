import os
import re
from typing import Optional
from item_extractor.models import ItemData
from item_extractor.logger import logger

class MarkdownBuilder:
    """
    Builds and saves Markdown files for ItemData instances.
    """
    def __init__(self, vault_root: str = "./vault") -> None:
        self.vault_root = vault_root
        logger.info("MarkdownBuilder initialized - {vault_root}", vault_root=vault_root)

    def _sanitize_name(self, name: str) -> str:
        # Lowercase, replace non-alphanumeric with underscore
        sanitized = re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_").lower()
        return sanitized

    def build(self, item: ItemData, image_filename: Optional[str] = None) -> str:
        """
        Construct the Markdown content for the given item.
        """
        frontmatter = ["---"]
        frontmatter.append(f"Category: \"[[Items]]\"")
        # Derive subcategory from type, e.g. 'armor', 'weapon', etc.
        subcat = item.type.split("(")[0].strip().capitalize()
        frontmatter.append(f"SubCategory: \"[[{subcat}]]\"")
        frontmatter.append(f"Rarity: \"[[{item.rarity.capitalize()}]]\"")
        attune = "yes" if item.attunement else "no"
        frontmatter.append(f"Requires Attunement: {attune}")
        cursed = "yes" if item.curse else "no"
        frontmatter.append(f"Cursed: {cursed}")
        frontmatter.append("---\n")

        lines = frontmatter

        if image_filename:
            # relative path from markdown to assets
            rel_path = os.path.relpath(image_filename, start=os.path.dirname(self._get_md_path(item)))
            lines.append(f"![[{rel_path}]] \n")
        lines.append(item.description.strip() + "\n")

        if item.curse:
            # Include curse description as blockquote
            lines.append("#### Curse \n" + item.curse.strip() + "")



        return "\n".join(lines)

    def _get_md_path(self, item: ItemData) -> str:
        # Create path: vault_root/Items/<subcategory>/<filename>.md
        subcat = item.type.split("(")[0].strip().lower()
        dir_path = os.path.join(self.vault_root, "Items", subcat)
        os.makedirs(dir_path, exist_ok=True)
        filename = self._sanitize_name(item.name) + ".md"
        return os.path.join(dir_path, filename)

    def save(self, item: ItemData, image_filename: Optional[str] = None) -> str:
        """
        Build and write the Markdown file, returning its filepath.
        """
        md_path = self._get_md_path(item)
        content = self.build(item, image_filename)
        with open(md_path, "w", encoding="utf-8") as md_file:
            md_file.write(content)
        logger.info("Saved markdown - {path}", path=md_path)
        return md_path