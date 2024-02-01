import os
opj = os.path.join

from datetime import datetime
import numpy as np
import sys
import re
import string 
import random 
import importlib

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

    def __init__(self, name, path, save_mode = True, fig_overwrite='ow', fig_tags=[], folder_ow=False, **kwargs):
        """__init__

        Constructor for report maker.

        name 

        """                
        self.date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.name = name
        self.path = os.path.abspath(opj(path))#, name))
        self.fig_tags = fig_tags
        self.save_mode = save_mode
        self.fig_overwrite = fig_overwrite
        self.save_svg = kwargs.get('save_svg', True)
        self.save_svg_basic = kwargs.get('save_svg_basic', False)
        self.save_png = kwargs.get('save_png', False)
        self.save_eps = kwargs.get('save_eps', False)
        self.save_pdf = kwargs.get('save_pdf', False)

        self.save_type_dict = {
            'save_svg' : self.save_svg,
            'save_svg_basic' : self.save_svg_basic,
            'save_png' : self.save_png,
            'save_eps' : self.save_eps,
            'save_pdf' : self.save_pdf,
        }
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
                os.makedirs(self.path)
            else:
                print('Not deleting...')        
        else:
            print('Making folder')
            os.makedirs(self.path)
    
    def add_img(self, fig, fig_name='', fig_tags=[], **kwargs):        
        dpi         = kwargs.get('dpi', 300)
        
        save_type_dict = {}
        save_type_dict['save_png']    = kwargs.get('save_png', self.save_type_dict['save_png'])
        save_type_dict['save_svg']    = kwargs.get('save_svg', self.save_type_dict['save_svg'])
        save_type_dict['save_svg_basic'] = kwargs.get('save_svg_basic', self.save_type_dict['save_svg_basic'])
        save_type_dict['save_eps']    = kwargs.get('save_eps', self.save_type_dict['save_eps'])
        save_type_dict['save_pdf']    = kwargs.get('save_pdf', self.save_type_dict['save_pdf'])

        sub_folder  = kwargs.get('sub_folder', None)
        
        if not self.save_mode:        
            plt.show(block=True)
            plt.pause(0.001)
            # plt.figure(1)           
            return

        if sub_folder is None:
            this_path = self.path
        else: 
            this_path = opj(self.path, sub_folder)
            if not os.path.exists(this_path):
                os.makedirs(this_path)

        fig_name = FIG_get_figure_name(fig, fig_name, '')            
        # fig_name = f'fig{self.num_figs:03d}_{extracted_fig_name}'

        for s_type in save_type_dict.keys():

            if (s_type=='save_svg') & (save_type_dict[s_type]):
                db_entry = FIG_save_fig_and_code_as_svg(
                    fig, 
                    fig_tags=fig_tags + [self.name] + self.fig_tags, # Add overall name to fig tags
                    fig_name=fig_name, 
                    save_folder=this_path, 
                    fig_overwrite='ow', 
                    return_db_entr=True)
                print(db_entry)

            elif (s_type=='save_svg_basic') & (save_type_dict[s_type]):
                fig.savefig(
                    opj(this_path, f'{fig_name}_BASIC.svg'), 
                    bbox_inches='tight', 
                    format='svg')

            elif (s_type=='save_png') & (save_type_dict[s_type]):
                fig.savefig(
                    opj(this_path, f'{fig_name}.png'),
                    bbox_inches='tight',
                    dpi=dpi)
            
            elif (s_type=='save_eps') & (save_type_dict[s_type]):
                fig.savefig(
                    opj(this_path, f'{fig_name}.eps'),
                    bbox_inches='tight',
                    dpi=dpi)        # self.num_figs += 1
            elif (s_type=='save_pdf') & (save_type_dict[s_type]):
                fig.savefig(
                    opj(this_path, f'{fig_name}.pdf'),
                    bbox_inches='tight',
                    dpi=dpi)        # self.num_figs += 1                
    
    def add_code_backup(self, bu_list=[], **kwargs):
        '''
        Function to add copies of the code that you depended on to make the figures
        i.e., if you are using a code that is likely to change...
        It will save a copy in the figure_save folder...
        
        bu_list     list of pacakges to save

        Optional:
        do_all_imports      save all the imports in the script
        just_thi_cell       if running though notebook, just do this cell
        do_full_package     Save the full package (e.g., blah rather than just the file blah.submodule)
        
        '''
        if not self.save_mode: # NOT IN SAVE MODE -> quit      
            plt.pause(0.001)
            return
        

        # make back up dir
        self.code_bu_dir = opj(self.path, 'code_bu_dir')
        if not os.path.exists(self.code_bu_dir):
            os.mkdir(self.code_bu_dir)

        if not isinstance(bu_list, list):
            bu_list = [bu_list]
        
        # Loop through...
        for bu_mod_str in bu_list:            
            self.save_bu_mod(bu_mod_str, **kwargs)

        # This cell... look at all the import lines in this cell...
        
        

    def save_bu_mod(self, bu_mod_str, **kwargs):
        
        # Save the full package? Or just the specified file
        do_full_package = kwargs.get('do_full_package', False) 
        if do_full_package:
            bu_mod_str = bu_mod_str.split('.')[0] 
        
        # [2] Check, can we import it?
        try:
            bu_mod = importlib.import_module(bu_mod_str)
        except ImportError as e:
            print(f"Error importing {bu_mod_str}: {e}")
            return 
        
        # [3] Make the output file
        bu_out_file = opj(self.code_bu_dir, bu_mod_str)
        if os.path.exists(bu_out_file):
            print('Deleting and remaking folder')
            os.system(f"rm -r {bu_out_file}")                     
            os.makedirs(bu_out_file)
        else:
            os.makedirs(bu_out_file)

        # [4] Where copying from?
        bu_mod_file = bu_mod.__file__        
        bu_mod_file = bu_mod_file.replace('/__init__.py', '')
        if '.conda' in bu_mod_file:
            print(f'{bu_mod_str} is in .conda, not saving')
            return
        
        # Create a text file with info 
        with open(opj(bu_out_file, f'A0-{bu_mod_str}-ff-backup-info.txt'), 'w') as file:
            file.write(
                f'{bu_mod_str} copied on {self.date} from {bu_mod_file}'                
            )

        cmd1 = f'cp -r {bu_mod_file} {bu_out_file}'
        print(cmd1)
        os.system(cmd1)