import os
import pwd
opj = os.path.join

from datetime import datetime
import numpy as np
import sys

# MATPLOTLIB STUFF
import matplotlib as mpl
import pandas as pd

from .figure_db_tools import FIG_find_fig_with_tags

figure_dump = os.environ['FIG_DUMP']

def print_matching_code_file(fig_tags, fig_name=[], exclude=None, save_folder=figure_dump, idx=[]):
    fig_db_match = FIG_find_fig_with_tags(fig_tags, fig_name=fig_name, exclude=exclude)
    match_fig_path = [fig_db_match[i]['path'] for i in range(len(fig_db_match))]
    match_fig_name = [fig_db_match[i]['name'] for i in range(len(fig_db_match))]
    
    if (len(match_fig_path)>1) & (idx==[]):
        print('More than 1 figs match the description')
        print('Be more specific or select the file, using idx=X, (or -i X)')
        print('Files found include:')
        for i,this_name in enumerate(match_fig_name):
            print(f'{i:03}, {this_name}')
        
        return # EXIT FUNCTION
    if idx!=[]:
        match_fig_path = match_fig_path[idx]
        match_fig_name = match_fig_name[idx]
    else:
        match_fig_path = match_fig_path[0]
        match_fig_name = match_fig_name[0]

    print(f"Opening {match_fig_name}")
    fig_code_path = match_fig_path
    f = open(fig_code_path+'.txt', 'r')            
    fig_code_text = f.read()
    f.close()
    print('')
    print('')
    print('****************** START OF FIGURE CODE ******************')
    print('**********************************************************')
    print(fig_code_text)        
    print('******************   END OF FIGURE CODE ******************')
    print('**********************************************************')            
    print('')
    print('')
    return None

def show_fig_with_tags(fig_tags, fig_name=[], exclude=None, save_folder=figure_dump, idx=[]):
    fig_db_match = FIG_find_fig_with_tags(fig_tags, fig_name=fig_name, exclude=exclude)
    match_fig_path = [fig_db_match[i]['path'] for i in range(len(fig_db_match))]
    match_fig_name = [fig_db_match[i]['name'] for i in range(len(fig_db_match))]

    if len(match_fig_path)>1:
        if idx==[]:
            print('More than 1 figs match the description')
            print('Be more specific or select the file, using idx=X (or -i X)')
            print('Files found include:')
            for i,this_name in enumerate(match_fig_name):
                print(f'{i:03}, {this_name}')
        elif idx=='all':
            for i,this_path in enumerate(match_fig_path):
                print(f'Opening {match_fig_name[i]}')
                os.system(f'eog {this_path}.svg & ')

        else:
            print(f'Opening {match_fig_name[idx]}')
            os.system(f'eog {match_fig_path[idx]}.svg & ')

    else:
        for i,this_path in enumerate(match_fig_path):
            print(f'Opening {match_fig_name[i]}')
            os.system(f'eog {this_path}.svg & ')
        

    return None
