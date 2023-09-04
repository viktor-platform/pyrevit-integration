import abc
from ..core import File as File
from ..errors import ExecutionError as ExecutionError
from .external_program import ExternalProgram as ExternalProgram
from _typeshed import Incomplete
from abc import ABC
from enum import Enum
from io import BytesIO
from typing import List, Tuple, Union

class LoadingType(Enum):
    LOAD_CASE: LoadingType
    LOAD_COMBINATION: LoadingType

class RFEMAction(ABC, metaclass=abc.ABCMeta):
    def __init__(self, id_: int) -> None: ...

class EnergyOptimizationAction(RFEMAction):
    load_cases: Incomplete
    loading_type: Incomplete
    goal: Incomplete
    accuracy: Incomplete
    def __init__(self, load_cases: List[int], loading_type: LoadingType = ..., *, goal: float, accuracy: float) -> None: ...

class CopyNodalLoadAction(RFEMAction):
    factor: Incomplete
    copy_from_to: Incomplete
    loading_type: Incomplete
    def __init__(self, copy_from_to: List[Tuple[int, int]], loading_type: LoadingType = ..., *, factor: float = ...) -> None: ...

class WriteResultsAction(RFEMAction):
    load_cases: Incomplete
    loading_type: Incomplete
    def __init__(self, load_cases: List[int] = ..., loading_type: LoadingType = ...) -> None: ...

class RFEMAnalysis(ExternalProgram):
    def __init__(self, rfx_file: Union[BytesIO, File], actions: List[RFEMAction]) -> None: ...
    def get_model(self, *, as_file: bool = ...) -> Union[BytesIO, File]: ...
    def get_result(self, load_case: int, *, as_file: bool = ...) -> Union[BytesIO, File]: ...
