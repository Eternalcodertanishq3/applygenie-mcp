import base64
import io
from pathlib import Path
from PIL import Image

def encode_image_to_base64(image_path: str | Path) -> str:
    """Read an image file and return its base64 representation."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def compress_image(img: Image.Image, max_width: int = 1920, quality: int = 70) -> bytes:
    """Compress a PIL Image to JPEG bytes, scaling down if wider than max_width."""
    if img.width > max_width:
        ratio = max_width / img.width
        new_size = (max_width, int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    if img.mode != "RGB":
        img = img.convert("RGB")
        
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality)
    return buffer.getvalue()

def base64_to_image(b64: str) -> Image.Image:
    """Decode a base64 string to a PIL Image."""
    image_data = base64.b64decode(b64)
    return Image.open(io.BytesIO(image_data))

def image_to_base64_jpeg(img: Image.Image, quality: int = 70) -> str:
    """Convert a PIL Image to a base64 JPEG string."""
    jpeg_bytes = compress_image(img, quality=quality)
    return base64.b64encode(jpeg_bytes).decode("utf-8")
