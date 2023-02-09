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
import pandas as pd

from .database_tools import save_fig_and_code_as_svg, get_figure_name, sanitise_string
from .report_db_tools import REP_remove_csv_entries, REP_add_rep_to_db, REP_load_report_db

with open(opj(os.path.dirname(os.path.realpath(__file__)), 'figure_dump_dir.txt')) as f:
    figure_dump = f.read().splitlines()[0]
csv_tag_file = opj(figure_dump, 'csv_tag_file.csv')
figure_dump_bin = opj(figure_dump, 'recycle_bin')

class ReportMaker(object):
    """Model

    Class that takes care of generating grids for pRF fitting and simulations
    """

    def __init__(self, file_name, file_path, report_overwrite='o', rep_tags=[], open_html=True):
        """__init__

        Constructor for report maker.

        """                
        self.file_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.file_name = file_name
        self.file_path = os.path.abspath(opj(file_path, file_name))
        self.html_path = os.path.abspath(opj(self.file_path, file_name+'.html')) 
        self.img_path = os.path.abspath(opj(self.file_path, 'images'))
        self.rep_tags = rep_tags
        self.open_html = open_html

        # -> add the report name to rep tags
        self.rep_tags += self.file_name.split('_')
        self.num_figs = 0

        if os.path.exists(self.file_path):
            print('FOLDER ALREADY EXISTS!')
            if report_overwrite!=None:
                save_instruction=report_overwrite
            else:
                print('Overwrite ? ("o")')
                print('Skip ? ("s")')
                print('Save copy with date ? ("d")')
                print('To automatically choose one of these options edit "fig_overwrite" argument')
                save_instruction = input()
            if save_instruction=="o":
                # Overwrite - > delete the old version
                print('Overwriting')
                try: 
                    REP_remove_csv_entries(self.file_name)
                except:
                    print(f'Could not remove {self.file_name} from csv database...' )
                    print(f'carrying on...' )
            elif save_instruction=='s':
                print('Not saving - skipping')
                return
            elif save_instruction=='d':
                print('Adding date to fig name to remove conflict...')
                date_now = self.file_date
                file_name = file_name + '_' + date_now
                self.file_name = file_name
                self.file_path = os.path.abspath(opj(file_path, file_name))
                self.html_path = os.path.abspath(opj(self.file_path, file_name+'.html')) 
                self.img_path = os.path.abspath(opj(self.file_path, 'images'))
                self.num_figs = 0                
        
        # Create report id 
        REP_db = REP_load_report_db()
        list_of_existing_ids = [REP_db[i]['report_id'] for i in range(len(REP_db))]
        letters = string.ascii_letters
        string_length = 6
        new_rep_id = ''.join(random.choice(letters) for i in range(string_length))
        while new_rep_id in list_of_existing_ids:
            new_rep_id = ''.join(random.choice(letters) for i in range(string_length))
        self.report_id = new_rep_id

        if not os.path.exists(self.file_path):
            print('Making folder')
            os.mkdir(self.file_path)
        if not os.path.exists(self.img_path):
            os.mkdir(self.img_path)
                
        # Start txt document
        self.txt_doc = '<!DOCTYPE html>\n<html>\n<body>\n'

    # *********************************************************************
    # ****************************** LOGGING ******************************
    # *********************************************************************
    def __enter__(self):

        self.old_stdout = sys.stdout
        
        self.log_file = open(opj(self.file_path, 'report.log'), 'w') 
        sys.stdout = self.log_file

    def __exit__(self,exc_type, exc_val, exc_tb):

        if exc_val:
            self.add_title('***ERROR***')
            self.add_text(exc_type.__name__)                                    # type
            self.add_text(f'In file: {exc_tb.tb_frame.f_code.co_filename}')     # filename
            self.add_text(f'At line: {exc_tb.tb_lineno}')                       # lineno

        sys.stdout = self.old_stdout
        self.log_file.close()
        self.save_html()

        if self.open_html:
            os.system(f'firefox {self.html_path}')
    # *********************************************************************
    # ****************************** LOGGING ******************************
    # *********************************************************************        

    def add_title(self, text, level=1):
        print(text)
        self.txt_doc += f'\n<h{level}>\n{text}\n</h{level}>\n'
        # Add text to tags...
        self.rep_tags += sanitise_string(text).split('_')

    def add_text(self, text):
        """
        Add text to string 
        """
        # scipy fftconvolve does not have padding options so doing it manually
        print(text)
        self.txt_doc += f'\n<p>{text}</p>\n'
        self.rep_tags += sanitise_string(text).split('_')
    
    def add_img(self, path_or_fig, fig_tags=[]):
        
        if isinstance(path_or_fig, mpl.figure.Figure):
            extracted_fig_name = get_figure_name(path_or_fig, '', '')            
            fig_name = f'{self.report_id}_fig{self.num_figs:03d}_{extracted_fig_name}'
            print(fig_name)
            print(path_or_fig)
            db_entry = save_fig_and_code_as_svg(
                path_or_fig, 
                fig_tags=[self.file_name], # Add report name to fig tags
                fig_name=fig_name, 
                save_folder=self.img_path, 
                fig_overwrite='o', 
                return_db_entr=True)
            print(db_entry)
            self.rep_tags += db_entry['tags']
            self.txt_doc += f'\n<img src="{opj("./images", fig_name+".svg")}" >'
            self.num_figs += 1
        else:
            self.txt_doc += f'\n<img src="{path_or_fig}" >\n'
            self.num_figs += 1
    
    def save_html(self):
        self.txt_doc += '\n</body>\n</html>'
        text_file = open(self.html_path, "w")
        text_file.write(self.txt_doc)
        text_file.close()

        REP_add_rep_to_db(self)