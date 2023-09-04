import os
import sys

os.environ['LIBCST_PARSER_TYPE'] = 'native'  # to support parsing of Python 3.10 documents

# When LIBCST_PARSER_TYPE is set to 'native', a compiled libcst module will be used (libcst.native).
# This module internally imports 'libcst', which we cannot patch to _vendor.libcst. Since apps could
# have installed libcst, we have to override this imported module.
try:
    libcst_vendor = __import__('viktor._vendor', fromlist=['libcst']).libcst
    sys.modules['libcst'] = libcst_vendor
except AttributeError:  # during development: viktor._vendor has no attribute 'libcst'
    pass
