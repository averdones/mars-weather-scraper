from pathlib import Path
import boto3
from typing import IO


def upload_file_to_s3(local_file_path: str, bucket_name: str, s3_file_name: str = None, s3_folder : str = None) -> None:
    """Uploads a file to AWS S3.

    Args:
        local_file_path: Path to the local file to upload.
        bucket_name: Name of the bucket to upload to.
        s3_file: Name with which the file will be saved in S3. If not provided, the name of the local file is used.
        s3_folder: S3 folder where the file will be saved. If not specified then the file will be saved in the root
            of the bucket.

    """
    if s3_file_name is None:
        s3_file_name = Path(local_file_path).name

    if s3_folder is not None:
        s3_file_name = f"{s3_folder}/{s3_file_name}"

    s3 = boto3.resource("s3")
    s3.meta.client.upload_file(local_file_path, bucket_name, s3_file_name)


def upload_object_to_s3(obj: IO[bytes], bucket_name: str, s3_file_name: str, s3_folder: str = None) -> None:
    """Uploads a string to AWS S3.

    Args:
        obj: In-memory bytes IO object.
        bucket_name: Name of the bucket to upload to.
        s3_file: Name with which the file will be saved in S3.
        s3_folder: S3 folder where the file will be saved. If not specified then the file will be saved in the root
            of the bucket.

    """
    if s3_folder is not None:
        s3_file_name = f"{s3_folder}/{s3_file_name}"

    s3 = boto3.resource("s3")
    s3.meta.client.upload_fileobj(obj, bucket_name, s3_file_name)
