import glob
import os
import shutil
import sys 
from tqdm import tqdm

def copy_images(source, dest):
    # Location with subdirectories
   
    # Location to move images to
    if not os.path.isdir(dest):
        os.mkdir(dest)

    image_ext = ['jpg', 'jpeg', 'nef', 'png', 'cr2', 'pef']
    duplicate_files = dict()
    def get_index(fname):
        if fname not in duplicate_files.keys():
            duplicate_files[fname] = 0
        duplicate_files[fname] = duplicate_files[fname] + 1
        return duplicate_files[fname]

    # Get List of all images
    file_list = []
    processed_files = set()
    for ext in tqdm(image_ext):
        search_pattern = source + '**/*.' 
        for ch in ext: 
            up = ch.upper()
            low = ch.lower()
            search_pattern = search_pattern + '[' + low + up+']'
        print(search_pattern)
        files = glob.glob(search_pattern, recursive=True)
        print(f'ext {ext}: {len(files)}')
        file_list = file_list + files


        # # For each image
        for file in tqdm(files):
            # Get File name and extension
            filename = os.path.basename(file)
            if filename in processed_files:
                index = get_index(filename)
                ext_loc = filename.rfind('.')
                dest_file = filename[:ext_loc] + f'_{index}' + filename[ext_loc:]
            else:
                dest_file = filename
            processed_files.add(filename)
            
            # uncomment to copy files to destination
            # shutil.copy2(file, dest+dest_file)
            # uncomment to delete source files 
            # os.remove(file)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python3 move_images.py source_dir/ dest_dir/')
        sys.exit(1)
    copy_images(sys.argv[1], sys.argv[2])
