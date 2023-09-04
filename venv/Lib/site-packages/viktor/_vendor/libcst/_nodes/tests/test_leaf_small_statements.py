# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import viktor._vendor.libcst as cst
from viktor._vendor.libcst._nodes.tests.base import CSTNodeTest
from viktor._vendor.libcst.testing.utils import data_provider


class LeafSmallStatementsTest(CSTNodeTest):
    @data_provider(
        ((cst.Pass(), "pass"), (cst.Break(), "break"), (cst.Continue(), "continue"))
    )
    def test_valid(self, node: cst.CSTNode, code: str) -> None:
        self.validate_node(node, code)
