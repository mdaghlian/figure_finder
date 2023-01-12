import os
opj = os.path.join

from datetime import datetime
import inspect
import numpy as np
import sys
import re

# MATPLOTLIB STUFF
import matplotlib as mpl
import pandas as pd

from .database_tools import listish_str_to_list, check_string_for_substring

with open(opj(os.path.dirname(os.path.realpath(__file__)), 'figure_dump_dir.txt')) as f:
    report_dump = f.read().splitlines()[0]
rep_tag_file = opj(report_dump, 'rep_tag_file.csv')
report_dump_bin = opj(report_dump, 'recycle_bin')

def REP_remove_csv_entries(rep_names2remove):
    if isinstance(rep_names2remove, str):
        rep_names2remove = [rep_names2remove]        

    report_db = REP_load_report_db()
    rep_name_list = [report_db[i]['file_name'] for i in range(len(report_db))]     
    # [1] Create a backup
    back_up_name = 'REP_backup_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.csv'
    back_up_file = opj(report_dump_bin, back_up_name)
    os.system(f'cp {rep_tag_file} {back_up_file}')  
    # [2] Compare reports listed in the csv with reports listed in the folder...
    # -> move to recycle bin
    entries_to_keep = []
    for i, this_rep in enumerate(rep_name_list):
        if this_rep in rep_names2remove:
            print(f'deleting {this_rep}')
            # Remove folder
            if os.path.exists(report_db[i]['file_path']):
                os.system(f"rm -R {report_db[i]['file_path']}") 
        else:
            entries_to_keep.append(i)
    new_report_db = []
    for i in entries_to_keep:
        new_report_db += [report_db[i]]

    REP_save_report_db(new_report_db)
    return None
    
def REP_load_report_db():
    if os.path.exists(rep_tag_file):
        try:
            rep_dict_dict = pd.read_csv(rep_tag_file).to_dict('index')
            # Loads a dictionary with first set of keys as 0,1,2,3... 
            # -> change this to be a list of dictionaries...
            report_db = []
            for key_idx in rep_dict_dict.keys():
                report_db += [rep_dict_dict[key_idx]]   
            # Now fix the loading of the tags, which load as a listish_string...
            for i in range(len(report_db)):
                report_db[i]['rep_tags'] = listish_str_to_list(report_db[i]['rep_tags'])
        except:
            # If all entries have been deleted - reload as empty dict
            report_db = []                
            
    else: 
        report_db = []    
    
    return report_db

def REP_save_report_db(report_db):
    df = pd.DataFrame(report_db)
    df.to_csv(rep_tag_file, index=False)

    return None

def REP_remove_rep_with_tags(rep_tags, rep_name=[], exclude=None, save_folder=report_dump):
    rep_db_match = REP_find_rep_with_tags(rep_tags, rep_name=rep_name, exclude=exclude)
    match_rep_name = [rep_db_match[i]['file_name'] for i in range(len(rep_db_match))]

    print(f'Found {len(match_rep_name)} files match')
    for this_rep in match_rep_name:
        print(this_rep)
    print(f'Found {len(match_rep_name)} files match')
    print(f'Do you want to delete ALL OF them? (y/n)')
    delete_files = input()
    if delete_files!='y':
        print('Cancelling deletion')
        return
    
    print('Are you absolutely sure? (y/n)')
    delete_sure = input()
    if delete_sure!='y':
        print('Cancelling deletion')
        return
    
    if delete_sure=='y':
        REP_remove_csv_entries(match_rep_name)

    return None


def REP_find_rep_with_tags(rep_tags, rep_name=[], exclude=None):
    # Load tag file
    report_db = REP_load_report_db()
    rep_name_list = [report_db[i]['file_name'] for i in range(len(report_db))] 
    # check rep names 
    if rep_name!=[]:
        match_rep_names_idc = check_string_for_substring(filt=rep_name, str2check=rep_name_list, exclude=None)
        print(f'found {len(match_rep_names_idc)} files with this name')
    else: 
        print(f'rep name not specified, looking at all reps')
        match_rep_names_idc = np.arange(0,len(rep_name_list))

    report_db_NAME_MATCH = [report_db[i] for i in match_rep_names_idc]
    # [1] Get a list of possible file paths, names, and turn the tags into one string
    match_rep_tags = [' '.join(report_db[i]['rep_tags']) for i in match_rep_names_idc]            
    match_idc = check_string_for_substring(filt=rep_tags, str2check=match_rep_tags, exclude=exclude)
    report_db_TAG_MATCH = [report_db_NAME_MATCH[i] for i in match_idc]

    return report_db_TAG_MATCH

def REP_add_rep_to_db(ff_Rep_object):
    # [1] Add the text from the document to the tags
    rep_tags = []
    rep_tags += ff_Rep_object.rep_tags
    txt_doc_no_html = re.sub('<[^>]+>', '', ff_Rep_object.txt_doc)
    txt_doc_no_newline = re.sub('\n', '', txt_doc_no_html)
    rep_tags += [txt_doc_no_newline] 
    # Split up tags with spaces in them...
    split_rep_tags = []
    for tag in rep_tags:
        split_rep_tags += tag.split()
    rep_tags = split_rep_tags
    # Remove duplicates
    rep_tags = list(set(rep_tags))
        
    this_db_entry = {
        'file_date' : ff_Rep_object.file_date,
        'file_name' : ff_Rep_object.file_name,
        'file_path' : ff_Rep_object.file_path,
        'html_path' : ff_Rep_object.html_path,
        'rep_tags' : rep_tags,
        'num_figs' : ff_Rep_object.num_figs,
        'report_id': ff_Rep_object.report_id,
    }

    # Load csv...
    report_db = REP_load_report_db()
    report_db += [this_db_entry]
    REP_save_report_db(report_db)

    return


def REP_find_rep_by_date():
    # Load tag file
    report_db = REP_load_report_db()
    rep_date_list = [report_db[i]['file_date'] for i in range(len(report_db))]
    # only want 
    print(rep_date_list)
    return 



def REP_clean_csv():
    if not os.path.exists(rep_tag_file):
        print('Figure finder: NO CSV FILE')
        return
    report_db = REP_load_report_db()
    if report_db==[]:
        print('Figure finder: Database is empty')
        return

    rep_path_list = [report_db[i]['file_path'] for i in range(len(report_db))]     
    # [1] Create a backup
    back_up_name = 'REP_backup_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.csv'
    back_up_file = opj(report_dump_bin, back_up_name)
    os.system(f'cp {rep_tag_file} {back_up_file}')  
    # [2] Check whether the reports still exist...
    entries_to_keep = []
    for i, this_rep in enumerate(rep_path_list):
        # check is 
        is_path = os.path.exists(this_rep)# in files_in_directory
        if not is_path:
            print(f'Could not find {this_rep}, in dir')            
            print('Deleting...')
        else:
            # print(f'*** COULD FIND ***{this_rep}')
            entries_to_keep.append(i)
    new_report_db = []
    for i in entries_to_keep:
        new_report_db += [report_db[i]]

    REP_save_report_db(new_report_db)
    return  
