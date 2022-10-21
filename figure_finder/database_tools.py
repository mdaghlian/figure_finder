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

# Get the directory where the databases (figure, and report) are stored as csvs 
with open(opj(os.path.dirname(os.path.realpath(__file__)), 'figure_dump_dir.txt')) as f:
    figure_dump = f.read().splitlines()[0]    
csv_tag_file = opj(figure_dump, 'csv_tag_file.csv') # path to figure data base
figure_dump_bin = opj(figure_dump, 'recycle_bin')   # path to bin - this is where deleted files will be backed up

def remove_csv_entries(fig_names2remove):
    '''remove_csv_entries
    
    Function to remove figures from csv database
    Parameters
    ----------
    fig_names2remove: str, list
        list or str of figure name/s (as stored in the csv database) which should be remove. 
        The corresponding entries will be deleted, as well as the associated data (i.e., png, svg & txt files)
    ----------
    Returns
    ----------
    None    
    '''
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
    '''listish_str_to_list
    
    Function to safely load the tags from the csv database
    Parameters
    ----------
    listish_str: str
        A string for the list of tags. Unfortunately - due to the way I have set up the toolbox the tags
        are not loaded as items in a list, but as one long string. This function formats this string, 
        returning the tags in the desired list of strings format
    ----------
    Returns
    ----------
    split_listish_str: list of strs (i.e., the tags, in the desired format)
    '''
    chars_to_remove = ['[', ']', '"', "'", ' ']
    for this_rm in chars_to_remove:
        listish_str = listish_str.replace(this_rm, '')
    # Now split at the commas
    split_listish_str = listish_str.split(',')
    return split_listish_str
    
def load_figure_db():
    '''load_figure_db
    
    Loads the csv database of figures as a list of dicts
    Such that if it returns figure_db where:
    figure_db[0] is a dict with entries:
        figure_db[0]['name']        name of the figure (as stored in csv),
        figure_db[0]['date']        date figure was made,
        figure_db[0]['path']        path to figure (without extentions, .svg, .png or .txt),
        figure_db[0]['tags']        list of tags associated with the figure (descriptions, etc.),
        figure_db[0]['cwd']         the working directory where the figure was made,
        figure_db[0]['nb_path']     the path to the notebook (or script) where the figure was made,        

    Parameters
    ----------
    None

    ----------
    Returns
    ----------
    figure_db: list of dicts (structured as written above)    
    '''    
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
    '''save_figure_db
    
    Saves an updated version of the csv database         

    Parameters
    ----------
    figure_db[0] is a dict with entries:
        figure_db[0]['name']        name of the figure (as stored in csv),
        figure_db[0]['date']        date figure was made,
        figure_db[0]['path']        path to figure (without extentions, .svg, .png or .txt),
        figure_db[0]['tags']        list of tags associated with the figure (descriptions, etc.),
        figure_db[0]['cwd']         the working directory where the figure was made,
        figure_db[0]['nb_path']     the path to the notebook (or script) where the figure was made,        
    ----------
    Returns
    ----------
    None        
    '''    
    df = pd.DataFrame(figure_db)
    df.to_csv(csv_tag_file, index=False)

    return None

def remove_fig_with_tags(fig_tags, fig_name=[], exclude=None):
    '''remove_fig_with_tags
    
    Function to remove figures which match a certain pattern
    >> this will delete there entries in the csv database, and also delete the 
    corresponding (.svg, .png, .txt) files

    Parameters
    ----------
    fig_tags: list, str
        include figures which have these tags
    fig_name: str 
        include figures with this name (easier to be more specific, if you know the exact file
        you want removed)
    exclude: list, str
        do *NOT* include figures which have these tags
    ----------
    Returns
    ----------
    None

    '''    
    # Match using tags (include & exclude)
    fig_db_match = find_fig_with_tags(fig_tags, fig_name=fig_name, exclude=exclude)
    # Concatenate a list of figure names
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
    '''find_fig_with_tags
    
    Function to find figures which match a certain pattern

    Parameters
    ----------
    fig_tags: list, str
        include figures which have these tags
    fig_name: str 
        include figures with this name (easier to be more specific, if you know the exact file
        you want removed)
    exclude: list, str    
        do *NOT* include figures which have these tags

    Returns 
    ---------
    figure_db_TAG_MATCH: list of dicts
        A list of dicts (formatted the same as the db as a whole), which match the search criteria

    '''        
    # Load tag file
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

    return figure_db_TAG_MATCH

def check_string_for_substring(filt, str2check, exclude=None):    
    '''check_string_for_substring
    Basically copied from a similar function in J Heijs Linescanning toolbox... (thanks!)
    Function to find figures which match a certain pattern

    Parameters
    ----------
    filt: list, str
        return matches which have *ALL* of these strings   
    str2check: list,str 
        The list/str to be checked 
    exclude: list, str    
        return matches which have *NONE* of these strings   
    
    ---------
    Returns 
    ---------
    full_match_idc: numpy array
        The index for all of the strings (in str2check) which match your specified pattern 

    ---------
    EXAMPLE
    ---------
    str2check = [
        'blah,bloop,hello,zero,fish,beep',   # Pattern 0
        'bleh,bleep,hello,one,fish,beep',   # Pattern 1
        'bluh,bloop,hello,two,fish,chip', # Pattern 2
    ]
    filt = ['fish', 'bloop']
    exclude = ['zero']
    full_match_idc = check_string_for_substring(filt=filt, str2check=str2check, exclude=exclude)

    # Patterns 0 and 2 both have 'fish' and 'bloop' so are included based on filter
    # BUT pattern 2 also has 'three', so would be excluded
    # Hence, full_match_idx would be array([2]) 

    '''
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

def get_figure_name(fig, fig_name, fig_date):
    '''get_figure_name
    Called while in the process of saving a figure
    Used to extract a useful figure name if one is not specified by the user

    Parameters
    ----------
    fig: matplotlib figure object        
    fig_name: str 
        By default will be '', if not specified before hand
    fig_date: str    
        the date when the 'fig' was constructed
    
    ---------
    Returns 
    ---------
    fig_name: str
        An appropriate name. Either that which is entered. Or one extracted from the
        figure. If we cannot find an appropriate name, random+data is used

    '''    
    if fig_name=='':
        # Does the figure have a suptitle?
        if fig._suptitle!=None:
            fig_suptitle = fig._suptitle.get_text().replace(' ', '_')
            fig_name = fig_suptitle
        else: # check for the first axis with a title
            for fig_child in fig.get_children():
                if isinstance(fig_child, mpl.axes.Axes):
                    fig_ax_title = fig_child.get_title().replace(' ', '_')
                    fig_name = fig_ax_title
                    break
    if fig_name=='':
        # Still not found an id...
        fig_name = f"random_{fig_date}"
    
    return fig_name

def save_fig_and_code_as_svg(fig, fig_tags=[], fig_name='', save_folder=figure_dump, return_db_entry=False, **kwargs):
    '''save_fig_and_code_as_svg
    What it says on the tin 
    Parameters
    ----------
    fig: matplotlib figure object        
    fig_tags: list,str 
    fig_name :
    fig_date: str    
        the date when the 'fig' was constructed
    save_folder : 
    return_db_entry
    
    ---------
    Returns 
    ---------
    fig_name: str
        An appropriate name. Either that which is entered. Or one extracted from the
        figure. If we cannot find an appropriate name, random+data is used

    '''       
    # GET PARAMETERS....
    extract_tags = kwargs.get("extract_tags", True)
    save_cwd = kwargs.get("save_cwd", True)
    save_cell_code = kwargs.get("save_cell_code", True)
    save_nb_path = kwargs.get("save_nb_path", True)
    fig_overwrite = kwargs.get("fig_overwrite", None) ### *** CHANGE THIS TO AUTOMATICALLY OVERWRITE OR NOT...***
    annotate_svg = kwargs.get("annotate_svg", True)

    fig_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    fig_name = get_figure_name(fig, fig_name, fig_date=fig_date)
    # *** CHECK WHETHER THE FILE ALREADY EXISTS ***
    files_in_directory = sorted(os.listdir(save_folder))
    if fig_name+'.svg' in files_in_directory:
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
            try: 
                remove_csv_entries(fig_name)
            except:
                print(f'Could not remove {fig_name} from csv database...' )
                print(f'carrying on...' )
            

        elif save_instruction=="s":
            # SKIPPING
            print('Not saving - skipping')
            return
        elif save_instruction=="d":
            print('Adding date to fig name to remove conflict...')
            fig_name = fig_name + '_' + fig_date

    
    fig_path = opj(save_folder, fig_name)
    fig_path = os.path.abspath(fig_path)

    # Now save as an svg
    fig.savefig(fig_path+'.svg', bbox_inches='tight', format='svg')

    # Add figure name & date to tags...
    fig_tags += [fig_name]
    fig_tags += [fig_date]
    # get them from the figure
    if extract_tags:
        fig_tags = scrape_tags_from_svg(svg_file=fig_path+'.svg', fig_tags=fig_tags)

    if save_cwd:
        fig_cwd = os.getcwd()
    else:
        fig_cwd = ''

    if save_nb_path:
        try: # First try the method that works for noetbookes
            notebook_path = get_ipython().get_parent()['metadata']['cellId']
            # e.g., 'vscode-notebook-cell:/data1/projects/dumoulinlab/Lab_members/Marcus/programs/figure_finder/example.ipynb#ch0000031'
            # So need to format it so that it is nice...
            notebook_path = notebook_path.split('cell:')[-1]        
            notebook_path = notebook_path.split('.ipynb')[0] + '.ipynb'
        except: 
            # Try the method that works for scripts...
            notebook_path = inspect.stack()[1].filename
            # check that this isn't the just another figure_finder function
            if 'report_printer' in notebook_path:
                notebook_path = inspect.stack()[2].filename
    else:
        notebook_path = ''

    if save_cell_code:
        try: 
            # Get the code from the cell that we are saving in...
            cell_code_str = get_ipython().get_parent()['content']['code']
            cell_code_path = fig_path + '.txt'
            text_file = open(cell_code_path, "w")
            text_file.write(cell_code_str)
            text_file.close()
        except:
            f = open(notebook_path, 'r')            
            cell_code_str = f.read()            
            cell_code_path = fig_path + '.txt'
            text_file = open(cell_code_path, "w")
            text_file.write(cell_code_str)
            text_file.close()            
    else: 
        cell_code_str = ''
        
    this_db_entry = {
        'name' : fig_name,
        'date' : fig_date,
        'path' : fig_path,
        'tags' : fig_tags,
        'cwd' : fig_cwd,
        'nb_path' : notebook_path,        
    }

    if annotate_svg:
        print('Inserting info into svg file')
        insert_info_to_svg(fig_dict=this_db_entry, cell_code_str=cell_code_str)
    else:
        print('Not inserting info to svg file...')
    
    # Load csv...
    figure_db = load_figure_db()
    figure_db += [this_db_entry]
    save_figure_db(figure_db)

    if return_db_entry:
        return this_db_entry

    return

def insert_info_to_svg(fig_dict, cell_code_str):

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
    svg_insert += [cell_code_str.replace('--', '/-/')]
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


def scrape_tags_from_svg(svg_file, fig_tags=[]):

    with open(svg_file) as f:
        svg_str = f.read()
    # [1] Get date 
    start_date_mark = "<dc:date>"
    end_date_mark = "</dc:date>"
    date_result = re.search(f'{start_date_mark}(.*){end_date_mark}', svg_str)
    
    fig_tags += [date_result.group(1)]

    start_txt_mark = "<!--"
    end_txt_mark = "-->"
    txt_result = re.findall(f'{start_txt_mark}(.*){end_txt_mark}', svg_str)
    
    fig_tags += txt_result
    # Split up tags with spaces in them...
    split_fig_tags = []
    for tag in fig_tags:
        split_fig_tags += tag.split()
    fig_tags = split_fig_tags
    # Remove duplicates
    fig_tags = list(set(fig_tags))

    return fig_tags

def find_fig_by_date():
    # Load tag file
    figure_db = load_figure_db()
    fig_date_list = [figure_db[i]['date'] for i in range(len(figure_db))]
    # only want 
    print(fig_date_list)
    return 



def clean_csv():
    if not os.path.exists(csv_tag_file):
        print('Figure finder: NO CSV FILE')
        return
    figure_db = load_figure_db()
    if figure_db==[]:
        print('Figure finder: Database is empty')
        return

    fig_path_list = [figure_db[i]['path'] for i in range(len(figure_db))]     
    # [1] Create a backup
    back_up_name = 'backup_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.csv'
    back_up_file = opj(figure_dump_bin, back_up_name)
    os.system(f'cp {csv_tag_file} {back_up_file}')  
    # [2] Check whether the figures still exist...
    entries_to_keep = []
    for i, this_fig in enumerate(fig_path_list):
        # check is there a png?
        is_png = os.path.exists(this_fig+'.png')# in files_in_directory
        is_svg = os.path.exists(this_fig+'.svg')
        is_txt = os.path.exists(this_fig+'.txt')
        is_img = is_png | is_svg | is_txt
        if not is_img:
            print(f'Could not find {this_fig}, in dir')            
            print('Deleting...')
        else:
            # print(f'*** COULD FIND ***{this_fig}')
            entries_to_keep.append(i)
    new_figure_db = []
    for i in entries_to_keep:
        new_figure_db += [figure_db[i]]

    save_figure_db(new_figure_db)
    return  





# def clean_csv():
#     if not os.path.exists(csv_tag_file):
#         print('Figure finder: NO CSV FILE')
#         return
#     figure_db = load_figure_db()
#     if figure_db==[]:
#         print('Figure finder: Database is empty')
#         return

#     fig_name_list = [figure_db[i]['name'] for i in range(len(figure_db))]     
#     # [1] Create a backup
#     back_up_name = 'backup_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.csv'
#     back_up_file = opj(figure_dump_bin, back_up_name)
#     os.system(f'cp {csv_tag_file} {back_up_file}')  
#     # [2] Compare figures listed in the csv with figures listed in the folder...
#     files_in_directory = sorted(os.listdir(figure_dump))
#     entries_to_keep = []
#     for i, this_fig in enumerate(fig_name_list):
#         # check is there a png?
#         is_png = this_fig+'.png' in files_in_directory
#         is_svg = this_fig+'.svg' in files_in_directory
#         is_img = is_png | is_svg
#         if not is_img:
#             print(f'Could not find {this_fig}, in dir')            
#             print('Deleting...')
#         else:
#             entries_to_keep.append(i)
#     new_figure_db = []
#     for i in entries_to_keep:
#         new_figure_db += [figure_db[i]]

#     save_figure_db(new_figure_db)
#     return    