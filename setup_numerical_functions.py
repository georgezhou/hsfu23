import functions
import string
import sys

cython_dir = functions.read_param_file("CYTHON_DIR")
print cython_dir
sys.path.append(cython_dir)

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension("spectype_numerical_functions", ["spectype_numerical_functions.pyx"])]
)
