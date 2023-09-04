import abc
import os
from ..api_v1 import API as API
from ..core import File as File
from ..errors import WordFileError as WordFileError
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from io import BytesIO
from typing import BinaryIO, List, Union

class WordFileComponent(ABC, metaclass=abc.ABCMeta):
    identifier: Incomplete
    @abstractmethod
    def __init__(self, identifier: str): ...

class WordFileTag(WordFileComponent):
    value: Incomplete
    def __init__(self, identifier: str, value: object) -> None: ...

class WordFileImage(WordFileComponent):
    file_content: Incomplete
    width: Incomplete
    height: Incomplete
    def __init__(self, file: BinaryIO, identifier: str, width: int = ..., height: int = ...) -> None: ...
    @classmethod
    def from_path(cls, file_path: Union[str, bytes, os.PathLike], identifier: str, width: int = ..., height: int = ...) -> WordFileImage: ...

class WordFileResult:
    def __init__(self, *, file_content: bytes = ...) -> None: ...
    @property
    def file_content(self) -> bytes: ...

class WordFileTemplate:
    def __init__(self, file: BytesIO, components: List[WordFileComponent]) -> None: ...
    @classmethod
    def from_path(cls, file_path: Union[str, bytes, os.PathLike], components: List[WordFileComponent]) -> WordFileTemplate: ...
    def render(self) -> WordFileResult: ...
    @property
    def result(self) -> WordFileResult: ...

def render_word_file(template: BinaryIO, components: List[WordFileComponent]) -> File: ...
