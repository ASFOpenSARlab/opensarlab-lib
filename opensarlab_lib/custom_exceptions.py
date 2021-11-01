class VRTError(Exception):
    """
    Raise when an expected VRT has a different filetype
    """
    pass


class UnexpectedFileExtension(Exception):
    """
    Raise when encountering an unexpected file extension
    """
    pass