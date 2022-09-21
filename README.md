# figure finder repository
I often make many many figures, with lots of variations, across several notebooks. It is often difficult to find the desired figure, and when you do find it, it is useful to know when you made it and how you made it (this is not always obvious).

The motivation behind this package is to help with these issues. 

NB - At the moment - this only works with notebooks. (I run it in VScode)

Figures are all dumped in one folder as png files. The code in the notebook cell used to create them is saved in a corresponding text file, and a database is created. The database (a csv file) has information on how the figure was made (in which notebook, with the code from the cell), what the figure is about (tags are extracted from all the text in the figure).

You can then search for your figures using the tags. This includes the date that the figure was made, any tags that the user specified, as well as any text which is in the figure. 

See the example notebook


## In active development
This package is still in development and its API might change. Use at your own risk!

## Installation
[1] In ff_setup -> decide where you want your figures to be dumped (i.e., set FIGURE_DUMP)
[2] run >> bash shell/ff_setup setup
... done!

## TODO
[] Support for SVG files (both saving & extracting tags)
[] Option to save from outside a notebook (i.e., in a script) 
[] Make a function which can delete entries with *tags* function
[] Create CLI functions 
[] Create support for project specific folders (& databases?)
[] Extract the plot type automatically (e.g., scatter, box... Possible?)
[] Experiment using a pandas dataframe (probably a much more efficient way to go than the current thing...)
[] Include search by cwd, and or nb path
[] Search for date range

```
