import functions
from numpy import *

hscand_connect = functions.read_config_file("HSCAND_CONNECT")
default_teff = float(functions.read_config_file("TEFF_ESTIMATE"))
default_logg = float(functions.read_config_file("LOGG_ESTIMATE"))
print functions.estimate_teff_logg("HATS563-036",hscand_connect,default_teff,default_logg)
