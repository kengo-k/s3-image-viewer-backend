from datetime import datetime
from typing import Callable, Literal, TypedDict

TActionKey = Literal["upload", "download", "delete_from_s3", "delete_from_local"]
TActionDict = TypedDict("ActionDictType", {"action": TActionKey, "path": str})
TFileInfoDict = dict[str, datetime]
TCreateAction = Callable[[str, bool], TActionDict]
