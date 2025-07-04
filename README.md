# Item Reader
**Product Description**

A pipeline that ingests fantasy RPG item screenshots (e.g. D\&D armor, weapons, potions), automatically extracts and structures their content into Obsidian-ready Markdown notes, and saves the associated artwork as individual image assets. Users will be able to drop batches of screenshots into a watched folder or upload them via CLI/API/UI, and receive back fully formatted Markdown files with embedded image links—ideal for organizing and searching a personal RPG item compendium.

---

## Requirements

### 1. Business Requirements

1. **Automated Ingestion**

   * Support bulk import of item screenshots.
   * Minimize manual tagging or correction.

2. **High-Quality Output**

   * Accurate OCR and text structuring into predefined Markdown schema.
   * Consistent naming conventions for files and image assets.

3. **Obsidian Compatibility**

   * Generate relative links to image assets.
   * Use frontmatter (YAML) for metadata (e.g. rarity, type, attunement).

4. **Extensibility & Integration**

   * Expose a CLI for power-users.
   * Provide a RESTful API for integration into other tools or workflows.
   * Optional lightweight web UI for occasional manual uploads and previews.

5. **Security & Privacy**

   * All processing can run entirely on local machines (no cloud upload required).
   * User data remains in their filesystem; no external storage by default.

---

### 2. Technical Requirements
| Category             | Requirement                                                                                                                                     | Implemented |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| **OCR Engine**       | - Use an open-source OCR (e.g. Tesseract) or commercial API configurable per user. <br>- Preprocess images for contrast, deskewing.             | [x]         |
| **Image Processing** | - Deskew and denoise images. <br>- Adjust contrast and scale images.                                                                           | [x]         |
| **Artwork Detection**| - Segment text vs. graphic areas. <br>- Crop and save artwork as separate images.                                                             | [x]         |
| **OCR Service**      | - Interface for OCR clients (abstract base class). <br>- Adapters for TesseractOCR / CloudOCR (configurable). <br>- Clean text artifacts, normalize whitespace. | [x]       |
| **LLM Parser**       | - Interface for parsers (single method `parse(raw_text) → ItemData`). <br>- Concrete ObsidianParser: calls LLM Studio API, validates JSON output.  | [x]         |
| **Domain Model**     | - Class `ItemData` with properties (`name`, `type`, `rarity`, `curse`, etc.). <br>- Value Objects for meaningful substructures (e.g., `Curse`, `StatBlock`). | [x]          |
| **Markdown Generator**| - Module `MarkdownBuilder`: generates YAML frontmatter + body + image embed. <br>- Templates for different item types.                          | [x]         |
| **File & Vault Management** | - Module `VaultManager`: creates paths (`Items/`, `Assets/`), file naming, conflict resolution. <br>- Module `ConfigManager`: loads/saves OCR, LLM, and path settings from config.yaml. | [x]         |
| **CLI Layer**        | - Module `CLI` (e.g., with Click or argparse). <br>- Commands: `ingest`, `preview`, `config set/get`, `serve-api`.                               | [ ]         |
| **REST API Layer**   | - Module `ApiServer` (e.g., FastAPI). <br>- Endpoints: `POST /items`, `GET /items`, `GET /items/{id}`, `DELETE /items/{id}`. <br>- Input validation, error handling, auth (optional). | [ ]         |
| **Logging & Error Handling** | - Central logging interface (`Logger`), configurable to file/console. <br>- Custom exception types (e.g., `OcrError`, `ParserError`, `FileSystemError`). | [x]      |
| **Testing & CI**     | - Unit tests for each module. <br>- Integration tests with sample images. <br>- Linting, type checking (mypy), pre-commit hooks.                  | [ ]         |

### 3. Interface Requirements

1. **CLI Interface**

   ```
   $ dnd-vault ingest --source ./screenshots --out ./vault
   $ dnd-vault preview --item shield_of_valor
   $ dnd-vault config set ocr.engine tesseract
   ```

2. **REST API**

   * **POST /items**

     * Request: `{"images": ["<base64-img1>", ...]}`
     * Response: `{"items": [{"id": "...", "markdown": "...", "imageFiles": ["shield.png", ...]}, ...]}`
   * **GET /items/{id}** → Markdown + metadata JSON.

3. **Web UI**

   * Drag-and-drop zone for screenshots.
   * Live preview panel showing generated Markdown.
   * “Download Vault” button to fetch generated files in ZIP.

4. **Obsidian Vault**

   * Each item → `<vault_root>/Items/<type>/<item_name>.md`
   * Images → `<vault_root>/Assets/<item_name>.<ext>`
   * Markdown example:

     ```markdown
     ---
     name: Armor of the Silent Scream
     type: Armor
     rarity: Rare
     attunement: true
     curse: true
     ---

     ![[../Assets/armor_of_the_silent_scream.png]]

     Armor of the Silent Scream is a supple leather armor...
     ```

---

## Roadmap

| Phase       | Deliverables                                                                                                                                                                 | Timeline  |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| **Phase 1** | • Prototype CLI ingestion pipeline<br>• Tesseract OCR + image preprocessing<br>• Simple LLM prompt for plain-text extraction<br>• Write Markdown files & save images locally | 2–3 weeks |
| **Phase 2** | • Refine OCR (deskew, denoise)<br>• Develop LLM-based parser to map text into YAML frontmatter + Markdown body<br>• Config file support<br>• Add unit/integration tests      | 3–4 weeks |
| **Phase 3** | • Build REST API server (Flask/FastAPI)<br>• Expose `POST /items` endpoint<br>• Error handling & logging                                                                     | 2–3 weeks |
| **Phase 4** | • Develop CLI wrapper around API<br>• Add `preview` and `config` commands<br>• Package as pip/npm module                                                                     | 2 weeks   |
| **Phase 5** | • Optional Web UI (React with file-upload, live Markdown preview)<br>• ZIP download feature<br>• Dockerize full stack                                                        | 4 weeks   |
| **Phase 6** | • Documentation (README, examples, troubleshooting)<br>• Release v1.0<br>• Gather user feedback & plan v2.0                                                                  | 2–3 weeks |

**Total estimated time:** \~4-5 months end-to-end (including buffer for iteration and bug-fixing).


### Functionalities

1. **Image Ingestion & Preprocessing**

   * Modul „ImageLoader“: Datei-Discovery, Batch-Import (Ordner, CLI-Globs)
   * Modul „Preprocessor“: Deskew, Denoise, Kontrastanpassung, Skalierung

2. **Artwork Extraction**

   * Modul „ArtDetector“: Segmentierung von Text- vs. Grafikbereich
   * Modul „Cropper“: Zuschneiden und Speichern der Artwork als eigenes Bild

3. **OCR-Service**

   * Interface „OCRClient“ (abstrakte Basisklasse)
   * Adapter „TesseractOCR“ / „CloudOCR“ (konfigurierbar)
   * Modul „TextCleaner“: Entfernen von Artefakten, Whitespace-Normalisierung

4. **LLM-Parser**

   * Interface „Parser“ (einzelne Methode `parse(raw_text) → ItemData`)
   * Concrete „ObsidianParser“: ruft LLM Studio API auf, validiert JSON-Output

5. **Domain Model & Datenstruktur**

   * Klasse `ItemData` mit Eigenschaften (`name`, `type`, `rarity`, `curse`, etc.)
   * Value Objects für sinnvolle Unterstrukturen (z. B. `Curse`, `StatBlock`)

6. **Markdown-Generator**

   * Modul „MarkdownBuilder“: erzeugt YAML-Frontmatter + Body + Image-Embed
   * Templates (Jinja2 o. Ä.) für verschiedene Item-Typen

7. **Datei- und Vault-Management**

   * Modul „VaultManager“: legt Pfade an (`Items/`, `Assets/`), Dateibenennung, Konfliktauflösung
   * Modul „ConfigManager“: lädt/speichert OCR-, LLM- und Pfad-Einstellungen aus config.yaml

8. **CLI-Schicht**

   * Modul „CLI“ (z. B. mit Click oder argparse)
   * Befehle: `ingest`, `preview`, `config set/get`, `serve-api`

9. **REST-API-Layer**

   * Modul „ApiServer“ (z. B. FastAPI)
   * Endpoints: `POST /items`, `GET /items`, `GET /items/{id}`, `DELETE /items/{id}`
   * Input-Validation, Error-Handling, Auth (optional)

10. **Logging & Fehlerbehandlung**

    * Zentrales Logging-Interface (`Logger`), konfigurierbar auf Datei/Console
    * Eigene Exception-Typen (z. B. `OcrError`, `ParserError`, `FileSystemError`)

11. **Testing & CI**

    * Unit-Tests für jedes Modul
    * Integrationstests mit Sample-Bildern
    * Linting, Typüberprüfung (mypy), Pre-Commit Hooks
---

### FlowChar (Mermaid)

```uml
@startuml Detailed_Workflow
actor User
participant CLI
participant API_Server as "API Server"
participant ImageLoader
participant Preprocessor
participant ArtDetector
participant OCRClient
participant Parser as "LLM Parser"
participant MarkdownBuilder
participant VaultManager

== Ingestion & Processing Sequence ==
User -> CLI : dnd-vault ingest --source <folder>
CLI -> ImageLoader : load_images(path)
ImageLoader -> Preprocessor : preprocess(images)
Preprocessor -> ArtDetector : detect_artwork_regions(images)
ArtDetector -> Preprocessor : return (art_crops, text_regions)
Preprocessor -> OCRClient : extract_text(text_regions)
OCRClient -> Parser : raw_text
Parser -> MarkdownBuilder : ItemData object
MarkdownBuilder -> VaultManager : save_markdown(itemData)
MarkdownBuilder -> VaultManager : save_images(art_crops)
VaultManager --> CLI : success & file paths
CLI --> User : "Ingestion complete"

== API Flow ==
User -> API_Server : POST /items { images }
API_Server -> ImageLoader : load_images(request.payload)
... -> Preprocessor : preprocess(...)
... -> ArtDetector
... -> OCRClient
... -> Parser
... -> MarkdownBuilder
... -> VaultManager
VaultManager --> API_Server : { items: [ { id, markdown, assets } ] }
API_Server --> User : JSON response

@enduml

@startuml Component_Interaction
package "Interfaces" {
  [CLI]
  [API Server]
}
package "Core Modules" {
  [ImageLoader]
  [Preprocessor]
  [ArtDetector]
  [OCRClient]
  [LLM Parser]
  [MarkdownBuilder]
  [VaultManager]
}

CLI --> ImageLoader : invoke load_images()
API Server --> ImageLoader : invoke load_images()
ImageLoader --> Preprocessor : send raw images
Preprocessor --> ArtDetector : request artwork detection
ArtDetector --> Preprocessor : return crops & regions
Preprocessor --> OCRClient : request text extraction
OCRClient --> LLM Parser : send OCR text
LLM Parser --> MarkdownBuilder : produce structured ItemData
MarkdownBuilder --> VaultManager : write files
VaultManager -> VaultManager : manage paths & conflicts

@enduml
```

---
