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
from .report_db_tools import REP_remove_csv_entries, REP_add_rep_to_db, REP_load_report_db

class ReportMaker(object):
    """

    Class that helps print reports to html, and save them in the ff database
    """

    def __init__(self, name, path, report_overwrite='ow', rep_tags=[], open_html=True, demo_mode=False):
        """__init__

        Constructor for report maker.

        """                
        self.date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.name = name
        self.path = os.path.abspath(opj(path, name))
        self.html_path = os.path.abspath(opj(self.path, name+'.html')) 
        self.img_path = os.path.abspath(opj(self.path, 'images'))
        self.rep_tags = rep_tags
        self.open_html = open_html
        self.demo_mode = demo_mode
        self.html_saved = False        
        # -> add the report name to rep tags
        self.rep_tags += self.name.split('_')
        self.num_figs = 0
        if self.demo_mode:
            return
        if os.path.exists(self.path):
            print('FOLDER ALREADY EXISTS!')
            if report_overwrite!=None:
                save_instruction=report_overwrite
            else:
                print('Overwrite ? ("ow")')
                print('Skip ? ("skip")')
                print('Save copy with date ? ("date")')
                print('To automatically choose one of these options edit "fig_overwrite" argument')
                save_instruction = input()
            if save_instruction=="ow":
                # Overwrite - > delete the old version
                print('Overwriting')
                try: 
                    REP_remove_csv_entries(self.name)
                except:
                    print(f'Could not remove {self.name} from csv database...' )
                    print(f'carrying on...' )
            elif save_instruction=='skip':
                print('Not saving - skipping')
                return
            elif save_instruction=='date':
                print('Adding date to fig name to remove conflict...')
                date_now = self.date
                name = name + '_' + date_now
                self.name = name
                self.path = os.path.abspath(opj(path, name))
                self.html_path = os.path.abspath(opj(self.path, name+'.html')) 
                self.img_path = os.path.abspath(opj(self.path, 'images'))
                self.num_figs = 0                
        
        # Create report id 
        REP_db = REP_load_report_db()
        list_of_existing_ids = REP_db['report_id'].copy()
        letters = string.ascii_letters
        string_length = 6
        new_rep_id = ''.join(random.choice(letters) for i in range(string_length))
        while new_rep_id in list_of_existing_ids:
            new_rep_id = ''.join(random.choice(letters) for i in range(string_length))
        self.report_id = new_rep_id

        if not os.path.exists(self.path):
            print('Making folder')
            os.mkdir(self.path)
        if not os.path.exists(self.img_path):
            os.mkdir(self.img_path)
                
        # Start txt document
        self.txt_doc = '<!DOCTYPE html>\n<html>\n<body>\n'

    # *********************************************************************
    # ****************************** LOGGING ******************************
    # *********************************************************************
    def __enter__(self):
        if self.demo_mode:
            return

        self.old_stdout = sys.stdout
        
        self.log_file = open(opj(self.path, 'report.log'), 'w') 
        sys.stdout = self.log_file

    def __exit__(self,exc_type, exc_val, exc_tb):
        if self.demo_mode:
            return

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
        if self.demo_mode:
            return
        self.txt_doc += f'\n<h{level}>\n{text}\n</h{level}>\n'
        # Add text to tags...
        self.rep_tags += sanitise_string(text).split('_')

    def add_text(self, text):
        """
        Add text to string 
        """
        # scipy fftconvolve does not have padding options so doing it manually
        print(text)
        if self.demo_mode:
            return
        self.txt_doc += f'\n<p>{text}</p>\n'
        self.rep_tags += sanitise_string(text).split('_')
    
    def add_img(self, path_or_fig, fig_tags=[]):
        if self.demo_mode:        
            plt.show(block=True)
            plt.pause(0.001)
            # plt.figure(1)           
            return
        
        if isinstance(path_or_fig, mpl.figure.Figure):
            extracted_fig_name = FIG_get_figure_name(path_or_fig, '', '')            
            fig_name = f'fig{self.num_figs:03d}_{extracted_fig_name}'
            print(fig_name)
            print(path_or_fig)
            db_entry = FIG_save_fig_and_code_as_svg(
                path_or_fig, 
                fig_tags=fig_tags + [self.name, self.report_id], # Add report name to fig tags
                fig_name=fig_name, 
                save_folder=self.img_path, 
                fig_overwrite='ow', 
                return_db_entr=True)
            print(db_entry)
            self.rep_tags += db_entry['tags']
            self.txt_doc += f'\n<img src="{opj("./images", fig_name+".svg")}" >'
            self.num_figs += 1
        else:
            self.txt_doc += f'\n<img src="{path_or_fig}" >\n'
            self.num_figs += 1
    
    def save_html(self):
        if self.demo_mode:
            return
        if self.html_saved:
            return
        else:
            self.txt_doc += '\n</body>\n</html>'
            text_file = open(self.html_path, "w")
            text_file.write(self.txt_doc)
            text_file.close()
            REP_add_rep_to_db(self)
            self.html_saved = True