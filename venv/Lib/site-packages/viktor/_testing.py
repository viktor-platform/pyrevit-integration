""" This module is added to skip_files in setup.py to exclude it from being cythonized, since below functions increase
the time to cythonize significantly. """

import importlib
import io

from munch import Munch
from types import ModuleType
from typing import Callable
from unittest import mock

from .api_v1 import API
from .core import Storage
from .external.axisvm import AxisVMAnalysis
from .external.excel import Excel
from .external.generic import GenericAnalysis
from .external.idea_rcs import IdeaRcsAnalysis
from .external.scia import SciaAnalysis
from .external.dsettlement import DSettlementAnalysis
from .external.dsheetpiling import DSheetPilingAnalysis
from .external.dstability import DStabilityAnalysis
from .external.dgeostability import DGeoStabilityAnalysis
from .external.dfoundations import DFoundationsAnalysis
from .external.grlweap import GRLWeapAnalysis
from .external.robot import RobotAnalysis
from .external.rfem import RFEMAnalysis


def _mock_ParamsFromFile(func: Callable, args: tuple, kwargs: dict, controller_module: ModuleType,
                         testing_module: ModuleType) -> Callable:
    try:
        with mock.patch('viktor.core.ParamsFromFile', lambda *x, **y: lambda f: f), \
                mock.patch('viktor.ParamsFromFile', lambda *x, **y: lambda f: f):
            importlib.reload(controller_module)  # reload module with patch
            importlib.reload(testing_module)  # reload testing module with patched controller module
            return func(*args, **kwargs)
    finally:
        importlib.reload(controller_module)  # reset module without patch
        importlib.reload(testing_module)  # reset module without patch


def _mock_Storage(func: Callable, args: tuple, kwargs: dict, mock_set: Callable, mock_delete: Callable,
                  mock_get: Callable, mock_list: Callable) -> Callable:
    with mock.patch.object(Storage, '__init__', return_value=None), \
            mock.patch.object(Storage, 'set', mock_set), \
            mock.patch.object(Storage, 'delete', mock_delete), \
            mock.patch.object(Storage, 'get', mock_get), \
            mock.patch.object(Storage, 'list', mock_list):
        return func(*args, **kwargs)


def _mock_API(func: Callable, args: tuple, kwargs: dict, mocked_get_entity: Callable,
              mocked_create_child_entity: Callable, mocked_delete_entity: Callable,
              mocked_generate_upload_url: Callable, mocked_get_current_user: Callable,
              mocked_get_entities_by_type: Callable, mocked_get_entity_children: Callable,
              mocked_get_entity_siblings: Callable, mocked_get_root_entities: Callable,
              mocked_get_entity_parent: Callable, mocked_get_entity_revisions: Callable,
              mocked_get_entity_file: Callable, mocked_rename_entity: Callable,
              mocked_set_entity_params: Callable) -> Callable:
    with mock.patch.object(API, '__init__', return_value=None), \
            mock.patch.object(API, 'get_entity', side_effect=mocked_get_entity), \
            mock.patch.object(API, 'create_child_entity', side_effect=mocked_create_child_entity), \
            mock.patch.object(API, 'delete_entity', side_effect=mocked_delete_entity), \
            mock.patch.object(API, 'generate_upload_url', side_effect=mocked_generate_upload_url), \
            mock.patch.object(API, 'get_current_user', side_effect=mocked_get_current_user), \
            mock.patch.object(API, 'get_entities_by_type', side_effect=mocked_get_entities_by_type), \
            mock.patch.object(API, 'get_entity_children', side_effect=mocked_get_entity_children), \
            mock.patch.object(API, 'get_entity_siblings', side_effect=mocked_get_entity_siblings), \
            mock.patch.object(API, 'get_root_entities', side_effect=mocked_get_root_entities), \
            mock.patch.object(API, 'get_entity_parent', side_effect=mocked_get_entity_parent), \
            mock.patch.object(API, 'get_entity_revisions', side_effect=mocked_get_entity_revisions), \
            mock.patch.object(API, 'get_entity_file', side_effect=mocked_get_entity_file), \
            mock.patch.object(API, 'rename_entity', side_effect=mocked_rename_entity), \
            mock.patch.object(API, 'set_entity_params', side_effect=mocked_set_entity_params):
        return func(*args, **kwargs)


def _mock_params(mocked_get_entity: Callable, mocked_file_resource: type,
                 deserialize_function: Callable[[dict, dict], Munch], param_types: dict, params: dict) -> Munch:
    with mock.patch.object(API, '__init__', return_value=None), \
            mock.patch.object(API, 'get_entity', side_effect=mocked_get_entity), \
            mock.patch('viktor.parametrization.FileResource', mocked_file_resource):

        try:
            return deserialize_function(param_types, params)
        except Exception as e:
            raise ValueError("Invalid params in combination with parametrization") from e


def _mock_View(func: Callable, args: tuple, kwargs: dict, controller_module: ModuleType,
               testing_module: ModuleType) -> Callable:
    patches = [
        mock.patch('viktor.views.GeometryView', lambda *x, **y: lambda f: f),
        mock.patch('viktor.views.DataView', lambda *x, **y: lambda f: f),
        mock.patch('viktor.views.ImageView', lambda *x, **y: lambda f: f),
        mock.patch('viktor.views.MapView', lambda *x, **y: lambda f: f),
        mock.patch('viktor.views.GeoJSONView', lambda *x, **y: lambda f: f),
        mock.patch('viktor.views.WebView', lambda *x, **y: lambda f: f),
        mock.patch('viktor.views.PlotlyView', lambda *x, **y: lambda f: f),
        mock.patch('viktor.views.PDFView', lambda *x, **y: lambda f: f),
        mock.patch('viktor.views.GeometryAndDataView', lambda *x, **y: lambda f: f),
        mock.patch('viktor.views.ImageAndDataView', lambda *x, **y: lambda f: f),
        mock.patch('viktor.views.MapAndDataView', lambda *x, **y: lambda f: f),
        mock.patch('viktor.views.GeoJSONAndDataView', lambda *x, **y: lambda f: f),
        mock.patch('viktor.views.WebAndDataView', lambda *x, **y: lambda f: f),
        mock.patch('viktor.views.PlotlyAndDataView', lambda *x, **y: lambda f: f),
    ]
    try:
        for p in patches:
            p.start()
        importlib.reload(controller_module)  # reload module with patch
        importlib.reload(testing_module)  # reload testing module with patched controller module
        return func(*args, **kwargs)
    finally:
        importlib.reload(controller_module)  # reset module without patch
        importlib.reload(testing_module)  # reset module without patch
        for p in patches:
            p.stop()


def _mock_SciaAnalysis(func: Callable, args: tuple, kwargs: dict, mocked_get_engineering_report: Callable,
                       mocked_get_updated_esa_model: Callable, mocked_get_xml_output_file: Callable) -> Callable:
    with mock.patch.object(SciaAnalysis, '__init__', return_value=None), \
            mock.patch.object(SciaAnalysis, 'execute', return_value=None), \
            mock.patch.object(SciaAnalysis, 'get_engineering_report', side_effect=mocked_get_engineering_report), \
            mock.patch.object(SciaAnalysis, 'get_updated_esa_model', side_effect=mocked_get_updated_esa_model), \
            mock.patch.object(SciaAnalysis, 'get_xml_output_file', side_effect=mocked_get_xml_output_file):
        return func(*args, **kwargs)


def _mock_DSettlementAnalysis(func: Callable, args: tuple, kwargs: dict, get_output_file: Callable,
                              get_sld_file: Callable) -> Callable:
    with mock.patch.multiple(
            DSettlementAnalysis,
            __init__=mock.Mock(return_value=None),
            execute=mock.Mock(return_value=None),
            get_output_file=mock.Mock(side_effect=get_output_file),
            get_sld_file=mock.Mock(side_effect=get_sld_file)
    ):
        return func(*args, **kwargs)


def _mock_DSheetPilingAnalysis(func: Callable, args: tuple, kwargs: dict, get_output_file: Callable) -> Callable:
    with mock.patch.multiple(
            DSheetPilingAnalysis,
            __init__=mock.Mock(return_value=None),
            execute=mock.Mock(return_value=None),
            get_output_file=mock.Mock(side_effect=get_output_file),
    ):
        return func(*args, **kwargs)


def _mock_DStabilityAnalysis(func: Callable, args: tuple, kwargs: dict, get_output_file: Callable) -> Callable:
    with mock.patch.multiple(
            DStabilityAnalysis,
            __init__=mock.Mock(return_value=None),
            execute=mock.Mock(return_value=None),
            get_output_file=mock.Mock(side_effect=get_output_file),
    ):
        return func(*args, **kwargs)


def _mock_DGeoStabilityAnalysis(func: Callable, args: tuple, kwargs: dict, get_output_file: Callable) -> Callable:
    with mock.patch.multiple(
            DGeoStabilityAnalysis,
            __init__=mock.Mock(return_value=None),
            execute=mock.Mock(return_value=None),
            get_output_file=mock.Mock(side_effect=get_output_file),
    ):
        return func(*args, **kwargs)


def _mock_DFoundationsAnalysis(func: Callable, args: tuple, kwargs: dict, get_output_file: Callable) -> Callable:
    with mock.patch.multiple(
            DFoundationsAnalysis,
            __init__=mock.Mock(return_value=None),
            execute=mock.Mock(return_value=None),
            get_output_file=mock.Mock(side_effect=get_output_file),
    ):
        return func(*args, **kwargs)


def _mock_GRLWeapAnalysis(func: Callable, args: tuple, kwargs: dict, get_output_file: Callable) -> Callable:
    with mock.patch.multiple(
            GRLWeapAnalysis,
            __init__=mock.Mock(return_value=None),
            execute=mock.Mock(return_value=None),
            get_output_file=mock.Mock(side_effect=get_output_file),
    ):
        return func(*args, **kwargs)


def _mock_IdeaRcsAnalysis(func: Callable, args: tuple, kwargs: dict, get_output_file: Callable,
                          get_idea_rcs_file: Callable) -> Callable:
    with mock.patch.multiple(
            IdeaRcsAnalysis,
            __init__=mock.Mock(return_value=None),
            execute=mock.Mock(return_value=None),
            get_output_file=mock.Mock(side_effect=get_output_file),
            get_idea_rcs_file=mock.Mock(side_effect=get_idea_rcs_file),
    ):
        return func(*args, **kwargs)


def _mock_RobotAnalysis(func: Callable, args: tuple, kwargs: dict, get_model_file: Callable,
                        get_results: Callable) -> Callable:
    with mock.patch.multiple(
            RobotAnalysis,
            __init__=mock.Mock(return_value=None),
            execute=mock.Mock(return_value=None),
            get_model_file=mock.Mock(side_effect=get_model_file),
            get_results=mock.Mock(side_effect=get_results)
    ):
        return func(*args, **kwargs)


def _mock_AxisVMAnalysis(func: Callable, args: tuple, kwargs: dict, get_model_file: Callable,
                         get_result_file: Callable, get_results: Callable) -> Callable:
    with mock.patch.multiple(
            AxisVMAnalysis,
            __init__=mock.Mock(return_value=None),
            execute=mock.Mock(return_value=None),
            get_model_file=mock.Mock(side_effect=get_model_file),
            get_result_file=mock.Mock(side_effect=get_result_file),
            get_results=mock.Mock(side_effect=get_results)
    ):
        return func(*args, **kwargs)


def _mock_GenericAnalysis(func: Callable, args: tuple, kwargs: dict, get_output_file: Callable) -> Callable:
    with mock.patch.multiple(
            GenericAnalysis,
            __init__=mock.Mock(return_value=None),
            execute=mock.Mock(return_value=None),
            get_output_file=mock.Mock(side_effect=get_output_file),
    ):
        return func(*args, **kwargs)


def _mock_Excel(func: Callable, args: tuple, kwargs: dict, get_named_cell_result: Callable,
                get_direct_cell_result: Callable, get_filled_template: Callable) -> Callable:
    with mock.patch.multiple(
            Excel,
            __init__=mock.Mock(return_value=None),
            execute=mock.Mock(return_value=None),
            get_named_cell_result=mock.Mock(side_effect=get_named_cell_result),
            get_direct_cell_result=mock.Mock(side_effect=get_direct_cell_result),
            get_filled_template=mock.Mock(side_effect=get_filled_template),
            filled_template=io.BytesIO(b''),
            success=True,
            result_available=mock.Mock(return_value=True),
            error_message=None,
    ):
        return func(*args, **kwargs)


def _mock_RFEMAnalysis(func: Callable, args: tuple, kwargs: dict, get_model: Callable,
                       get_result: Callable) -> Callable:
    with mock.patch.multiple(
            RFEMAnalysis,
            __init__=mock.Mock(return_value=None),
            execute=mock.Mock(return_value=None),
            get_model=mock.Mock(side_effect=get_model),
            get_result=mock.Mock(side_effect=get_result)
    ):
        return func(*args, **kwargs)
