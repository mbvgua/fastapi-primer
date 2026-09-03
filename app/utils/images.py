"""
enable users to upload images within our application.
the profile picture will be uploaded usign form-data, processed with
PILLOW(resize, filetype conversion) and saved tothe database with a unique
filename.

contains the following methods:
    - process_profile_image
    - _get_s3_client
    - _upload_to_s3
    - _delete_from_s3
NOTE:
    - our fastapi app is async, but image processing is CPU bound. performing
      CPU bound operations in asyc functions are blocking, hence no other
      operation can be performed. to solve this, we'll define image procesing
      oparation in sync functions, and then call them with "run_in_threadpool()"
      from starlette which offloads them to a separate thread.
    - file images are now uploaded to amazon s3 buckets. this helps reduce size
      of application growth overtime for image/video intensive apps.
"""

import uuid
from io import BytesIO

from PIL import Image, ImageOps
import boto3
from starlette.concurrency import run_in_threadpool

from app.config import settings


def process_profile_image(content: bytes) -> tuple[bytes, str]:
    """
    basic image processing. process the imageas bytes using pillow, if not a
    valid image, pillow raises the Unidentified Image Error. this is performed
    with a context which allows for automatic cleanup on completion
    this returns only a filename
    """
    with Image.open(BytesIO(content)) as original:
        # handle orientation
        img = ImageOps.exif_transpose(original)

        # resizes image by cropping it for optimal fit, while retainig the
        # aspect ration. "LANCZOS" give high quality resampling
        img = ImageOps.fit(img, (300, 300), method=Image.Resampling.LANCZOS)

        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")

        # generate unique filename for image, thus preventing filename
        # collisions
        filename = f"{uuid.uuid4().hex}.jpg"

        # save to output object thats an in memory file
        # seek(0) returns it to the beginnig to allow it to be read
        output = BytesIO()
        img.save(output, "JPEG", quality=85, optimize=True)
        output.seek(0)

    return output.read(), filename


def _get_s3_client():
    """
    pass in our aws s3 credentials is they exist

    NOTE:
        - the leading underscore is a python convention denoting that it is
            a private helper
    """
    return boto3.client(
        "s3",
        region_name=settings.s3_region,
        aws_access_key_id=(
            settings.s3_access_key_id.get_secret_value()
            if settings.s3_access_key_id
            else None
        ),
        aws_secret_access_key=(
            settings.s3_secret_access_key.get_secret_value()
            if settings.s3_secret_access_key
            else None
        ),
        endpoint_url=settings.s3_endpoint_url,
    )


def _upload_to_s3(file_bytes: bytes, key: str) -> None:
    """
    upload processed images to s3 storage
    """
    s3 = _get_s3_client()
    s3.upload_fileobj(
        BytesIO(file_bytes),
        settings.s3_bucket_name,
        Key=key,
        ExtraArgs={"ContentType": "image/jpeg"},
    )


def _delete_from_s3(key: str) -> None:
    """
    delete processed images from s3 storage
    """
    s3 = _get_s3_client()
    s3.delete_object(Bucket=settings.s3_bucket_name, Key=key)


async def upload_profile_image(file_bytes: bytes, filename: str) -> None:
    """
    the _upload_to_s3 fucntion is blocking, hence we run it here async
    """
    key = f"profile_pics/{filename}"
    await run_in_threadpool(_upload_to_s3, file_bytes, key)


async def delete_profile_image(filename: str | None) -> None:
    """
    the _delete_from_s3 fucntion is blocking, hence we run it here async
    """
    if filename is None:
        return
    key = f"profile_pics/{filename}"
    await run_in_threadpool(_delete_from_s3, key)
