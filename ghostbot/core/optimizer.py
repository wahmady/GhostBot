"""
GhostBot Image Optimizer

Handles image resizing and compression for optimal token usage with GPT-4o.
"""

import base64
import io
from pathlib import Path
from typing import Union

from PIL import Image


def encode_image(
    image_path: Union[str, Path],
    max_size: int = 1024,
    quality: int = 85,
) -> str:
    """
    Optimize and encode an image for GPT-4o vision API.

    Opens the image, resizes it so the longest side is at most max_size pixels,
    compresses it as JPEG, and returns a base64-encoded string.

    Args:
        image_path: Path to the image file.
        max_size: Maximum dimension (width or height) in pixels. Default 1024.
        quality: JPEG compression quality (1-100). Default 85.

    Returns:
        Base64-encoded string of the optimized image.

    Raises:
        FileNotFoundError: If the image file doesn't exist.
        PIL.UnidentifiedImageError: If the file is not a valid image.
    """
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    with Image.open(image_path) as img:
        # Convert to RGB if necessary (handles PNG with transparency, etc.)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Calculate new dimensions preserving aspect ratio
        width, height = img.size
        if width > height:
            if width > max_size:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_width, new_height = width, height
        else:
            if height > max_size:
                new_height = max_size
                new_width = int(width * (max_size / height))
            else:
                new_width, new_height = width, height

        # Resize if needed
        if (new_width, new_height) != (width, height):
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Compress to JPEG and encode
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        buffer.seek(0)

        return base64.b64encode(buffer.read()).decode("utf-8")


def get_image_dimensions(image_path: Union[str, Path]) -> tuple[int, int]:
    """
    Get the dimensions of an image without fully loading it.

    Args:
        image_path: Path to the image file.

    Returns:
        Tuple of (width, height).
    """
    with Image.open(image_path) as img:
        return img.size
