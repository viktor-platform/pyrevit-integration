from .api_v1 import API as API
from .core import File as File, _SerializableObject
from .views import ImageResult as ImageResult
from _typeshed import Incomplete
from io import BytesIO
from munch import Munch as Munch
from typing import Any, Dict, List, Union

class SetParamsResult(_SerializableObject):
    def __init__(self, params: Union[dict, Munch]) -> None: ...
    def get(self, key: str) -> Any: ...
SetParametersResult = SetParamsResult

class DownloadResult(_SerializableObject):
    def __init__(self, file_content: Union[str, bytes, File, BytesIO] = ..., file_name: str = ..., encoding: str = ..., *, zipped_files: Dict[str, Union[File, BytesIO]] = ...) -> None: ...

class OptimizationResultElement:
    def __init__(self, params: Union[dict, Munch], analysis_result: dict = ...) -> None: ...
OptimisationResultElement = OptimizationResultElement

class OptimizationResult(_SerializableObject):
    result_column_names_input: Incomplete
    result_column_names_result: Incomplete
    def __init__(self, results: List[OptimizationResultElement], result_column_names_input: List[str] = ..., output_headers: dict = ..., image: ImageResult = ...) -> None: ...
OptimisationResult = OptimizationResult

class ViktorResult(_SerializableObject):
    def __init__(self, optimisation_result: OptimizationResult = ..., set_parameters_result: SetParamsResult = ..., download_result: DownloadResult = ..., *, optimization_result: OptimizationResult = ..., set_params_result: SetParamsResult = ...) -> None: ...
