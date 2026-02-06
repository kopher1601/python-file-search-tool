class FileSearchError(Exception):
    pass

class AuthenticationError(FileSearchError):
    pass

class StoreNotFoundError(FileSearchError):
    pass

class FileUploadError(FileSearchError):
    pass
