import enum
import os
import shutil
import logging
import boto3
from botocore.exceptions import ClientError


# Set up Django logger
logger = logging.getLogger(__name__)


def s3_save_strategy(filepath_list, catalogue_name):
    """Function to save files to S3."""
    logger.info("Saving to S3")
    logger.debug(f"Filepath list: {filepath_list}")

    s3_endpoint_url = os.environ.get("S3_ENDPOINT_URL")
    s3_access_key_id = os.environ.get("S3_ACCESS_KEY_ID")
    s3_secret_access_key = os.environ.get("S3_SECRET_ACCESS_KEY")
    s3_region = os.environ.get("S3_REGION")
    s3_verify_certificate = not os.getenv(
        "S3_SELF_SIGNED_CERTIFICATE", "False"
    ).lower() in ["true", "1", "t", "yes", "y"]
    bucket_prefix = os.environ.get("CATALOGUE_PREFIX", "")

    bucket_name = f"{bucket_prefix}{catalogue_name}"
    if not s3_access_key_id or not s3_secret_access_key or not bucket_name:
        error_message = "Missing S3 credentials or S3 bucket name."
        logger.error(error_message)
        return {"success": False, "error": error_message}

    try:
        s3_client = boto3.client(
            "s3",
            endpoint_url=s3_endpoint_url,
            region_name=s3_region,
            aws_access_key_id=s3_access_key_id,
            aws_secret_access_key=s3_secret_access_key,
            verify=s3_verify_certificate,
        )
        if (
            s3_client.head_bucket(Bucket=bucket_name)["ResponseMetadata"][
                "HTTPStatusCode"
            ]
            != 200
        ):
            s3_client.create_bucket(Bucket=bucket_name)
            logger.info(f"Created bucket {bucket_name}")
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            s3_client.create_bucket(Bucket=bucket_name)
            logger.info(f"Created bucket {bucket_name}")
        else:
            error_message = f"Error accessing or creating bucket {bucket_name}: {e}"
            logger.error(error_message)
            return {"success": False, "error": error_message}
    except Exception as e:
        error_message = f"Error creating S3 client: {e}"
        logger.error(error_message)
        return {"success": False, "error": error_message}

    errors = []
    for filepath in filepath_list:
        logger.debug(f"Processing file: {filepath}")
        try:
            filename = os.path.basename(filepath)
            s3_client.upload_file(filepath, bucket_name, filename)
            logger.info(f"Uploaded {filename} to S3 bucket {bucket_name}.")
        except ClientError as e:
            error_message = f"Failed to upload {filepath} to S3: {e}"
            logger.error(error_message)
            errors.append(error_message)
        except FileNotFoundError:
            error_message = f"File not found: {filepath}"
            logger.error(error_message)
            errors.append(error_message)
        except Exception as e:
            error_message = f"Error uploading {filepath} to S3: {e}"
            logger.error(error_message)
            errors.append(error_message)

    if not errors:
        for filepath in filepath_list:
            try:
                os.remove(filepath)
                logger.info(f"Deleted local file {filepath}.")
            except Exception as e:
                error_message = f"Error deleting file {filepath}: {e}"
                logger.error(error_message)
        return {"success": True}
    else:
        return {"success": False, "errors": errors}


def local_filesystem_save_strategy(filepath_list, catalogue_name):
    """Function to save files to the local filesystem, using catalogue_name for directory names."""
    logger.info("Saving to local filesystem")

    base_path = os.environ.get("FILESYSTEM_DESTINATION_PATH")

    if not base_path:
        error_message = "Missing FILESYSTEM_DESTINATION_PATH environment variable."
        logger.error(error_message)
        return {"success": False, "error": error_message}
    directory_prefix = os.environ.get("CATALOGUE_PREFIX", "")

    directory_name = f"{directory_prefix}{catalogue_name}"
    destination_path = os.path.join(base_path, directory_name)

    if not os.path.isdir(destination_path):
        try:
            os.makedirs(destination_path)
            logger.info(f"Created directory {destination_path}")
        except Exception as e:
            error_message = f"Failed to create directory {destination_path}: {e}"
            logger.error(error_message)
            return {"success": False, "error": error_message}

    errors = []
    for filepath in filepath_list:
        try:
            filename = os.path.basename(filepath)
            dest_file_path = os.path.join(destination_path, filename)
            shutil.copy2(filepath, dest_file_path)
            logger.info(f"Copied {filename} to {destination_path}")
        except FileNotFoundError:
            error_message = f"File not found: {filepath}"
            logger.error(error_message)
            errors.append(error_message)
        except Exception as e:
            error_message = f"Error copying {filepath} to {destination_path}: {e}"
            logger.error(error_message)
            errors.append(error_message)

    if not errors:
        for filepath in filepath_list:
            try:
                os.remove(filepath)
                logger.info(f"Deleted local file {filepath}.")
            except Exception as e:
                error_message = f"Error deleting file {filepath}: {e}"
                logger.error(error_message)
        return {"success": True}
    else:
        return {"success": False, "errors": errors}


class MediaSaveStrategies(enum.Enum):
    S3_SAVE = (
        "s3_save",
        "Saves file to the s3 instance.",
        s3_save_strategy,
    )
    LOCAL_FILESYSTEM = (
        "LOCAL_FILESYSTEM_SAVE",
        "Saves files to the local filesystem.",
        local_filesystem_save_strategy,
    )

    def __new__(cls, value, description, strategy_function):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        obj.strategy_function = strategy_function
        return obj

    @classmethod
    def choices(cls):
        return [(key.value, key.description) for key in cls]

    @classmethod
    def get_strategy_function(cls, value):
        """Retrieve the appropriate save strategy function."""
        for item in cls:
            if item.value == value:
                return item.strategy_function
        raise ValueError(f"No strategy function found for value: {value}")
