import base64
import os

from io import BytesIO
from PIL import Image

def get_images_path():
    return os.path.join(os.getcwd(), 'static', 'images')

def get_rms_default_image():
    image_path = os.path.join(get_images_path(), 'RSM_Logo_002.jpg')
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        base64_string = encoded_string.decode('utf-8')
        return base64_string

def pillow_image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_bytes   = buffered.getvalue()
    img_base64  = base64.b64encode(img_bytes)
    return img_base64.decode('utf-8')


def correctImageOrientation(imagePath):
    oldFilePath = os.path.split(imagePath)[0]
    newFilePath = os.path.join(oldFilePath, "studentImage.jpg")
    try:
        with Image.open(imagePath) as img:
            exif = img.getexif()
            orientation = exif.get(0x0112, 1)
            if orientation == 3:
                img = img.rotate(180, expand=True)
            elif orientation == 6:
                img = img.rotate(270, expand=True)
            elif orientation == 8:
                img = img.rotate(90, expand=True)
            img.save(newFilePath)
            max_size = (300, 300)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.close()
    except Exception as e:
        print(f"Error processing image {imagePath}: {e}")
    return newFilePath

def showImageProperties(imagePath):
    img = Image.open(imagePath)

    # Access properties
    print(f"-------------------------------------")
    print(f"Filename: {img.filename}")
    print(f"Format:   {img.format}")  # e.g., JPEG, PNG, GIF
    print(f"Size:     {img.size}")  # (width, height) tuple in pixels
    print(f"Width:    {img.width}")  # Width in pixels
    print(f"Height:   {img.height}")  # Height in pixels
    print(f"Mode:     {img.mode}")