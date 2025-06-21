import sys 
import multiprocessing as mp 
import pathlib 

import typer

from item_extractor import process_item, list_image_files, worker


app = typer.Typer()

@app.command("file")
def main(file: str,
         output_dir: str = "out"):
    
    
    file = pathlib.Path(file) 
    output = pathlib.Path(__file__)/ output_dir
    port = 11434

    process_item(file, output, port)
    print("Done")

@app.command("folder")
def crawl_folder(folder: str,
                 output_dir: str = "out"):
    
    files = list_image_files(folder)

    output = pathlib.Path(__file__)/ output_dir
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

if __name__ == "__main__":
    main()