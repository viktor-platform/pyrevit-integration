from ..core import File as File
from .external_program import ExternalProgram as ExternalProgram
from _typeshed import Incomplete
from typing import Optional

class DStabilityAnalysis(ExternalProgram):
    input_file: Incomplete
    def __init__(self, input_file: File) -> None: ...
    def get_output_file(self, extension: str = ...) -> Optional[File]: ...
