import os
import sys
from distutils.core import setup
import cx_Freeze
import matplotlib 
matplotlib.use('Qt5Agg')

base = "Console"

os.environ['TCL_LIBRARY'] = r'C:\Users\khyeh\AppData\Local\Programs\Python\Python36-32\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\khyeh\AppData\Local\Programs\Python\Python36-32\tcl\tk8.6'
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"]=r'C:\Users\khyeh\Anaconda3\Library\plugins\platforms'

executable = [
    cx_Freeze.Executable("Dynamic Plotting.py", base = base)
]

build_exe_options = {"includes":["numpy.core._methods", "numpy.lib.format", "matplotlib.backends.backend_qt5agg"],
                     "include_files":[(matplotlib.get_data_path(), "mpl-data")],
                     }

cx_Freeze.setup(
    name = "Dynamic Plotting",
    options = {"build_exe": build_exe_options},
    version = "0.0",
    description = "standalone",
    executables = executable
)