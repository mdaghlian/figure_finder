import os
opj = os.path.join

import time
from IPython.display import display, Javascript
import hashlib

def save_notebook(file_path):
    start_md5 = hashlib.md5(open(file_path,'rb').read()).hexdigest()
    display(Javascript('IPython.notebook.save_checkpoint();'))
    current_md5 = start_md5
    
    while start_md5 == current_md5:
        time.sleep(1)
        current_md5 = hashlib.md5(open(file_path,'rb').read()).hexdigest()

def nb_to_html(html_path):
    
    notebook_path = get_ipython().get_parent()['metadata']['cellId']
    # e.g., 'vscode-notebook-cell:/data1/projects/dumoulinlab/Lab_members/Marcus/programs/figure_finder/example.ipynb#ch0000031'
    # So need to format it so that it is nice...
    notebook_path = notebook_path.split('cell:')[-1]            
    notebook_path = notebook_path.split('.ipynb')[0] + '.ipynb'    
    # Get the file name of the notbook     
    ipynb_copy_name = notebook_path.split('/')[-1]
    html_w_code_name = notebook_path.split('/')[-1].replace('.ipynb', '.html')
    html_wout_code_name = notebook_path.split('/')[-1].replace('.ipynb', '_NOCODE.html')
    # Set the file name for the exported HTML
    ipynb_copy_file = opj(html_path, ipynb_copy_name)
    html_w_code_file = opj(html_path, html_w_code_name)
    html_wout_code_file = opj(html_path, html_wout_code_name)
        
    cmd1 = f'cp {notebook_path} {ipynb_copy_file}'
    cmd2 = f'jupyter nbconvert --to html {notebook_path} --output {html_w_code_file}'
    cmd3 = f'jupyter nbconvert --to html {notebook_path} --no-input --output {html_wout_code_file}'
    print(cmd1)
    os.system(cmd1)
    print(cmd2)
    os.system(cmd2)    
    print(cmd3)
    os.system(cmd3)        

    # also copy the notebook (.ipynb) itself...
    