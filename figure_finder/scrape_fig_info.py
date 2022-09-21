import os
opj = os.path.join

from datetime import datetime
import numpy as np
import sys

# MATPLOTLIB STUFF
import matplotlib as mpl
import pandas as pd


with open(opj(os.getcwd(), 'bin', 'figure_dump_dir.txt')) as f:
    figure_dump = f.read().splitlines()[0]
csv_tag_file = opj(figure_dump, 'csv_tag_file.csv')
figure_dump_bin = opj(figure_dump, 'recycle_bin')

def get_figure_name(fig, fig_name, fig_date):
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
    
    # Add png...
    fig_name += '.png'
    return fig_name

def scrape_tags_from_figure(fig, start_obj=[], fig_tags=[]):
    # If no start object... then this is the first loop...
    if not isinstance(fig, mpl.figure.Figure):
        sys.exit()
    
    if start_obj==[]:
        # First run... get the sup title info...
        if fig._suptitle!=None:
            fig_suptitle = fig._suptitle.get_text().replace(' ', '_')            
            fig_tags += [fig_suptitle]

        for this_obj in fig.get_children():
            fig_tags = scrape_tags_from_figure(fig, start_obj=this_obj, fig_tags=fig_tags)
    
    # If object is axes...
    # Check title, xlabel, ylabel, xticks, then run recursively...
    # **************************************
    if isinstance(start_obj, mpl.axes.Axes):          
        # Check title
        fig_tags += [start_obj.get_title()]
        # Check xlabel
        fig_tags += [start_obj.xaxis.get_label().get_text()]
        # Check ylabel
        fig_tags += [start_obj.yaxis.get_label().get_text()]
        # Check xticks
        for xtick in start_obj.xaxis.get_ticklabels():
            fig_tags += [xtick.get_text()]
        # Check yticks
        for ytick in start_obj.yaxis.get_ticklabels():
            fig_tags += [ytick.get_text()]
        # Run recursively...
        for this_obj in start_obj.get_children():
            fig_tags = scrape_tags_from_figure(fig, start_obj=this_obj, fig_tags=fig_tags)        

    # Check if it is text    
    if isinstance(start_obj, mpl.text.Text):   
        fig_tags += [start_obj.get_text()]

    # CHECK FOR OTHER STUFF WITH LABELS... 
    if hasattr(start_obj, 'get_text'):
        start_obj_label = start_obj.get_text()
        if isinstance(start_obj_label, str):
            fig_tags += [start_obj_label]

    # CHECK FOR OTHER STUFF WITH LABELS... 
    if hasattr(start_obj, 'get_label'):
        start_obj_label = start_obj.get_label()
        if isinstance(start_obj_label, str):
            fig_tags += [start_obj_label]

    # Remove '' from list
    fig_tags = list(filter(None, fig_tags))
    # Remove '_child' from list
    fig_tags = [i for i in fig_tags if '_child' not in i]
    # Split up tags with spaces in them...
    split_fig_tags = []
    for tag in fig_tags:
        split_fig_tags += tag.split()
    fig_tags = split_fig_tags
    # Remove duplicates
    fig_tags = list(set(fig_tags))
    return fig_tags


##############################

# def legend_check(axs):
#     do_legend = False
#     for child in axs.get_children():
#         if isinstance(child, mpl.lines.Line2D):
#             if child.get_label()[0]!="_":
#                 do_legend = True
#     for child in axs.collections:
#         if child.get_label()[0]!="_":
#             do_legend=True
#     return do_legend
        