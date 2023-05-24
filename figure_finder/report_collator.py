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

from .figure_db_tools import sanitise_string, check_string_for_substring
from .report_db_tools import REP_remove_csv_entries, REP_add_rep_to_db, REP_load_report_db, REP_find_rep_with_tags

class ReportCollator(object):
    """
    Class which collates from a set of reports: pulling the 
    
    """

    def __init__(self, file_name, file_path, report_overwrite='o', tags_incl=[], tags_excl=[], open_html=True):
        """__init__

        Constructor for report maker.

        """                
        self.file_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.file_name = file_name
        self.file_path = os.path.abspath(opj(file_path, file_name))
        self.html_path = os.path.abspath(opj(self.file_path, file_name+'.html')) 
        self.img_path = os.path.abspath(opj(self.file_path, 'images'))
        self.tags_incl = tags_incl
        self.tags_excl = tags_excl + ['collated']
        self.rep_tags = []
        self.rep_tags += ['collated']
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
        self.add_title(self.file_name)
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

    def add_text(self, text, font_size=None):
        """
        Add text to string 
        """
        # scipy fftconvolve does not have padding options so doing it manually
        print(text)
        if font_size is not None:
            self.txt_doc += f'\n<p style="font-size:{font_size}px;>{text}</p>\n'    
        self.txt_doc += f'\n<p>{text}</p>\n'
        self.rep_tags += sanitise_string(text).split('_')

    def begin_collation(self, **kwargs):
        # img_order = kwargs.get('image_order', 'REP') # REP or fig

        # Get the name of matching reports:
        print(self.tags_incl)
        rep_match = REP_find_rep_with_tags(rep_tags=self.tags_incl, exclude=self.tags_excl)
        self.add_text(f'Collating from {[this_rep["file_name"] for this_rep in rep_match]}')
        # find the max number of figures:
        n_figs = [this_rep['num_figs'] for this_rep in rep_match]
        max_n_figs = np.max(n_figs)
        
        for i_fig in range(max_n_figs):
            self.add_title(f'fig{i_fig:03}', level=2)
            for this_rep in rep_match:
                this_img_path = opj(this_rep['file_path'], 'images')                
                this_img_list = os.listdir(this_img_path)
                this_img_id = list(check_string_for_substring(filt=[f'fig{i_fig:03}', '.svg'], str2check=this_img_list))[0]
                self.add_text(f'fig{i_fig:03}, {this_rep["file_name"]}')                
                this_img_name = this_img_list[this_img_id]
                this_new_path = opj(self.img_path, this_img_name)
                os.system(f'cp {opj(this_img_path, this_img_name)} {this_new_path}')
                self.txt_doc += f'\n<img src="{this_new_path}" >\n'
                self.num_figs += 1

            
        # if img_order=='REP':
            # 
        
        return
    
    def save_html(self):
        self.txt_doc += '\n</body>\n</html>'
        text_file = open(self.html_path, "w")
        text_file.write(self.txt_doc)
        text_file.close()

        REP_add_rep_to_db(self)