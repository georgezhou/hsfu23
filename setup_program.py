### Load python modules
import os

### Change permissions on csh files
os.system("chmod +x *.csh")
os.system("python setup_numerical_functions.py build_ext --inplace")
