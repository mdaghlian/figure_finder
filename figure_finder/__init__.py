import os
opj = os.path.join

from datetime import datetime
import numpy as np
import sys

# MATPLOTLIB STUFF
import matplotlib as mpl
import pandas as pd

# from .utils import *
# from .database_tools import *
# from .scrape_fig_info import *

from .database_tools import *
from .scrape_fig_info import *
from .utils import *

# Run the csv clean function
clean_csv()