import os
opj = os.path.join

from datetime import datetime
import numpy as np
import sys

# MATPLOTLIB STUFF
import matplotlib as mpl
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
os.environ['FIG_DUMP'] = '/data1/projects/dumoulinlab/Lab_members/Marcus/programs/figure_dump'

from .figure_db_tools import *
from .figure_saver import *
from .utils import *
from .report_printer import *
from .report_db_tools import *
from .report_collator import *
from .nb_to_html import *


REP_clean_csv()