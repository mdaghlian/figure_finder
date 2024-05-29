import os
opj = os.path.join

from datetime import datetime
import numpy as np
import importlib

# MATPLOTLIB STUFF
import matplotlib as mpl
import matplotlib.pyplot as plt

from .utils import *

class FigureSaver(object):
    """

    Help with figure saving...
    Specify at the beginning of the notebook where to save everything.. 
    just makes it easier
    """

    def __init__(self, name, path, save_mode = True, folder_ow=False, fig_ow='ow',  **kwargs):
        """__init__
        Will make the folder and set everything up...

        name            name of the folder 
        path            path (full where saved will path + name)
        save_mode       Do saving, or not...
        folder_ow       If folder already exists, ow?
        fig_ow          If fig exists, ow? 
                        'ow', 'skip', 'date',
        
        Optional
        fig_tags            If save w/ code add tags...
        save_*              Default save formats i.e., svg, png,...
        dpi                 Default dpi

        """                
        self.date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.name = name
        self.path = os.path.abspath(opj(path, name))
        self.save_mode = save_mode        
        self.fig_ow = fig_ow
        # Optional        
        self.fig_tags       = kwargs.get('fig_tags', [])
        
        # -> default formats to save 
        save_svg = kwargs.get('save_svg', False)
        save_png = kwargs.get('save_png', False)
        save_eps = kwargs.get('save_eps', False)
        save_pdf = kwargs.get('save_pdf', False)
        self.save_type_dict = {
            'save_svg'          : save_svg,
            'save_png'          : save_png,
            'save_eps'          : save_eps,
            'save_pdf'          : save_pdf,
        }
        self.dpi      = kwargs.get('dpi', 300)

        # -> Other useful defaults to put in...
        mpl.rcParams.update(mpl.rcParamsDefault)
        mpl.rcParams['pdf.fonttype'] = 42 # To work with adobe when saving .pdf
        mpl.rcParams['ps.fonttype'] = 42 # To work with adobe when saving .pdf
        mpl.rcParams['font.size'] = 10    # Default fontsize
        # mpl.rcParams['text.usetex'] = True
        mpl.rcParams['mathtext.default'] = 'regular' 
        # Set up saving folder...
        if not self.save_mode:
            return

        if os.path.exists(self.path):
            print('FOLDER ALREADY EXISTS!')
            if folder_ow:
                # Overwrite - > delete the old version
                print('Deleting and remaking folder')
                os.system(f"rm -r {self.path}")                     
                os.makedirs(self.path)
            else:
                print('Not deleting...')        
        else:
            print('Making folder')
            os.makedirs(self.path)


    
    def add_img(self, fig, fig_name='', **kwargs):        
        '''add_img
        Save an image in the folder...

        fig         matplotlib figure
        fig_name    name of figure        
        '''
        if not self.save_mode:   # NOT SAVING!!!
            plt.show(block=True)
            plt.pause(0.001)    
            return
        context_note = kwargs.get('context_note', None)
        context_note_pos = kwargs.get('context_note_pos',[0,0] )        
        # What format are we saving? Use defaults unless specified
        fig_ow      = kwargs.get('fig_ow', self.fig_ow)         
        dpi         = kwargs.get('dpi', self.dpi)        
        save_type_dict = {}
        for save_key in self.save_type_dict.keys():
            save_type_dict[save_key] = kwargs.get(save_key, self.save_type_dict[save_key])           

        # Saving into a subfolder?
        sub_folder  = kwargs.get('sub_folder', None)
        if sub_folder is None:
            this_path = self.path
        else: 
            this_path = opj(self.path, sub_folder)
            if not os.path.exists(this_path):
                os.makedirs(this_path)
        # Make fig_name -> find from figure, or use default. keep option for adding the date
        fig_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')                
        fig_name,fig_exists = FIG_get_figure_name(
            fig=fig, fig_name=fig_name, fig_date=fig_date,
            fig_folder=this_path, fig_ow=fig_ow
            )             
        
        if fig_exists & (fig_ow=='skip'):
            print('fig exists, not overwriting')
            return

        for s_type in save_type_dict.keys():
            if (s_type=='save_svg') & (save_type_dict[s_type]):
                # meta kwargs
                meta_kwargs = {**kwargs}
                meta_kwargs['fig_folder'] = this_path
                meta_kwargs['fig_ow'] = fig_ow
                meta_kwargs['dpi'] = dpi
                FIG_save_svg_meta(
                    fig=fig, 
                    fig_name=fig_name,
                    **meta_kwargs,
                )                

            elif save_type_dict[s_type]:
                fig_suffix = s_type.replace('save_', '')
                fig.savefig(
                    opj(this_path, f'{fig_name}.{fig_suffix}'), 
                    bbox_inches='tight', 
                    dpi=dpi,
                    transparent=True,
                    # backend= 'pgf' if s_type=='save_pdf' else None,
                    )
        # Add context note explicitly 
        # (it will be added automatically as metadata in svg files)
        # but for other files it is created as an extra image
        if context_note is not None:
            # Add the context underneath
            # Add the text to the figure initially
            text_obj = fig.text(context_note_pos[0], context_note_pos[1], context_note, wrap=True, )
            fig.canvas.draw()
            for s_type in save_type_dict.keys():
                if save_type_dict[s_type]:
                    fig_suffix = s_type.replace('save_', '')
                    fig.savefig(
                        opj(this_path, f'{fig_name}_context.{fig_suffix}'), 
                        bbox_inches='tight', 
                        dpi=dpi,
                        transparent=True,
                        # backend= 'pgf' if s_type=='save_pdf' else None,
                        )
        
    
    def add_code_backup(self, bu_list=[], **kwargs):
        '''
        Function to add copies of the code that you depended on to make the figures
        i.e., if you are using a code that is likely to change...
        It will save a copy in the figure_save folder...
        
        bu_list     list of pacakges to save

        Optional:
        do_all_imports      save all the imports in the script
        just_this_cell       if running though notebook, just do this cell
        do_full_package     Save the full package (e.g., blah rather than just the file blah.submodule)
        
        '''
        if not self.save_mode: # NOT IN SAVE MODE -> quit      
            plt.pause(0.001)
            return
        self.code_bu_dir = opj(self.path, 'code_bu_dir')
        save_running_code_imports(self.code_bu_dir, bu_list=bu_list, **kwargs)



import matplotlib.text as mtext

class WrapText(mtext.Text):
    def __init__(self,
                 x=0, y=0, text='',
                 width=0,
                 **kwargs):
        mtext.Text.__init__(self,
                 x=x, y=y, text=text,
                 wrap=True,
                 **kwargs)
        self.width = width  # in screen pixels. You could do scaling first

    def _get_wrap_line_width(self):
        return self.width