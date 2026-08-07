"""
enable users to upload images within our application.
the profile picture will be uploaded usign form-data, processed with
PILLOW(resize, filetype conversion) and saved tothe database with a unique
filename.

NOTE:
    - our fastapi app is async, but image processing is CPU bound. performing
      CPU bound operations in asyc functions are blocking, hence no other
      operation can be performed. to solve this, we'll define image procesing
      oparation in sync functions, and then call them with "run_in_threadpool()"
      from starlette which offloads them to a separate thread.
"""

import uuid
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps

PROFILE_PICS_DIR = Path("media/profile_pics")


class ImageUtils:
    """
    actions perfomed on images, has two methods:
        - process_profile_image
        - delete_profile_image
    """

    @staticmethod
    def process_profile_image(content: bytes) -> str:
        """
        basic image processing. process the imageas bytes using pillow, if not a
        valid image, pillow raises the Unidentified Image Error. this is performed
        with a context which allows for automatic cleanup on completion
        this returns only a filename, which is what is stored in our database
        """
        with Image.open(BytesIO(content)) as original:
            # handle orientation
            img = ImageOps.exif_transpose(original)

            # resizes image by cropping it for optimal fit, while retainig the
            # aspect ration. "LANCZOS" give high quality resampling
            img = ImageOps.fit(img, (300, 300), method=Image.Resampling.LANCZOS)

            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGBA")

            # generate unique filename for image, thus preventing filename
            # collisions
            filename = f"{uuid.uuid4().hex}.jpg"
            filepath = PROFILE_PICS_DIR / filename

            # create directory if it doesnt exists. else procedd
            PROFILE_PICS_DIR.mkdir(parents=True, exist_ok=True)

            img.save(filepath, "JPEG", quality=85, optimize=True)

        return filename

    @staticmethod
    def delete_profile_image(filename: str | None) -> None:
        """
        essential when users upload a new profile_pic to replace their old one,
        or delete their account entirely
        """
        # if no filename passed, exit early
        if filename is None:
            return

        # else delete the filename passed in
        filepath = PROFILE_PICS_DIR / filename
        if filepath.exists():
            filepath.unlink()
