from ..core import File as File
from ..errors import ExecutionError as ExecutionError
from .external_program import ExternalProgram as ExternalProgram
from _typeshed import Incomplete
from io import BytesIO
from typing import Optional, Union

class GRLWeapAnalysis(ExternalProgram):
    input_file: Incomplete
    def __init__(self, input_file: Union[BytesIO, File]) -> None: ...
    def get_output_file(self, *, as_file: bool = ...) -> Optional[Union[BytesIO, File]]: ...
