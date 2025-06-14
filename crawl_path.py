import retry
from PIL import Image
import ocr  # Assuming this is a module you have
import parser  # Assuming this is a module you have
import art_detector  # Assuming this is a module you have
import cropper  # Assuming this is a module you have
import md_builder  # Assuming this is a module you have
from typing import Optional
import multiprocessing as mp
import pathlib

@retry.retry(Exception, delay=2, tries=3)
def process_item(file_queue, vault, port):
    image_path = file_queue.get()
    try:
        # OCR
        text = ocr.extract_text(Image.open(image_path))

        # Parse item data
        item = parser.parse(text)

        # Artwork cropping
        bboxe = art_detector.detect(image_path)
        image_file: Optional[str] = None
        image_file = cropper.crop_save(image_path, bboxe, vault)

        # Generate Markdown
        md_path = md_builder.save(item, image_file)
        print(f"Markdown saved to {md_path}")
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

def worker(*args):
    file_queue = args[0]
    vault: str = args[1]
    port = args[2]
    try:
        process_item(file_queue, vault, port)
    except Exception as e:
        print(f"Error due to - {e}")
    finally:
        q.put(port)

def list_image_files(folder):
    return [str(path) for path in pathlib.Path(folder).rglob('*.png') | pathlib.Path(folder).rglob('*.jpg')]

if __name__ == "__main__":
    import sys

    folder = sys.argv[1]
    files = list_image_files(folder)

    output = "/Users/marvintaschenberger/Projects/DnD/item_reader/out/"
    process = []
    q = mp.Queue()
    ports = [11435, 11436, 11437, 11438, 11439, 11440, 11441, 11442]
    [q.put(i) for i in files]

    for port in ports:
        p = mp.Process(target=worker, args=(q, output, port))
        p.start()
        process.append(p)

    for p in process:
        p.join()

    print("Done")
