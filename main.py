from rembg import remove
from PIL import Image, ImageFilter
import io
import os

def resize_image(image, max_size=2048):
    """Resize the image if its width or height is greater than max_size."""
    width, height = image.size
    if width > max_size or height > max_size:
        # Maintain aspect ratio
        aspect_ratio = width / height
        if aspect_ratio > 1:
            new_width = max_size
            new_height = int(max_size / aspect_ratio)
        else:
            new_height = max_size
            new_width = int(max_size * aspect_ratio)
        resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)
        return resized_image
    return image

def remove_background_and_crop(input_path, output_path, padding=20):
    # Load the image with Rembg and remove the background
    with open(input_path, 'rb') as f:
        input_image = f.read()
    output_image = remove(input_image)
    
    # Convert the output to a PIL image
    output_pil_image = Image.open(io.BytesIO(output_image)).convert("RGBA")

    # Get the bounding box of the non-transparent part
    bbox = output_pil_image.getbbox()

    # Add padding to the bounding box
    x0, y0, x1, y1 = bbox
    x0 = max(0, x0 - padding)
    y0 = max(0, y0 - padding)
    x1 = min(output_pil_image.width, x1 + padding)
    y1 = min(output_pil_image.height, y1 + padding)

    # Crop the image with the padding
    cropped_image = output_pil_image.crop((x0, y0, x1, y1))

    # Resize the image if necessary
    resized_cropped_image = resize_image(cropped_image)

    # Create a new mask with blurred edges
    alpha = cropped_image.split()[3] 
    blurred_alpha = alpha.filter(ImageFilter.GaussianBlur(10))

    # Combine the blurred alpha channel back with the image resized_cropped_image.putalpha(blurred_alpha)
    resized_cropped_image.putalpha(blurred_alpha)

    # Save the cropped image with transparency
    resized_cropped_image.save(output_path, format="PNG")

def process_folder(input_folder, output_folder, padding=20):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + '_altered.png')
            remove_background_and_crop(input_path, output_path, padding)

# Example usage
input_folder = 'input_images'
output_folder = 'output_images'
process_folder(input_folder, output_folder)
