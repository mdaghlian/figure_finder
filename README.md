# figure finder repository
I often make many many figures, with lots of variations, across several notebooks. It is often difficult to find the desired figure, and when you do find it, it is useful to know when you made it and how you made it.

The motivation behind this package is to help with these issues. 

NB - At the moment - this only works with notebooks. (I run it in VScode)

Figures are saved as svg files. The package automatically extracts important information about the figure, including:

* Any text (which is saved under tags)

* The date

* Code from the notebook cell which was used to make the figure

* The path to the notebook used to make the figure

This information is then written to the figure svg file, inside the metadata component. It can be viewed by opening the svg with a text editor 

By default all figures are saved to the "figure_dump" folder, but you can specify where you want the figures to go.

A secondary function is that it creates a database of figures, using a csv / dict. You can then use the search functions and key words to find and display your figure as well as the accompanying metadata.  

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


```
