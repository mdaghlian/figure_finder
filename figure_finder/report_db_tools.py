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

from .figure_db_tools import listish_str_to_list, check_string_for_substring, FIG_clean_csv

# Get the directory where the databases (figure, and report) are stored as csvs 
report_dump = os.environ['FIG_DUMP']
rep_tag_file = opj(report_dump, 'rep_tag_file.csv') 
report_dump_bin = opj(report_dump, 'recycle_bin')   

def REP_remove_csv_entries(rep_names2remove):
    '''REP_remove_csv_entries
    
    Function to remove reports from csv database
    Parameters
    ----------
    rep_names2remove: str, list
        list or str of figure name/s (as stored in the csv database) which should be remove. 
        The corresponding entries will be deleted, as well as the associated data (i.e., png, svg & txt files)
    ----------
    Returns
    ----------
    None    
    '''    
    if isinstance(rep_names2remove, str):
        rep_names2remove = [rep_names2remove]        

    report_db = REP_load_report_db()
    rep_name_list = report_db.name.copy()
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
            if os.path.exists(report_db['path'][i]):
                os.system(f"rm -R {report_db['path'][i]}") 
        else:
            entries_to_keep.append(i)

    new_report_db = report_db.loc[entries_to_keep].copy()

    REP_save_report_db(new_report_db)
    return None
    
def REP_load_report_db():
    '''REP_load_report_db
    
    Loads the pandas dataframe of info about saved reports
    with keys:
        report_db['name']           name of the report
        report_db['date']           date report was made,
        report_db['path']           path to report folder
        report_db['html_path']      path to html file of report
        report_db['tags']           list of tags associated with the report
        report_db['num_figs']       number of figures in the report
        report_db['report_id']      the unique random id for the report (used to concisely add an id to figures)              

    Parameters
    ----------
    None

    ----------
    Returns
    ----------
    report_db: pandas dataframe
    '''
    if os.path.exists(rep_tag_file):
        try:
            report_db = pd.read_csv(rep_tag_file)
            for i in range(len(report_db)):
                report_db['tags'][i] = listish_str_to_list(report_db['tags'][i])
        except:
            # If all entries have been deleted - reload as empty dict
            report_db = []                
            
    else: 
        report_db = []    
    
    return report_db

def REP_save_report_db(report_db):
    '''REP_save_report_db
    
    Saves an updated version of the csv database         

    Parameters
    ----------
    report_db is a pandas dataframe with keys
        report_db['name']           name of the report
        report_db['date']           date report was made,
        report_db['path']           path to report folder
        report_db['html_path']      path to html file of report
        report_db['tags']           list of tags associated with the report
        report_db['num_figs']       number of figures in the report
        report_db['report_id']      the unique random id for the report (used to concisely add an id to figures)              
    ----------
    Returns
    ----------
    None        
    '''        
    report_db.to_csv(rep_tag_file, index=False)

    return None

def REP_remove_rep_with_tags(rep_tags, rep_name=[], exclude=None):
    '''REP_remove_rep_with_tags
    
    Function to remove reports which match a certain pattern
    >> this will delete there entries in the csv database, and also delete the corresponding file

    Parameters
    ----------
    rep_tags: list, str
        include reports which have these tags
    rep_name: str 
        include reports with this name (easier to be more specific, if you know the exact file
        you want removed)
    exclude: list, str
        do *NOT* include reports which have these tags
    ----------
    Returns
    ----------
    None

    '''
    # Match using tags (include & exclude)      
    rep_db_match = REP_find_rep_with_tags(rep_tags, rep_name=rep_name, exclude=exclude)
    # Concatenate a list of report names
    match_rep_name = rep_db_match.name.copy()
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
    '''REP_find_rep_with_tags
    
    Function to find reports which match a certain pattern

    Parameters
    ----------
    rep_tags: list, str
        include reports which have these tags
    rep_name: str 
        include reports with this name (easier to be more specific, if you know the exact file
        you want removed)
    exclude: list, str    
        do *NOT* include figures which have these tags

    Returns 
    ---------
    report_db_TAG_MATCH: pandas dataframe, of matching entries

    '''        
    # Load tag file
    report_db = REP_load_report_db()
    rep_name_list = report_db.name.copy()
    # check rep names 
    if rep_name!=[]:
        match_rep_names_idc = check_string_for_substring(filt=rep_name, str2check=rep_name_list, exclude=None)
        print(f'found {len(match_rep_names_idc)} files with this name')
    else: 
        print(f'rep name not specified, looking at all reps')
        match_rep_names_idc = np.arange(0,len(rep_name_list))

    report_db_NAME_MATCH = report_db.loc[match_rep_names_idc].copy()
    # [1] Get a list of possible file paths, names, and turn the tags into one string
    match_rep_tags = [' '.join(report_db[i]['tags']) for i in match_rep_names_idc]            
    match_idc = check_string_for_substring(filt=rep_tags, str2check=match_rep_tags, exclude=exclude)
    report_db_TAG_MATCH = report_db_NAME_MATCH.loc[match_idc].copy()

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
        
    this_pd_entry = {
        'date'      : [ff_Rep_object.date],
        'name'      : [ff_Rep_object.name],
        'path'      : [ff_Rep_object.path],
        'html_path' : [ff_Rep_object.html_path],
        'tags'      : [rep_tags],
        'num_figs'  : [ff_Rep_object.num_figs],
        'report_id' : [ff_Rep_object.report_id],
    }    
    
    # Load csv...
    report_db = REP_load_report_db()
    new_row = pd.DataFrame(this_pd_entry)
    new_report_db = pd.concat([new_row, report_db.loc[:]]).reset_index(drop=True)
    REP_save_report_db(new_report_db)

    return


def REP_find_rep_by_date():
    # Load tag file
    report_db = REP_load_report_db()
    rep_date_list = report_db.date.copy()
    # only want 
    print(rep_date_list)
    return 



def REP_clean_csv():
    if not os.path.exists(rep_tag_file):
        print('Figure finder: NO CSV FILE')
        return
    report_db = REP_load_report_db()
    if len(report_db)==0:
        print('Figure finder: Database is empty')
        return

    rep_path_list = report_db.path.copy()
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
    new_report_db = report_db.loc[entries_to_keep]
    REP_save_report_db(new_report_db)
    
    # Now clean figure database
    FIG_clean_csv()
    return  
