# figure finder repository
This provides a way to generate html reports, which save figures as .svg files. Information about each figure and report is stored in a csv database.

You can easily find the figures or reports later using the search parameters and tags. In addition info about how and when the report was made is also saved.

This makes it easier to reatedly run the same plotting procedure across subjects and conditions, and to store it all in an accessible way.

Figures are saved as svg files. The package automatically extracts important information about the figure, including:

* Any text (which is saved under tags)

* The date

* Code from the notebook cell which was used to make the figure (or python script)

* The path to the notebook used to make the figure

This information is then written to the figure svg file, inside the metadata component. It can be viewed by opening the svg with a text editor 

A secondary function is that it creates a database of figures, using a csv file and pandas. You can then use the search functions and key words to find and display your figure as well as the accompanying metadata.  

The commands in /bin can be called from the command line from anywhere. They can be used to print the code for a figure

See the example notebook


## In active development
This package is still in development and its API might change. Use at your own risk!

## Installation
[1] In ff_setup -> decide where you want your figures to be dumped (i.e., set FIGURE_DUMP)

[2] run >> bash shell/ff_setup setup
... done!

## TODO

[*] Option to save from outside a notebook (i.e., in a script) 

[*] Extract the plot type automatically (e.g., scatter, box... Possible?)

[*] Experiment using a pandas dataframe (probably a much more efficient way to go than the current thing...)

[*] Include search by cwd, and or nb path

[*] Search for date range

[*] Make search not case sensitive

[*] Option to compare files with competing names - and resolve them by appending the different tags...

```
