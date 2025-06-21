# Project Title

## Description

This project aims to...

## Requirements

### 1. Functional Requirements

- ...

### 2. Technical Requirements

| Category             | Requirement                                                                                                                                     | Implemented |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| **OCR Engine**       | - Use an open-source OCR (e.g. Tesseract) or commercial API configurable per user. <br>- Preprocess images for contrast, deskewing.             | [ ]         |
| **Image Processing** | - Deskew and denoise images. <br>- Adjust contrast and scale images.                                                                           | [ ]         |
| **Artwork Detection**| - Segment text vs. graphic areas. <br>- Crop and save artwork as separate images.                                                             | [ ]         |
| **OCR Service**      | - Interface for OCR clients (abstract base class). <br>- Adapters for TesseractOCR / CloudOCR (configurable). <br>- Clean text artifacts, normalize whitespace. | [ ]         |
| **LLM Parser**       | - Interface for parsers (single method `parse(raw_text) → ItemData`). <br>- Concrete ObsidianParser: calls LLM Studio API, validates JSON output.  | [ ]         |
| **Domain Model**     | - Class `ItemData` with properties (`name`, `type`, `rarity`, `curse`, etc.). <br>- Value Objects for meaningful substructures (e.g., `Curse`, `StatBlock`). | [ ]         |
| **Markdown Generator**| - Module `MarkdownBuilder`: generates YAML frontmatter + body + image embed. <br>- Templates for different item types.                          | [ ]         |
| **File & Vault Management** | - Module `VaultManager`: creates paths (`Items/`, `Assets/`), file naming, conflict resolution. <br>- Module `ConfigManager`: loads/saves OCR, LLM, and path settings from config.yaml. | [ ]         |
| **CLI Layer**        | - Module `CLI` (e.g., with Click or argparse). <br>- Commands: `ingest`, `preview`, `config set/get`, `serve-api`.                               | [ ]         |
| **REST API Layer**   | - Module `ApiServer` (e.g., FastAPI). <br>- Endpoints: `POST /items`, `GET /items`, `GET /items/{id}`, `DELETE /items/{id}`. <br>- Input validation, error handling, auth (optional). | [ ]         |
| **Logging & Error Handling** | - Central logging interface (`Logger`), configurable to file/console. <br>- Custom exception types (e.g., `OcrError`, `ParserError`, `FileSystemError`). | [ ]         |
| **Testing & CI**     | - Unit tests for each module. <br>- Integration tests with sample images. <br>- Linting, type checking (mypy), pre-commit hooks.                  | [ ]         |
| **Utilities & Common Components** | - Module `Utils` for common helpers (e.g., path operations, string sanitizer). <br>- Constant definitions (supported item types, default prompt templates). | [ ]         |

## Installation

- ...

## Usage

- ...
