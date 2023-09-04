# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from viktor._vendor.libcst._position import CodePosition, CodeRange
from viktor._vendor.libcst.metadata.accessor_provider import AccessorProvider
from viktor._vendor.libcst.metadata.base_provider import (
    BaseMetadataProvider,
    BatchableMetadataProvider,
    ProviderT,
    VisitorMetadataProvider,
)
from viktor._vendor.libcst.metadata.expression_context_provider import (
    ExpressionContext,
    ExpressionContextProvider,
)
from viktor._vendor.libcst.metadata.full_repo_manager import FullRepoManager
from viktor._vendor.libcst.metadata.name_provider import (
    FullyQualifiedNameProvider,
    QualifiedNameProvider,
)
from viktor._vendor.libcst.metadata.parent_node_provider import ParentNodeProvider
from viktor._vendor.libcst.metadata.position_provider import (
    PositionProvider,
    WhitespaceInclusivePositionProvider,
)
from viktor._vendor.libcst.metadata.reentrant_codegen import (
    CodegenPartial,
    ExperimentalReentrantCodegenProvider,
)
from viktor._vendor.libcst.metadata.scope_provider import (
    Access,
    Accesses,
    Assignment,
    Assignments,
    BaseAssignment,
    BuiltinAssignment,
    BuiltinScope,
    ClassScope,
    ComprehensionScope,
    FunctionScope,
    GlobalScope,
    ImportAssignment,
    QualifiedName,
    QualifiedNameSource,
    Scope,
    ScopeProvider,
)
from viktor._vendor.libcst.metadata.span_provider import ByteSpanPositionProvider, CodeSpan
from viktor._vendor.libcst.metadata.type_inference_provider import TypeInferenceProvider
from viktor._vendor.libcst.metadata.wrapper import MetadataWrapper

__all__ = [
    "CodePosition",
    "CodeRange",
    "CodeSpan",
    "WhitespaceInclusivePositionProvider",
    "PositionProvider",
    "ByteSpanPositionProvider",
    "BaseMetadataProvider",
    "ExpressionContext",
    "ExpressionContextProvider",
    "BaseAssignment",
    "Assignment",
    "BuiltinAssignment",
    "ImportAssignment",
    "BuiltinScope",
    "Access",
    "Scope",
    "GlobalScope",
    "FunctionScope",
    "ClassScope",
    "ComprehensionScope",
    "ScopeProvider",
    "ParentNodeProvider",
    "QualifiedName",
    "QualifiedNameSource",
    "MetadataWrapper",
    "BatchableMetadataProvider",
    "VisitorMetadataProvider",
    "QualifiedNameProvider",
    "FullyQualifiedNameProvider",
    "ProviderT",
    "Assignments",
    "Accesses",
    "TypeInferenceProvider",
    "FullRepoManager",
    "AccessorProvider",
    # Experimental APIs:
    "ExperimentalReentrantCodegenProvider",
    "CodegenPartial",
]
