import glob
from PIL import Image

photo_files_source = "<absolute-path-to-photo-folder>"

photo_files_dest = "<absolute-path-to-destination>"

jpg_file_list = glob.glob(photo_files_source + "*.jpg")
# png_file_list = glob.glob(photo_files_source + "*.png")
# jpeg_file_list = glob.glob(photo_files_source + "*.png")


def convert_jpg():
    for item in jpg_file_list:
        item_name_without_tag = item.split(".")[-2]
        item_name = item_name_without_tag.split("/")[-1]
        im = Image.open(item).convert("RGB")
        webp_name = photo_files_dest + item_name + ".webp"
        print(webp_name)
        im.save(webp_name, "webp")