import abc
import pandas as pd
from ..api_v1 import API as API
from ..core import Color as Color, File as File
from ..errors import InternalError as InternalError, ModelError as ModelError, ParsingError as ParsingError
from ..geo import GEFData as GEFData
from .external_program import ExternalProgram as ExternalProgram
from _typeshed import Incomplete
from abc import ABCMeta, abstractmethod
from datetime import datetime
from enum import Enum
from io import BytesIO, StringIO
from typing import Any, Dict, List, Optional, Tuple, Type, Union

class DFoundationsAnalysis(ExternalProgram):
    input_file: Incomplete
    def __init__(self, input_file: Union[BytesIO, File]) -> None: ...
    def get_output_file(self, extension: str = ..., *, as_file: bool = ...) -> Optional[Union[BytesIO, File]]: ...

class SoilType(Enum):
    GRAVEL: SoilType
    SAND: SoilType
    LOAM: SoilType
    CLAY: SoilType
    PEAT: SoilType

class MaxConeResistType(Enum):
    STANDARD: MaxConeResistType
    MANUAL: MaxConeResistType

class CPTRule(Enum):
    NEN: CPTRule
    NEN_STRESS: CPTRule
    CUR: CPTRule
    TYPE_3: CPTRule
    QC_ONLY: CPTRule

class ConstructionSequence(Enum):
    CPT_EXCAVATION_INSTALL: ConstructionSequence
    INSTALL_CPT_EXCAVATION: ConstructionSequence
    EXCAVATION_CPT_INSTALL: ConstructionSequence
    EXCAVATION_INSTALL_CPT: ConstructionSequence
    INSTALL_EXCAVATION_CPT: ConstructionSequence
    CPT_INSTALL_EXCAVATION: ConstructionSequence
    EXCAVATION_CPT_BOTH_BEFORE_AND_AFTER_INSTALL: ConstructionSequence

class _MainCalculationType(Enum):
    PRELIMINARY_DESIGN: _MainCalculationType
    VERIFICATION: _MainCalculationType

class CalculationType(Enum):
    DESIGN_CALCULATION: CalculationType
    COMPLETE_CALCULATION: CalculationType
    INDICATION_BEARING_CAPACITY: CalculationType
    BEARING_CAPACITY_AT_FIXED_PILE_TIP_LEVEL: CalculationType
    PILE_TIP_LEVEL_AND_NET_BEARING_CAPACITY: CalculationType

class _ReductionConeResistance(Enum):
    SAFE: _ReductionConeResistance
    BEGEMANN: _ReductionConeResistance
    MANUAL: _ReductionConeResistance

class PileType(Enum):
    PREFAB_CONCRETE: PileType
    CLOSED_STEEL: PileType
    DRIVEN_TUBE_BACK_DRIVING: PileType
    DRIVEN_TUBE_BACK_VIBRATION: PileType
    TAPERED_TIMBER: PileType
    STRAIGHT_TIMBER: PileType
    SCREW_LOST_TIP: PileType
    SCREW_WITH_GROUT: PileType
    PREFAB_WITH_GROUT: PileType
    PREFAB_WITHOUT_GROUT: PileType
    STEEL: PileType
    CONTINUOUS_FLIGHT_AUGER: PileType
    BORED_DRILLING: PileType
    BORED_SHELLING: PileType
    OPEN_STEEL: PileType
    MV: PileType
    MICRO_DOUBLE_EXTORTED: PileType
    MICRO_DOUBLE_NOT_EXTORTED: PileType
    MICRO_SINGLE_EXTORTED: PileType
    MICRO_SINGLE_NOT_EXTORTED: PileType
    MICRO_ANCHOR_BORED: PileType
    MICRO_ANCHOR_SCREWED: PileType
    MICRO_VIBRATED: PileType
    GROUTED_STEEL_PROFILE: PileType
    GROUTED_STEEL_PIPE: PileType
    USER_DEFINED_VIBRATING: PileType
    USER_DEFINED_LOW_VIBRATING: PileType
    USER_DEFINED: PileType

class PileTypeClayLoamPeat(Enum):
    ACCORDING_TO_STANDARD: PileTypeClayLoamPeat
    USER_DEFINED: PileTypeClayLoamPeat

class PileLoadSettlementCurve(Enum):
    ONE: PileLoadSettlementCurve
    TWO: PileLoadSettlementCurve
    THREE: PileLoadSettlementCurve

class PileMaterial(Enum):
    CONCRETE: PileMaterial
    STEEL: PileMaterial
    TIMBER: PileMaterial
    WOOD: PileMaterial
    USER_DEFINED: PileMaterial

class PileSlipLayer(Enum):
    NONE: PileSlipLayer
    SYNTHETIC: PileSlipLayer
    BENTONITE: PileSlipLayer
    BITUMEN: PileSlipLayer
    USER_DEFINED: PileSlipLayer

class Metadata:
    def __init__(self, file_name: str = ..., company: str = ..., title_1: str = ..., title_2: str = ..., geotechnical_consultant: str = ..., design_engineer: str = ..., principal: str = ..., project_id: str = ..., location: str = ..., current_date: bool = ..., current_time: bool = ...) -> None: ...

class _CalculationOptions:
    def __init__(self, calculation_type: CalculationType, rigid: bool, *, unit_weight_water: float = ..., surcharge: float = ..., max_allowed_settlement_str_geo: int = ..., max_allowed_relative_rotation_str_geo: int = ..., max_allowed_settlement_sls: int = ..., max_allowed_relative_rotation_sls: int = ..., xi3: float = ..., xi4: float = ..., gamma_b: float = ..., gamma_s: float = ..., gamma_fnk: float = ..., gamma_m_var_qc: float = ..., gamma_st: float = ..., gamma_gamma: float = ..., area: float = ..., e_ea_gem: float = ..., write_intermediate_results: bool = ..., use_pile_group: bool = ..., overrule_excavation: bool = ..., suppress_qciii_reduction: bool = ..., use_almere_rules: bool = ..., use_extra_almere_rules: bool = ..., use_compaction: bool = ..., overrule_excess_pore_pressure: bool = ..., trajectory_begin_end_interval: Tuple[float, float, float] = ..., net_bearing_capacity: int = ..., cpt_test_level: float = ...) -> None: ...
    @property
    def calculation_type(self) -> CalculationType: ...

class BearingPilesCalculationOptions(_CalculationOptions):
    def __init__(self, calculation_type: CalculationType, rigid: bool, max_allowed_settlement_str_geo: int = ..., max_allowed_settlement_sls: int = ..., max_allowed_relative_rotation_str_geo: int = ..., max_allowed_relative_rotation_sls: int = ..., *, xi3: float = ..., xi4: float = ..., gamma_b: float = ..., gamma_s: float = ..., gamma_fnk: float = ..., area: float = ..., e_ea_gem: float = ..., write_intermediate_results: bool = ..., use_pile_group: bool = ..., overrule_excavation: bool = ..., suppress_qciii_reduction: bool = ..., use_almere_rules: bool = ..., use_extra_almere_rules: bool = ..., trajectory_begin_end_interval: Tuple[float, float, float] = ..., net_bearing_capacity: int = ..., cpt_test_level: float = ...) -> None: ...

class TensionPilesCalculationOptions(_CalculationOptions):
    def __init__(self, calculation_type: CalculationType, rigid: bool, unit_weight_water: float = ..., surcharge: float = ..., *, xi3: float = ..., xi4: float = ..., gamma_m_var_qc: float = ..., gamma_st: float = ..., gamma_gamma: float = ..., use_compaction: bool = ..., overrule_excavation: bool = ..., overrule_excess_pore_pressure: bool = ..., trajectory_begin_end_interval: Tuple[float, float, float] = ..., net_bearing_capacity: int = ...) -> None: ...

class _Material:
    def __init__(self, soil_type: SoilType, gam_dry: float, gam_wet: float, color: Color = ..., *, e0: float = ..., diameter_d50: float = ..., min_void_ratio: float = ..., max_void_ratio: float = ..., cohesion: float = ..., phi: float = ..., cu: float = ..., max_cone_resist_type: MaxConeResistType = ..., max_cone_resist: float = ..., use_tension: bool = ..., ca: float = ..., cc: float = ...) -> None: ...
    @property
    def color(self) -> Color: ...
    def serialize(self) -> Dict[str, Any]: ...

class _CPT:
    def __init__(self, measurements: List[List[float]], ground_level: float, rule: CPTRule = ..., min_layer_thickness: float = ..., *, imported: bool, project_name: str = ..., project_id: str = ..., client_name: str = ..., file_date: datetime = ..., gef_version: str = ..., x: float = ..., y: float = ..., excavation_depth: float = ...) -> None: ...
    def serialize(self) -> Dict[str, Any]: ...

class ProfileLayer:
    def __init__(self, top_level: float, material: str, ad_pore_pressure_at_top: float = ..., ad_pore_pressure_at_bottom: float = ..., ocr: float = ...) -> None: ...
    @property
    def material(self) -> str: ...

class _Profile:
    def __init__(self, cpt: _CPT, layers: List[ProfileLayer], x: float, y: float, phreatic_level: float, *, pile_tip_level: float = ..., overconsolidation_ratio: float = ..., top_positive_skin_friction: float = ..., bottom_negative_skin_friction: float = ..., expected_ground_level_settlement: float = ..., top_tension_zone: float = ...) -> None: ...
    @property
    def layers(self) -> List[ProfileLayer]: ...
    def serialize(self, name: str) -> Dict[str, Any]: ...

class _PileShape(metaclass=ABCMeta):
    class _Shape(Enum):
        ROUND: _PileShape._Shape
        RECT: _PileShape._Shape
        ROUND_ENL: _PileShape._Shape
        RECT_ENL: _PileShape._Shape
        TAPER: _PileShape._Shape
        HOLLOW: _PileShape._Shape
        LOST_TIP: _PileShape._Shape
        DRIVEN: _PileShape._Shape
        SECTION: _PileShape._Shape
        HOL_OPEN: _PileShape._Shape
        H: _PileShape._Shape
        USER_DEFINED: _PileShape._Shape

class RectPile(_PileShape):
    width: Incomplete
    length: Incomplete
    def __init__(self, width: float, length: float) -> None: ...

class RectEnlPile(_PileShape):
    base_width: Incomplete
    base_length: Incomplete
    base_height: Incomplete
    shaft_width: Incomplete
    shaft_length: Incomplete
    def __init__(self, base_width: float, base_length: float, base_height: float, shaft_width: float, shaft_length: float) -> None: ...

class SectionPile(RectPile): ...

class UserPile(_PileShape):
    circumference: Incomplete
    cross_section: Incomplete
    def __init__(self, circumference: float, cross_section: float) -> None: ...

class RoundPile(_PileShape):
    diameter: Incomplete
    def __init__(self, diameter: float) -> None: ...

class TaperPile(_PileShape):
    diameter_tip: Incomplete
    increase: Incomplete
    def __init__(self, diameter_tip: float, increase: float) -> None: ...

class HollowPile(_PileShape):
    external_diameter: Incomplete
    wall_thickness: Incomplete
    def __init__(self, external_diameter: float, wall_thickness: float) -> None: ...
    @property
    def internal_diameter(self) -> float: ...

class HollowOpenPile(_PileShape):
    external_diameter: Incomplete
    wall_thickness: Incomplete
    def __init__(self, external_diameter: float, wall_thickness: float) -> None: ...
    @property
    def internal_diameter(self) -> float: ...

class LostTipPile(_PileShape):
    base_diameter: Incomplete
    pile_diameter: Incomplete
    def __init__(self, base_diameter: float, pile_diameter: float) -> None: ...

class RoundEnlPile(LostTipPile):
    base_height: Incomplete
    def __init__(self, base_diameter: float, pile_diameter: float, base_height: float) -> None: ...

class DrivenBasePile(RoundEnlPile): ...

class HShapedPile(_PileShape):
    height: Incomplete
    width: Incomplete
    thickness_web: Incomplete
    thickness_flange: Incomplete
    def __init__(self, height: float, width: float, thickness_web: float, thickness_flange: float) -> None: ...

class _PileTypeConfig(metaclass=ABCMeta):
    def __init__(self, type_sand_gravel: PileType = ..., type_clay_loam_peat: PileTypeClayLoamPeat = ..., material: PileMaterial = ..., factor_sand_gravel: float = ..., factor_clay_loam_peat: float = ..., material_property: float = ...) -> None: ...
    @abstractmethod
    def validate(self, shape: Type[_PileShape]) -> None: ...
    def serialize(self) -> Dict[str, Any]: ...

class _BearingPileTypeConfig(_PileTypeConfig):
    def __init__(self, pile_type: PileType, slip_layer: PileSlipLayer, type_sand_gravel: PileType = ..., type_clay_loam_peat: PileTypeClayLoamPeat = ..., type_p: PileType = ..., load_settlement_curve: PileLoadSettlementCurve = ..., material: PileMaterial = ..., factor_sand_gravel: float = ..., factor_clay_loam_peat: float = ..., factor_pile_class: float = ..., e_modulus_material: float = ..., slip_layer_adhesion: float = ..., use_pre_2016: bool = ..., as_prefab: bool = ..., qciii_reduction: float = ..., overrule_tip_section_factor: float = ..., overrule_tip_shape_factor: float = ...) -> None: ...
    def validate(self, shape: Type[_PileShape]) -> None: ...
    def serialize(self) -> Dict[str, Any]: ...

class _TensionPileTypeConfig(_PileTypeConfig):
    def __init__(self, type_sand_gravel: PileType, type_clay_loam_peat: PileTypeClayLoamPeat, material: PileMaterial, factor_sand_gravel: float = ..., factor_clay_loam_peat: float = ..., unit_weight_material: float = ...) -> None: ...
    def validate(self, shape: Type[_PileShape]) -> None: ...

class _PileType:
    def __init__(self, shape: _PileShape, config: _PileTypeConfig) -> None: ...
    def serialize(self, name: str) -> Dict[str, Any]: ...

class _Pile:
    def __init__(self, x: float, y: float, *, pile_head_level: float = ..., surcharge: float = ..., limit_state_str_geo: float = ..., serviceability_limit_state: float = ..., load_max_min: Tuple[float, float] = ...) -> None: ...
    def serialize(self, name: str) -> Dict[str, Any]: ...

class _Model(metaclass=ABCMeta):
    def __init__(self, construction_sequence: ConstructionSequence, calculation_options: _CalculationOptions, excavation_level: float, reduction_cone_resistance: float = ..., *, create_default_materials: bool = ...) -> None: ...
    @property
    def materials(self) -> Dict[str, Dict[str, Any]]: ...
    @property
    def profiles(self) -> List[Dict[str, Any]]: ...
    @property
    def pile_types(self) -> List[Dict[str, Any]]: ...
    @property
    def piles(self) -> List[Dict[str, Any]]: ...
    def generate_input_file(self, metadata: Metadata = ..., *, as_file: bool = ...) -> Union[File, BytesIO]: ...

class BearingPilesModel(_Model):
    def __init__(self, construction_sequence: ConstructionSequence, calculation_options: BearingPilesCalculationOptions, excavation_level: float, reduction_cone_resistance: float = ..., *, create_default_materials: bool = ...) -> None: ...
    def create_material(self, name: str, soil_type: SoilType, gamma_unsat: float, gamma_sat: float, friction_angle: float, diameter_d50: float = ..., color: Color = ...) -> None: ...
    def create_profile(self, name: str, layers: List[ProfileLayer], x: float, y: float, measurements: List[Tuple[float, float]], phreatic_level: float, pile_tip_level: float, overconsolidation_ratio: float, top_positive_skin_friction: float, bottom_negative_skin_friction: float, expected_ground_level_settlement: float, *, cpt_rule: CPTRule = ..., min_layer_thickness: float = ...) -> None: ...
    def import_profile(self, cpt: GEFData, layers: List[ProfileLayer], x: float, y: float, phreatic_level: float, pile_tip_level: float, overconsolidation_ratio: float, top_positive_skin_friction: float, bottom_negative_skin_friction: float, expected_ground_level_settlement: float, name: str = ..., manual_ground_level: float = ..., *, cpt_rule: CPTRule = ..., min_layer_thickness: float = ...) -> None: ...
    def create_pile_type(self, name: str, shape: _PileShape, pile_type: PileType, slip_layer: PileSlipLayer, type_sand_gravel: PileType = ..., type_clay_loam_peat: PileTypeClayLoamPeat = ..., type_p: PileType = ..., load_settlement_curve: PileLoadSettlementCurve = ..., material: PileMaterial = ..., factor_sand_gravel: float = ..., factor_clay_loam_peat: float = ..., factor_pile_class: float = ..., e_modulus: float = ..., slip_layer_adhesion: float = ..., *, use_pre_2016: bool = ..., as_prefab: bool = ..., qciii_reduction: float = ..., overrule_tip_section_factor: float = ..., overrule_tip_shape_factor: float = ...) -> None: ...
    def create_pile(self, name: str, x: float, y: float, pile_head_level: float, surcharge: float, limit_state_str_geo: float, serviceability_limit_state: float) -> None: ...

class TensionPilesModel(_Model):
    def __init__(self, construction_sequence: ConstructionSequence, calculation_options: TensionPilesCalculationOptions, excavation_level: float, reduction_cone_resistance: float = ..., *, create_default_materials: bool = ...) -> None: ...
    def create_material(self, name: str, soil_type: SoilType, gamma_unsat: float, gamma_sat: float, friction_angle: float, diameter_d50: float = ..., max_cone_resist_type: MaxConeResistType = ..., max_cone_resist: float = ..., apply_tension: bool = ..., min_void_ratio: float = ..., max_void_ratio: float = ..., color: Color = ...) -> None: ...
    def create_profile(self, name: str, layers: List[ProfileLayer], x: float, y: float, measurements: List[Tuple[float, float]], phreatic_level: float, pile_tip_level: float, top_tension_zone: float, *, cpt_rule: CPTRule = ..., min_layer_thickness: float = ...) -> None: ...
    def import_profile(self, cpt: GEFData, layers: List[ProfileLayer], x: float, y: float, phreatic_level: float, pile_tip_level: float, top_tension_zone: float, name: str = ..., manual_ground_level: float = ..., *, cpt_rule: CPTRule = ..., min_layer_thickness: float = ...) -> None: ...
    def create_pile_type(self, name: str, shape: _PileShape, type_sand_gravel: PileType, type_clay_loam_peat: PileTypeClayLoamPeat, material: PileMaterial, factor_sand_gravel: float = ..., factor_clay_loam_peat: float = ..., unit_weight_material: float = ...) -> None: ...
    def create_pile(self, name: str, x: float, y: float, pile_head_level: float, load_max_min: Tuple[float, float] = ...) -> None: ...

class OutputFileParser(metaclass=abc.ABCMeta):
    def __new__(cls, fod_file: StringIO) -> Any: ...
    def __init__(self, fod_file: StringIO) -> None: ...
    @property
    def raw_results(self) -> str: ...
    @property
    @abstractmethod
    def calculation_parameters(self) -> Dict[str, Union[float, bool]]: ...
    @abstractmethod
    def results(self, as_pandas: bool = ...) -> Dict[str, Union[pd.DataFrame, Dict[str, Any]]]: ...

class _ParserV19: ...

class _PreliminaryBearingParserV17(OutputFileParser):
    @property
    def calculation_parameters(self) -> Dict[str, Union[float, bool]]: ...
    def results(self, as_pandas: bool = ...) -> Dict[str, Union[pd.DataFrame, Dict[str, Any]]]: ...

class _PreliminaryTensionParserV17(OutputFileParser):
    @property
    def calculation_parameters(self) -> Dict[str, Union[float, bool]]: ...
    def results(self, as_pandas: bool = ...) -> Dict[str, Any]: ...

class _VerificationParserV17(OutputFileParser):
    def __init__(self, fod_file: StringIO) -> None: ...
    @property
    def calculation_parameters(self) -> Dict[str, Union[float, bool]]: ...
    def results(self, as_pandas: bool = ...) -> Dict[str, Union[pd.DataFrame, Dict[str, Any]]]: ...

class _PreliminaryBearingParserV19(OutputFileParser, _ParserV19):
    def __init__(self, fod_file: StringIO) -> None: ...
    @property
    def calculation_parameters(self) -> Dict[str, Union[float, bool]]: ...
    def results(self, as_pandas: bool = ...) -> Dict[str, Union[pd.DataFrame, Dict[str, Any]]]: ...

class _PreliminaryTensionParserV19(_PreliminaryTensionParserV17, _ParserV19):
    def results(self, as_pandas: bool = ...) -> Dict[str, Union[pd.DataFrame, Dict[str, Any]]]: ...

class _VerificationParserV19(OutputFileParser, _ParserV19):
    @property
    def calculation_parameters(self) -> Dict[str, Union[float, bool]]: ...
    def results(self, as_pandas: bool = ...) -> Dict[str, Union[pd.DataFrame, Dict[str, Any]]]: ...
