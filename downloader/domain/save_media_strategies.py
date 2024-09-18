import enum
import os
import shutil
import boto3
from botocore.exceptions import ClientError


def s3_save_strategy(filepath_list, catalogue_name):
    """Function to save files to S3."""
    print("Saving to S3")

    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    aws_session_token = os.environ.get("AWS_SESSION_TOKEN")  # Optional
    s3_bucket = os.environ.get("S3_BUCKET")
    s3_region = os.environ.get("AWS_REGION", "us-east-1")
    bucket_prefix = os.environ.get("CATALOGUE_PREFIX", "")

    bucket_name = f"{bucket_prefix}{catalogue_name}"
    if not aws_access_key_id or not aws_secret_access_key or not s3_bucket:
        error_message = "Missing AWS credentials or S3 bucket environment variables."
        print(error_message)
        return {"success": False, "error": error_message}

    try:
        s3_client = boto3.client(
            "s3",
            region_name=s3_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
        )
        if (
            s3_client.head_bucket(Bucket=bucket_name)["ResponseMetadata"][
                "HTTPStatusCode"
            ]
            != 200
        ):
            s3_client.create_bucket(Bucket=bucket_name)
            print(f"Created bucket {bucket_name}")
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            s3_client.create_bucket(Bucket=bucket_name)
            print(f"Created bucket {bucket_name}")
        else:
            error_message = f"Error accessing or creating bucket {bucket_name}: {e}"
            print(error_message)
            return {"success": False, "error": error_message}
    except Exception as e:
        error_message = f"Error creating S3 client: {e}"
        print(error_message)
        return {"success": False, "error": error_message}

    errors = []
    for filepath in filepath_list:
        try:
            filename = os.path.basename(filepath)
            s3_client.upload_file(filepath, s3_bucket, filename)
            print(f"Uploaded {filename} to S3 bucket {s3_bucket}.")
        except ClientError as e:
            error_message = f"Failed to upload {filepath} to S3: {e}"
            print(error_message)
            errors.append(error_message)
        except FileNotFoundError:
            error_message = f"File not found: {filepath}"
            print(error_message)
            errors.append(error_message)
        except Exception as e:
            error_message = f"Error uploading {filepath} to S3: {e}"
            print(error_message)
            errors.append(error_message)

    if not errors:
        for filepath in filepath_list:
            try:
                os.remove(filepath)
                print(f"Deleted local file {filepath}.")
            except Exception as e:
                error_message = f"Error deleting file {filepath}: {e}"
                print(error_message)
        return {"success": True}
    else:
        return {"success": False, "errors": errors}


def local_filesystem_save_strategy(filepath_list, catalogue_name):
    """Function to save files to the local filesystem, using catalogue_name for directory names."""
    print("Saving to local filesystem")

    base_path = os.environ.get("DESTINATION_PATH")

    if not base_path:
        error_message = "Missing DESTINATION_PATH environment variable."
        print(error_message)
        return {"success": False, "error": error_message}
    directory_prefix = os.environ.get("CATALOGUE_PREFIX", "")

    directory_name = f"{directory_prefix}{catalogue_name}"

    destination_path = os.path.join(base_path, directory_name)

    if not os.path.isdir(destination_path):
        try:
            os.makedirs(destination_path)
            print(f"Created directory {destination_path}")
        except Exception as e:
            error_message = f"Failed to create directory {destination_path}: {e}"
            print(error_message)
            return {"success": False, "error": error_message}

    errors = []
    for filepath in filepath_list:
        try:
            filename = os.path.basename(filepath)
            dest_file_path = os.path.join(destination_path, filename)
            shutil.copy2(filepath, dest_file_path)
            print(f"Copied {filename} to {destination_path}")
        except FileNotFoundError:
            error_message = f"File not found: {filepath}"
            print(error_message)
            errors.append(error_message)
        except Exception as e:
            error_message = f"Error copying {filepath} to {destination_path}: {e}"
            print(error_message)
            errors.append(error_message)

    if not errors:
        for filepath in filepath_list:
            try:
                os.remove(filepath)
                print(f"Deleted local file {filepath}.")
            except Exception as e:
                error_message = f"Error deleting file {filepath}: {e}"
                print(error_message)
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
        "Downloads choosen playlist using ytdlp with highest available quality.",
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
