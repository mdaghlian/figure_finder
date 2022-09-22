import os
opj = os.path.join

from datetime import datetime
import numpy as np
import sys

# MATPLOTLIB STUFF
import matplotlib as mpl
import pandas as pd

from .scrape_fig_info import get_figure_name, scrape_tags_from_figure

with open(opj(os.path.dirname(os.path.realpath(__file__)), 'figure_dump_dir.txt')) as f:
    figure_dump = f.read().splitlines()[0]
csv_tag_file = opj(figure_dump, 'csv_tag_file.csv')
figure_dump_bin = opj(figure_dump, 'recycle_bin')


def clean_csv():
    if not os.path.exists(csv_tag_file):
        print('Figure finder: NO CSV FILE')
        return
    figure_db = load_figure_db()
    if figure_db==[]:
        print('Figure finder: Database is empty')
        return

    fig_name_list = [figure_db[i]['name'] for i in range(len(figure_db))]     
    # [1] Create a backup
    back_up_name = 'backup_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.csv'
    back_up_file = opj(figure_dump_bin, back_up_name)
    os.system(f'cp {csv_tag_file} {back_up_file}')  
    # [2] Compare figures listed in the csv with figures listed in the folder...
    files_in_directory = sorted(os.listdir(figure_dump))
    entries_to_keep = []
    for i, this_fig in enumerate(fig_name_list):
        # check is there a png?
        is_png = this_fig+'.png' in files_in_directory
        is_svg = this_fig+'.svg' in files_in_directory
        is_img = is_png | is_svg
        if not is_img:
            print(f'Could not find {this_fig}, in dir')            
            print('Deleting...')
        else:
            entries_to_keep.append(i)
    new_figure_db = []
    for i in entries_to_keep:
        new_figure_db += [figure_db[i]]

    save_figure_db(new_figure_db)
    return

def remove_csv_entries(fig_names2remove):
    if isinstance(fig_names2remove, str):
        fig_names2remove = [fig_names2remove]        

    figure_db = load_figure_db()
    fig_name_list = [figure_db[i]['name'] for i in range(len(figure_db))]     
    # [1] Create a backup
    back_up_name = 'backup_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.csv'
    back_up_file = opj(figure_dump_bin, back_up_name)
    os.system(f'cp {csv_tag_file} {back_up_file}')  
    # [2] Compare figures listed in the csv with figures listed in the folder...
    # -> move to recycle bin
    entries_to_keep = []
    for i, this_fig in enumerate(fig_name_list):
        if this_fig in fig_names2remove:
            print(f'deleting {this_fig}')
            # Check for png 
            extensions_to_delete = ['.png', '.txt', '.svg']
            for this_ext in extensions_to_delete:
                if os.path.exists(figure_db[i]['path'] + this_ext):
                    os.system(f"mv {figure_db[i]['path'] + this_ext} {opj(figure_dump_bin, this_fig + this_ext)}") 
        else:
            entries_to_keep.append(i)
    new_figure_db = []
    for i in entries_to_keep:
        new_figure_db += [figure_db[i]]

    save_figure_db(new_figure_db)
    return None

def listish_str_to_list(listish_str):
    chars_to_remove = ['[', ']', '"', "'", ' ']
    for this_rm in chars_to_remove:
        listish_str = listish_str.replace(this_rm, '')
    # Now split at the commas
    return listish_str.split(',')
    
def load_figure_db():
    if os.path.exists(csv_tag_file):
        try:
            tag_dict_dict = pd.read_csv(csv_tag_file).to_dict('index')
            # Loads a dictionary with first set of keys as 0,1,2,3... 
            # -> change this to be a list of dictionaries...
            figure_db = []
            for key_idx in tag_dict_dict.keys():
                figure_db += [tag_dict_dict[key_idx]]   
            # Now fix the loading of the tags, which load as a listish_string...
            for i in range(len(figure_db)):
                figure_db[i]['tags'] = listish_str_to_list(figure_db[i]['tags'])
        except:
            # If all entries have been deleted - reload as empty dict
            figure_db = []                
            
    else: 
        figure_db = []    
    
    return figure_db

def save_figure_db(figure_db):
    df = pd.DataFrame(figure_db)
    df.to_csv(csv_tag_file, index=False)

    return None

def remove_fig_with_tags(fig_tags, fig_name=[], exclude=None, save_folder=figure_dump):
    fig_db_match = find_fig_with_tags(fig_tags, fig_name=fig_name, exclude=exclude)
    match_fig_name = [fig_db_match[i]['name'] for i in range(len(fig_db_match))]

    print(f'Found {len(match_fig_name)} files match')
    for this_fig in match_fig_name:
        print(this_fig)
    print(f'Found {len(match_fig_name)} files match')
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
        remove_csv_entries(match_fig_name)

    return None



def find_fig_with_tags(fig_tags, fig_name=[], exclude=None):
    # Load pkl tag file
    figure_db = load_figure_db()
    fig_name_list = [figure_db[i]['name'] for i in range(len(figure_db))] 
    # check fig names 
    if fig_name!=[]:
        match_fig_names_idc = check_string_for_substring(filt=fig_name, str2check=fig_name_list, exclude=None)
        # match_fig_names = [figure_db[i]['name'] for i in ] 
        print(f'found {len(match_fig_names_idc)} files with this name')
    else: 
        print(f'fig name not specified, looking at all figs')
        match_fig_names_idc = np.arange(0,len(fig_name_list))

    figure_db_NAME_MATCH = [figure_db[i] for i in match_fig_names_idc]
    # [1] Get a list of possible file paths, names, and turn the tags into one string
    match_fig_tags = [' '.join(figure_db[i]['tags']) for i in match_fig_names_idc]            
    match_idc = check_string_for_substring(filt=fig_tags, str2check=match_fig_tags, exclude=exclude)
    figure_db_TAG_MATCH = [figure_db_NAME_MATCH[i] for i in match_idc]
    # match_fig_path = [match_fig_path[i] for i in match_idc]
    # match_fig_name = [match_fig_name[i] for i in match_idc]
    # match_fig_tags = [match_fig_tags[i] for i in match_idc]

    return figure_db_TAG_MATCH

# Copied from J Heijs Linescanning toolbox...
def check_string_for_substring(filt, str2check, exclude=None):    
    if isinstance(filt, str):
        filt = [filt]

    if isinstance(filt, list):
        # list and sort all files in the directory
        if isinstance(str2check, str):
            str2check = [str2check]
        if isinstance(exclude, str):
            exclude = [exclude]
        # the idea is to create a binary matrix for the strings, loop through the filters, and find the row where all values are 1
        filt_array = np.zeros((len(str2check), len(filt)))
        for ix,f in enumerate(str2check):
            for filt_ix,filt_opt in enumerate(filt):
                filt_array[ix,filt_ix] = filt_opt in f

        if exclude!=None:
            excl_array = np.zeros((len(str2check), len(exclude)))
            for ix,f in enumerate(str2check):
                for excl_ix,excl_opt in enumerate(exclude):
                    excl_array[ix,excl_ix] = excl_opt in f
        else: 
            excl_array = np.zeros((len(str2check), 1))
        excl_match_idx = excl_array.sum(-1)==0

        # now we have a binary <number of files x number of filters> array. If all filters were available in a file, the entire row should be 1, 
        # so we're going to look for those rows
        full_match = np.ones(len(filt))
        full_match_idx = np.all(filt_array==full_match,axis=1)
        full_match_idx &= excl_match_idx
        full_match_idc = np.where(full_match_idx)[0]
    
    if len(full_match_idc)==0:
        raise FileNotFoundError(f"Could not find fig with tags: {filt}")
    return full_match_idc


def save_figure_with_tags(fig, fig_tags=[], fig_name='', save_folder=figure_dump, **kwargs):
    # GET PARAMETERS....
    # dpi = kwargs.get("dpi", 70)    
    save_folder = kwargs.get("save_folder", figure_dump)    
    extract_tags = kwargs.get("extract_tags", True)
    proj = kwargs.get("proj", None)
    save_cwd = kwargs.get("save_cwd", True)
    save_cell_code = kwargs.get("save_cell_code", True)
    save_nb_path = kwargs.get("save_nb_path", True)
    fig_overwrite = kwargs.get("fig_overwrite", None) ### *** CHANGE THIS TO AUTOMATICALLY OVERWRITE OR NOT...***
    if not os.path.exists(save_folder):
        os.mkdir(save_folder)
    #
    if proj==None:
        proj_str = ''
    else:
        proj_str = f'proj-{proj}'
    fig_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    fig_name = get_figure_name(fig, fig_name, fig_date=fig_date)
    # *** CHECK WHETHER THE FILE ALREADY EXISTS ***
    files_in_directory = sorted(os.listdir(figure_dump))
    if (fig_name+'.svg' in files_in_directory) or (fig_name+'.png' in files_in_directory):
        print(f'{fig_name} already exists...')
        if fig_overwrite!=None:
            save_instruction=fig_overwrite
        else:
            print('Overwrite ? ("o")')
            print('Skip ? ("s")')
            print('Save copy with date ? ("d")')
            print('To automatically choose one of these options edit "fig_overwrite" argument in utils.save_figure_with_tags')
            save_instruction = input()
        if save_instruction=="o":
            # Overwrite - > delete the old version
            remove_csv_entries(fig_name)
        elif save_instruction=="s":
            # SKIPPING
            print('Not saving - skipping')
            return
        elif save_instruction=="d":
            print('Adding date to fig name to remove conflict...')
            fig_name = fig_name + '_' + fig_date

    if extract_tags:
        fig_tags = scrape_tags_from_figure(fig, fig_tags=fig_tags)
    
    fig_path = opj(save_folder, f'{proj_str}{fig_name}')
    # Add figure name & date to tags...
    fig_tags += [fig_name]
    fig_tags += [fig_date]
    # get them from the figure


    if save_cwd:
        fig_cwd = os.getcwd()
    else:
        fig_cwd = ''

    if save_nb_path:
        # Comes in complex string form...
        notebook_path = get_ipython().get_parent()['metadata']['cellId']
        # e.g., 'vscode-notebook-cell:/data1/projects/dumoulinlab/Lab_members/Marcus/programs/figure_finder/example.ipynb#ch0000031'
        # So need to format it so that it is nice...
        notebook_path = notebook_path.split('cell:')[-1]        
        notebook_path = notebook_path.split('.ipynb')[0] + '.ipynb'
    else:
        notebook_path = ''

    if save_cell_code:
        # Get the code from the cell that we are saving in...
        cell_code_str = get_ipython().get_parent()['content']['code']
        cell_code_path = fig_path + '.txt'
        text_file = open(cell_code_path, "w")
        text_file.write(cell_code_str)
        text_file.close()        
        
    this_db_entry = {
        'name' : fig_name,
        'date' : fig_date,
        'path' : fig_path,
        'tags' : fig_tags,
        'cwd' : fig_cwd,
        'nb_path' : notebook_path,        
    }
    # Now save as an svg -> including all the 
    save_fig_and_code_as_svg(fig, fig_dict=this_db_entry, cell_code_str=cell_code_str)
    # Load csv...
    figure_db = load_figure_db()
    figure_db += [{
        'name' : fig_name,
        'date' : fig_date,
        'path' : fig_path,
        'tags' : fig_tags,
        'cwd' : fig_cwd,
        'nb_path' : notebook_path,
    }]
    save_figure_db(figure_db)

    return


def save_fig_and_code_as_svg(fig, fig_dict, cell_code_str):
    # [1] Save as svg
    fig.savefig(fig_dict['path']+'.svg', bbox_inches='tight', format='svg')

    svg_file = fig_dict['path']+'.svg'
    # [2] Create string to add to the svg...
    svg_insert = ["<text>"]
    svg_insert += ["<!--"]
    svg_insert += ["*********** START - info inserted by figure finder ********"]
    svg_insert += ["***********************************************************"]
    svg_insert += ["***********************************************************"]    
    svg_insert += [f'DATE : {fig_dict["date"]}']
    svg_insert += [f'FIGURE NAME: {fig_dict["name"]}']
    svg_insert += [f'FIGURE CWD: {fig_dict["cwd"]}']
    svg_insert += [f'NOTEBOOK: {fig_dict["nb_path"]}']
    tag_str = ','.join(fig_dict['tags'])
    svg_insert += [f'TAGS: {tag_str}']
    svg_insert += ["***********************************************************"]    
    svg_insert += ["********* CODE FROM NB CELL USED TO MAKE FIG **************"]    
    svg_insert += [cell_code_str]
    svg_insert += ["***********************************************************"]
    svg_insert += ["***********************************************************"]    
    svg_insert += ["************* END - info inserted by figure finder ********"]
    svg_insert += ["-->"]
    svg_insert += ["</text>"]    
    
    svg_insert_str = '\n'.join(svg_insert)
    inputfile = open(svg_file, 'r').readlines()
    write_file = open(svg_file,'w')
    for line in inputfile:
        write_file.write(line)
        if '<metadata>' in line:
            write_file.write(svg_insert_str + "\n") 

    return