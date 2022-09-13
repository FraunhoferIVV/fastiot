import os

FASTIOT_OBJECT_STORAGE_SUBJECT = 'FASTIOT_OBJECT_STORAGE_SUBJECT'


class ObjectStorageConstants:

    @property
    def subject(self):
        return os.environ.get(FASTIOT_OBJECT_STORAGE_SUBJECT, 'v1.>')


env_object_storage = ObjectStorageConstants()
