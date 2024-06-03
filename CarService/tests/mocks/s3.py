from fastapi import UploadFile

from app.storage.s3 import EXPIRATION_TIME, FileManager

FILES = {}


class MockS3Manager(FileManager):
    THUMBNAIL_URL: str = 'http://test-mock-s3/thumbnail-url'

    def __init__(self, bucket: str):
        self.bucket = bucket

    async def create_presigned_url(self, file_name: str, expiration_time: int = EXPIRATION_TIME) -> str | None:
        if file_name in FILES:
            return self.THUMBNAIL_URL

    async def upload_file(self, file: UploadFile, file_name: str) -> bool:
        FILES[file_name] = file
        return True

    async def delete_objects(self, file_name: str) -> bool:
        if file_name in FILES:
            del FILES[file_name]
            return True
        return False
