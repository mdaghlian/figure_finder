import os
opj = os.path.join

from datetime import datetime
import numpy as np
import sys
import re
import string 
import random 

import logging
from contextlib import contextmanager

# MATPLOTLIB STUFF
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

from .figure_db_tools import FIG_save_fig_and_code_as_svg, FIG_get_figure_name, sanitise_string

class FigureSaver(object):
    """

    Class that allows you to either save or not save every image at the beginning
    """

    def __init__(self, name, path, save_mode = True, fig_overwrite='o', fig_tags=[], folder_ow=False):
        """__init__

        Constructor for report maker.

        """                
        self.date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.name = name
        self.path = os.path.abspath(opj(path))#, name))
        self.fig_tags = fig_tags
        self.save_mode = save_mode
        self.fig_overwrite = fig_overwrite
        # -> add the report name to rep tags
        # self.num_figs = 0
        if not self.save_mode:
            return

        if os.path.exists(self.path):
            print('FOLDER ALREADY EXISTS!')
            if folder_ow:
                # Overwrite - > delete the old version
                print('Deleting and remaking folder')
                os.system(f"rm -r {self.path}")                     
                os.mkdir(self.path)
            else:
                print('Not deleting...')        
    
    def add_img(self, fig, fig_name='', fig_tags=[], do_png=False, dpi=300, do_svg=True):
        if not self.save_mode:        
            plt.show(block=True)
            plt.pause(0.001)
            # plt.figure(1)           
            return
        
        fig_name = FIG_get_figure_name(fig, fig_name, '')            
        # fig_name = f'fig{self.num_figs:03d}_{extracted_fig_name}'
        if do_svg:
            db_entry = FIG_save_fig_and_code_as_svg(
                fig, 
                fig_tags=fig_tags + [self.name] + self.fig_tags, # Add overall name to fig tags
                fig_name=fig_name, 
                save_folder=self.path, 
                fig_overwrite='o', 
                return_db_entr=True)
            print(db_entry)
        if do_png:
            fig.savefig(
                opj(self.path, f'{fig_name}.png'),
                dpi=dpi)

        # self.num_figs += 1
