import os
opj = os.path.join

from datetime import datetime
import numpy as np
import sys
import re
import string 
import random 
import inspect
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

    Help with figure saving...
    Specify at the beginning of the notebook where to save everything.. 
    just makes it easier
    """

    def __init__(self, name, path, save_mode = True, folder_ow=False, fig_ow='ow',  **kwargs):
        """__init__
        Will make the folder and set everything up...

        name            name of the folder 
        path            path (full where saved will path + name)
        save_mode       Do saving, or not...
        folder_ow       If folder already exists, ow?
        fig_ow          If fig exists, ow? 
                        'ow', 'skip', 'date',
        
        Optional
        fig_tags            If save w/ code add tags...
        save_*              Default save formats i.e., svg, png,...
        dpi                 Default dpi

        """                
        self.date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.name = name
        self.path = os.path.abspath(opj(path, name))
        self.save_mode = save_mode        
        self.fig_ow = fig_ow
        # Optional        
        self.fig_tags       = kwargs.get('fig_tags', [])
        
        # -> default formats to save 
        save_svg_w_code = kwargs.get('save_svg_w_code', True)
        save_svg = kwargs.get('save_svg', False)
        save_png = kwargs.get('save_png', False)
        save_eps = kwargs.get('save_eps', False)
        save_pdf = kwargs.get('save_pdf', False)
        self.save_type_dict = {
            'save_svg_w_code'   : save_svg_w_code,
            'save_svg'          : save_svg,
            'save_png'          : save_png,
            'save_eps'          : save_eps,
            'save_pdf'          : save_pdf,
        }
        self.dpi      = kwargs.get('dpi', 300)

        # -> Other useful defaults to put in...
        mpl.rcParams.update(mpl.rcParamsDefault)
        mpl.rcParams['pdf.fonttype'] = 42 # To work with adobe when saving .pdf
        mpl.rcParams['ps.fonttype'] = 42 # To work with adobe when saving .pdf
        mpl.rcParams['font.size'] = 10    # Default fontsize
        # mpl.rcParams['text.usetex'] = True
        mpl.rcParams['mathtext.default'] = 'regular' 
        # Set up saving folder...
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


    
    def add_img(self, fig, fig_name='', **kwargs):        
        '''add_img
        Save an image in the folder...

        fig         matplotlib figure
        fig_name    name of figure        
        '''
        if not self.save_mode:   # NOT SAVING!!!
            plt.show(block=True)
            plt.pause(0.001)    
            return
        
        # What format are we saving? Use defaults unless specified
        dpi         = kwargs.get('dpi', self.dpi)        
        save_type_dict = {}
        for save_key in self.save_type_dict.keys():
            save_type_dict[save_key] = kwargs.get(save_key, self.save_type_dict[save_key])           

        # Saving into a subfolder?
        sub_folder  = kwargs.get('sub_folder', None)
        if sub_folder is None:
            this_path = self.path
        else: 
            this_path = opj(self.path, sub_folder)
            if not os.path.exists(this_path):
                os.makedirs(this_path)

        # Make fig_name -> find from figure, or use default. keep option for adding the date
        fig_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')                
        fig_name,_ = FIG_get_figure_name(
            fig=fig, fig_name=fig_name, fig_date=fig_date,
            fig_folder=this_path, fig_ow=self.fig_ow
            )        

        for s_type in save_type_dict.keys():
            if (s_type=='save_svg_w_code') & (save_type_dict[s_type]):
                fig_tags = kwargs.get('fig_tags', []) # if save w code 
                db_entry = FIG_save_fig_and_code_as_svg(
                    fig, 
                    fig_tags=fig_tags + [self.name] + self.fig_tags, # Add overall name to fig tags
                    fig_name=fig_name, 
                    save_folder=this_path, 
                    fig_overwrite=self.fig_ow, 
                    return_db_entr=True)
                print(db_entry)

            elif save_type_dict[s_type]:
                fig_suffix = s_type.replace('save_', '')
                fig.savefig(
                    opj(this_path, f'{fig_name}.{fig_suffix}'), 
                    bbox_inches='tight', 
                    dpi=dpi,
                    transparent=True,
                    # backend= 'pgf' if s_type=='save_pdf' else None,
                    )
        
    
    def add_code_backup(self, bu_list=[], **kwargs):
        '''
        Function to add copies of the code that you depended on to make the figures
        i.e., if you are using a code that is likely to change...
        It will save a copy in the figure_save folder...
        
        bu_list     list of pacakges to save

        Optional:
        do_all_imports      save all the imports in the script
        just_this_cell       if running though notebook, just do this cell
        do_full_package     Save the full package (e.g., blah rather than just the file blah.submodule)
        
        '''
        if not self.save_mode: # NOT IN SAVE MODE -> quit      
            plt.pause(0.001)
            return
        
        do_all_imports = kwargs.get('do_all_imports', False)
        just_this_cell = kwargs.get('just_this_cell', True)
        do_full_package = kwargs.get('do_full_package', False)

        # make back up dir
        self.code_bu_dir = opj(self.path, 'code_bu_dir')
        if not os.path.exists(self.code_bu_dir):
            os.mkdir(self.code_bu_dir)

        if not isinstance(bu_list, list):
            bu_list = [bu_list]
        
        # Loop through...
        for bu_mod_str in bu_list:            
            self.save_bu_mod(bu_mod_str, do_full_package=do_full_package)

        # This cell... look at all the import lines in this cell...
        
        if not do_all_imports:
            return 
        # -> Get string for notebook cell or script
        # -> first find the path of the script / notebook
        try: # First try the method that works for noetbookes
            nb_path = get_ipython().get_parent()['metadata']['cellId']
            # e.g., 'vscode-notebook-cell:/data1/projects/dumoulinlab/Lab_members/Marcus/programs/figure_finder/example.ipynb#ch0000031'
            # So need to format it so that it is nice...
            nb_path = nb_path.split('cell:')[-1]        
            nb_path = nb_path.split('.ipynb')[0] + '.ipynb'
        except: 
            # Try the method that works for scripts...
            nb_path = inspect.stack()[1].filename
            # check that this isn't the just another figure_finder function
            if 'figure_saver' in nb_path:
                nb_path = inspect.stack()[2].filename        
        
        if just_this_cell:
            # Get the code from the cell that we are saving in...
            import_code_str = get_ipython().get_parent()['content']['code']
        else:
            f = open(nb_path, 'r')            
            import_code_str = f.read()   
        # Next check for the import strings
        import_code_str = import_code_str.split('\n') # Get the different lines
        extracted_bu_list = []
        for line in import_code_str:
            # Empty line ? pass
            if line=='':
                continue
            # Does it start with a '#'?
            if line.lstrip()[0]=='#':
                continue

            if (line.split()[0]=='import') or (line.split()[0]=='from'):
                extracted_bu_list.append(line.split()[1])
        for bu_mod_str in extracted_bu_list:
            self.save_bu_mod(bu_mod_str, do_full_package=do_full_package)
        

        return import_code_str
        

    def save_bu_mod(self, bu_mod_str, do_full_package=False):
        
        # Save the full package? Or just the specified file
        if do_full_package:
            bu_mod_str = bu_mod_str.split('.')[0] 
        
        # [2] Check, can we import it?
        try:
            bu_mod = importlib.import_module(bu_mod_str)
        except ImportError as e:
            print(f"Error importing {bu_mod_str}: {e}")
            return 
        
        # [3] Where copying from?
        bu_mod_file = bu_mod.__file__        
        bu_mod_file = bu_mod_file.replace('/__init__.py', '')
        if '.conda' in bu_mod_file:
            print(f'{bu_mod_str} is in .conda, not saving')
            return
        if 'figure_finder' in bu_mod_file:
            print(f'{bu_mod_str} is FIGURE FINDER! Not saving')
            return

        
        # [4] Make the output file
        bu_out_file = opj(self.code_bu_dir, bu_mod_str)
        if os.path.exists(bu_out_file):
            print('Deleting and remaking folder')
            os.system(f"rm -r {bu_out_file}")                     
            os.makedirs(bu_out_file)
        else:
            os.makedirs(bu_out_file)

        
        # Create a text file with info 
        with open(opj(bu_out_file, f'A0-{bu_mod_str}-ff-backup-info.txt'), 'w') as file:
            file.write(
                f'{bu_mod_str} copied on {self.date} from {bu_mod_file}'                
            )

        cmd1 = f'cp -r {bu_mod_file} {bu_out_file}'
        print(cmd1)
        os.system(cmd1)