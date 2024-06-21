import os
opj = os.path.join

from datetime import datetime
import inspect
import numpy as np
import re
import time
from IPython.display import display, Javascript, HTML
import hashlib
import matplotlib as mpl
import importlib


def sanitise_string(s):
    '''sanitise_string
    Remove nasty characters from string... 
    '''
    if not isinstance(s,str):
        s = str(s)
    # Replace '=' with 'eq'
    s = s.replace('=', '-eq-')
    
    # Replace all other non-alphanumeric characters with '_'
    # The regular expression '[^a-zA-Z0-9-]' matches any character that is not
    # a letter, digit, or '-'.
    s = re.sub(r'[^a-zA-Z0-9-]', '_', s)
    
    # Remove consecutive '_' characters
    s = re.sub(r'_{2,}', '_', s)

    # Remove consecutive '-' characters 
    s = re.sub(r'-{2,}', '-', s)
    
    return s

def save_notebook(file_path):
    '''save the notebook (i.e., after it has run)
    May not work if the notebook for jupyterlab
    '''
    # return
    start_md5 = hashlib.md5(open(file_path,'rb').read()).hexdigest()
    current_md5 = start_md5
    display(Javascript('IPython.notebook.save_checkpoint();'))
    wait_time = 0
    while start_md5 == current_md5:
        time.sleep(1)
        current_md5 = hashlib.md5(open(file_path,'rb').read()).hexdigest()
        wait_time += 1
        if wait_time>5:
            print('Notebook not saving...')
            break

def get_running_code_string(file_path):
    '''Get the code from the running cell
    '''
    f = open(file_path, 'r')            
    code_str = f.read()   
    return code_str


def get_running_path():
    '''Get the path of the script / notebook which is being run
    '''
    try: # First try the method that works for noetbookes
        running_path = get_ipython().get_parent()['metadata']['cellId']
        # e.g., 'vscode-notebook-cell:/data1/projects/dumoulinlab/Lab_members/Marcus/programs/figure_finder/example.ipynb#ch0000031'
        # So need to format it so that it is nice...
        running_path = running_path.split('cell:')[-1]        
        running_path = running_path.split('.ipynb')[0] + '.ipynb'
    except: 
        # Try the method that works for scripts...
        running_path = inspect.stack()[1].filename
        # check that this isn't the just another figure_finder function
        layer = 1 
        while 'figure_finder' in running_path:
            layer += 1
            running_path = inspect.stack()[layer].filename
    return running_path


def save_running_code(output_folder):    
    '''Save the code being run to an output folder
    '''
    running_path = get_running_path()    
    if 'ipynb' in running_path:        
        save_notebook(running_path) # if notebook, save changes before copying 
    # save a copy to the output folder
    copy_name = running_path.split('/')[-1]
    cmd = f'cp {running_path} {opj(output_folder, copy_name)}'
    os.system(cmd)

    # If notebook do some other things
    if 'ipynb' in running_path:
        # Get the file name of the notbook             
        html_w_code_name = copy_name.replace('.ipynb', '.html')
        html_wout_code_name = copy_name.replace('.ipynb', '_NOCODE.html')
        # Set the file name for the exported HTML
        html_w_code_file = opj(output_folder, html_w_code_name)
        html_wout_code_file = opj(output_folder, html_wout_code_name)
        # With code
        cmd = f'jupyter nbconvert --to html {running_path} --output {html_w_code_file}'
        print(cmd)
        os.system(cmd)
        # No code
        cmd = f'jupyter nbconvert --to html {running_path} --no-input --output {html_wout_code_file}'
        print(cmd)
        os.system(cmd)    

def save_running_code_imports(code_bu_dir, bu_list=[], **kwargs):
    '''
    Function to add copies of the code that you depended on to make the figures
    i.e., if you are using a code that is likely to change...
    It will save a copy in the figure_save folder...
    
    code_bu_dir where to put the code
    bu_list     list of pacakges to save

    Optional:
    do_all_imports      save all the imports in the script
    just_this_cell       if running though notebook, just do this cell
    do_full_package     Save the full package (e.g., blah rather than just the file blah.submodule)
    
    '''
    
    do_all_imports = kwargs.get('do_all_imports', False)
    just_this_cell = kwargs.get('just_this_cell', True)
    do_full_package = kwargs.get('do_full_package', False)

    # make back up dir
    if not os.path.exists(code_bu_dir):
        os.mkdir(code_bu_dir)

    if not isinstance(bu_list, list):
        bu_list = [bu_list]
    
    # Loop through...
    for bu_mod_str in bu_list:            
        save_bu_mod(bu_mod_str, do_full_package=do_full_package)

    # This cell... look at all the import lines in this cell...
    
    if not do_all_imports:
        return 
    # -> Get string for notebook cell or script
    # -> first find the path of the script / notebook
    nb_path = get_running_path()        
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
        save_bu_mod(bu_mod_str, do_full_package=do_full_package)    

    return import_code_str
    

def save_bu_mod(code_bu_dir, bu_mod_str, do_full_package=False):
    
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
    bu_out_file = opj(code_bu_dir, bu_mod_str)
    if os.path.exists(bu_out_file):
        print('Deleting and remaking folder')
        os.system(f"rm -r {bu_out_file}")                     
        os.makedirs(bu_out_file)
    else:
        os.makedirs(bu_out_file)
    
    # Create a text file with info 
    date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    with open(opj(bu_out_file, f'A0-{bu_mod_str}-ff-backup-info.txt'), 'w') as file:
        file.write(
            f'{bu_mod_str} copied on {date} from {bu_mod_file}'                
        )

    cmd1 = f'cp -r {bu_mod_file} {bu_out_file}'
    print(cmd1)
    os.system(cmd1)





def FIG_get_figure_name(fig, fig_name, fig_date='', fig_folder=None, fig_ow='ignore'):
    '''FIG_get_figure_name
    Called while in the process of saving a figure
    Used to extract a useful figure name if one is not specified by the user

    Parameters
    ----------
    fig: matplotlib figure object        
    fig_name: str 
        By default will be '', if not specified before hand
    fig_date: str    
        the date when the 'fig' was constructed
    fig_folder:
        where saving
    fig_ow:
        If a version already exist, what to do? 
        'ow' - overwrite, 'skip' - do nothing, 'date' - add a version with the date...

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
    fig_name = sanitise_string(fig_name)
    
    if fig_ow=='ignore':
        # Don't bother checking if it exists...
        return fig_name
    
    # Check if it already exists...
    files_in_directory = sorted(os.listdir(fig_folder))
    fig_exists = False
    for file in files_in_directory:
        if f'{fig_name}.' in file:
            if fig_ow=='ow':
                os.remove(opj(fig_folder, file))
            else:
                fig_exists = True

    
    # If date ow add date at the end
    if fig_exists & (fig_ow=='date'):
        fig_name = fig_name+fig_date
        fig_exists = False
    
    return fig_name, fig_exists

def FIG_save_svg_meta(fig, fig_name='', fig_folder=None, **kwargs):
    '''Add metadatat to the figure svg
    What it says on the tin 
    Parameters
    ----------
    fig: matplotlib figure object        
    fig_tags: list,str 
    fig_name :
    fig_date: str    
        the date when the 'fig' was constructed
    fig_folder : 
    return_db_entry
    
    ---------
    Returns 
    ---------
    fig_name: str
        An appropriate name. Either that which is entered. Or one extracted from the
        figure. If we cannot find an appropriate name, random+data is used

    '''       
    # GET PARAMETERS....
    annotate_svg = kwargs.get("annotate_svg", False)    
    fig_tags = kwargs.get('fig_tags', [])
    extract_tags = kwargs.get("extract_tags", True)
    save_cwd = kwargs.get("save_cwd", True)
    context_note = kwargs.get("context_note", '')
    save_cell_code = kwargs.get("save_cell_code", False)
    save_nb_path = kwargs.get("save_nb_path", True)
    fig_ow = kwargs.get("fig_ow", 'ow') # 'ow' overwrite, 'skip' don't change, 'date' add date...
    if context_note !='':
        annotate_svg=True

    # Get fig name + date
    fig_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')    
    fig_name,fig_exists = FIG_get_figure_name(
        fig=fig, fig_name=fig_name, 
        fig_date=fig_date, fig_folder=fig_folder, fig_ow=fig_ow
        )
    if fig_exists:
        print(f'{fig_name} already exists...')
        if fig_ow=='ow':
            print('overwriting...')
        if fig_ow=="skip":
            # SKIPPING
            print('Not saving - skipping')
            return
    
    fig_path = opj(fig_folder, fig_name)
    fig_path = os.path.abspath(fig_path)

    # Now save as an svg
    fig.savefig(
        fig_path+'.svg', 
        dpi=kwargs['dpi'],
        bbox_inches='tight', 
        transparent=True,         
        format='svg'
        )
    if not annotate_svg:
        return
    
    # ADD INFORMATION
    # Add figure name & date to tags...
    fig_tags += [fig_name]
    fig_tags += [fig_date]
    # get them from the figure
    if extract_tags:
        fig_tags = FIG_scrape_tags_from_svg(svg_file=fig_path+'.svg', fig_tags=fig_tags)

    if save_cwd:
        fig_cwd = os.getcwd()
    else:
        fig_cwd = ''

    if save_nb_path:
        notebook_path = get_running_path()
    else:
        notebook_path = ''

    if save_cell_code:
        try: 
            # Get the code from the cell that we are saving in...
            cell_code_str = get_ipython().get_parent()['content']['code']
        except:
            f = open(notebook_path, 'r')            
            cell_code_str = f.read()            
        
    else: 
        cell_code_str = ''
        
    this_db_entry = {
        'context'   : context_note, 
        'name'      : fig_name,
        'date'      : fig_date,
        'path'      : fig_path,
        'tags'      : fig_tags,
        'cwd'       : fig_cwd,
        'nb_path'   : notebook_path,
        'code_str'  : cell_code_str,        
    }
    
    if annotate_svg:
        print('Inserting info into svg file')
        FIG_insert_info_to_svg(fig_dict=this_db_entry)        
    else:
        print('Not inserting info to svg file...')    

    return this_db_entry

def FIG_insert_info_to_svg(fig_dict):

    svg_file = fig_dict['path']+'.svg'
    
    # [2] Create string to add to the svg...
    svg_insert = ["<text>"]
    svg_insert += ["<!--"]
    svg_insert += ["*********** START - info inserted by figure finder ********"]
    svg_insert += ["***********************************************************"]
    svg_insert += ["***********************************************************"]    
    svg_insert += [f'CONTEXT : {fig_dict["context"]}']
    svg_insert += [f'DATE : {fig_dict["date"]}']
    svg_insert += [f'FIGURE NAME: {fig_dict["name"]}']
    svg_insert += [f'FIGURE CWD: {fig_dict["cwd"]}']
    svg_insert += [f'NOTEBOOK: {fig_dict["nb_path"]}']
    tag_str = ','.join(fig_dict['tags'])
    svg_insert += [f'TAGS: {tag_str}']
    svg_insert += ["***********************************************************"]    
    svg_insert += ["********* CODE FROM NB CELL USED TO MAKE FIG **************"]    
    svg_insert += [fig_dict['code_str'].replace('--', '/-/')]
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

def FIG_scrape_tags_from_svg(svg_file, fig_tags=[]):

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
