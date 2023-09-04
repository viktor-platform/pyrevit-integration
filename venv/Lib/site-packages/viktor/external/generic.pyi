from ..core import File as File
from ..errors import ExecutionError as ExecutionError, LicenseError as LicenseError
from .external_program import ExternalProgram as ExternalProgram
from io import BytesIO
from typing import List, Optional, Tuple, Union

class GenericAnalysis(ExternalProgram):
    def __init__(self, files: List[Tuple[str, Union[BytesIO, File]]] = ..., executable_key: str = ..., output_filenames: List[str] = ...) -> None: ...
    def get_output_file(self, filename: str, *, as_file: bool = ...) -> Optional[Union[BytesIO, File]]: ...
