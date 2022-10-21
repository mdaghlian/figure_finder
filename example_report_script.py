import numpy as np
import matplotlib.pyplot as plt
import os
import figure_finder as ff

ff_Report = ff.ReportMaker('eg_report', '/data1/projects/dumoulinlab/Lab_members/Marcus/programs/figure_finder')

ff_Report.add_title('Blah level 1', level=1)
ff_Report.add_title('Blah level 2', level=2)
ff_Report.add_text('''Generic description doo doo doo hello 
Now we can save the figure in the fig_dump folder
>> we can specify the name of the file (or ff will extract the title from the figure). 
We can also specify the tags we want to save with this fig. ff will automatically find *any* text in the fig (legend, axes, text) and 
scrape these to include in the tags (so don't worry too much)
Figure name & the date will also be saved as tags
>> First we will save this to our local folder''')

# now add the image
x = np.random.random(100)
y = np.random.random(100)
plt.scatter(x,y, label='sub01')
plt.xlabel('bloop')
plt.ylabel('bleep')
plt.title('Comparing ')
plt.text(1,.5, 'interesting text')
plt.legend()
fig = plt.gcf()
fig.suptitle('Something else')
ff_Report.add_img(fig)


# Now some more text...

ff_Report.add_text('''more text boop boop blah blah''')
ff_Report.add_title('Blah level 2', level=4)

x = np.linspace(0,1, 100)
y = np.random.random(100)
plt.plot(x,y, label='sub02')
plt.xlabel('tick')
plt.ylabel('tock')
plt.title('here ')
plt.text(1,.5, 'interesting text')
plt.legend()
fig = plt.gcf()
fig.suptitle('Something else')
ff_Report.add_img(fig)

ff_Report.save_html()



 