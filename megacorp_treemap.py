import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import squarify as sq
import matplotlib.pyplot as plt


## Corporate Ownership Treemap

# Each corporation is owned (stock) by other "investor" corporations.
# This program is designed to make a Treemap of which corporations own which.
# Since each owner corporation is also owned by other corporations
# this requires an interative approach to determine real ownership.
# 
# In the end I need x, y, width (dx), height (dy), face color, amd face label for a box.
# Each box in the Treemap represents the size of ownership a corporation has for 
# that parent corp.
# On each iteration I need to access the db to get the size (percent ownership),
# corp color, and name for face label for each of the children (owner) corps.
# Size determines dx, dy through normalization of the containing square,
# so on each iteration I need to bring along the containing squares.
# x, y, dx, dy of each new contained square are determined through squarify.


# Get the database
df = pd.read_csv('../megacorp_db.csv')

## Corporation to map from DB 
# (there are a few others in there that are not here)

# Set the top level corp for ownership investigation

# Investment corps
#corp = 'Vanguard Group Inc'
#corp = 'Merrill Lynch Co Inc'
#corp = 'Bank Of America Corp'
#corp = 'State Street Corp'
#corp = 'Jpmorgan Chase Co'
#corp = 'Fidelity Investments'
corp = 'Blackrock Inc'

# Media Corps
#corp = 'Sinclair Broadcasting Group'
#corp = 'Comcast'
#corp = 'AT&T'
#corp = 'News Corp'
#corp = 'ViacomCBS'

# Multi-media corps
#corp = 'Google'
#corp = 'Facebook'
#corp = 'Twitter'

# Entertainment corps
#corp = 'Disney'
#corp = 'Netflix'

# Retail corps
#corp = 'Amazon'
#corp = 'Best Buy'
#corp = 'Albertsons'


# Infrastructure corps
#corp = 'AECOM'

# Resources corps
#corp = 'Louisiana-Pacific Corp'
#corp = 'Archer-Daniels-Midland Co'
#corp = 'General Mills Inc'

# Example Corps
#corp = 'Money Inc'
#corp = 'Fat Money'
#corp = 'Money Castle'
#corp = 'HinkeyPoo'

## Set flags for Treemap

# Depth = number of recursive iterations to display in the Treemap.
# Be cautious, this is an O(n) algorithm (x20). E.g. depth = 0 -> 20(ish) 
# boxes, depth = 1 -> 400, depth = 2 -> 8000, depth = 3 -> 160,000, etc.
# I'm sure it could be made much more efficient.
# The highest I could run it for a larger corp before it choked was depth = 2
# and that still took half an hour. YYMV.

depth = 0

# Add labels
text = True
#text = False

# Turn the institutions black to represent the limit of further iterations 
# without making the computer bleed its own blood
#black = True
black = False

# Self creates a Treemap of just the corp itself (top level)
# Note: to create a self map "Self" must be defined in the db
# format is: '(corp name)', 'Self', 0.0000000001, '#xxxxxx'
# for: the name of self, 'Self', a number in case of divide by zero (which I think I fixed), hex color str
#self = True
self = False

# Set the frame dimensions for the initial square and set initial squarify vars
width = 1
height = 1
x = 0
y = 0
rects = []
colors = []
labels = []

# Build lists of sizes, rects, labels, and colors iteratively. In the process
# the lists will be flattened for Treemap input.
def build_hierarchical_arrays(df,depth,corp,x,y,width,height,colors,rects,black,text):
    
    df = df[df.child != 'Self'] # remove "self" references from initial database
    dfg = df.groupby('parent')
    
    # check to see if the corporation is in the db, otherwise set it to Default
    in_db = df['parent'].str.contains(corp) # Returns a series of len(dataframe) of boolean values
    if in_db.sum() == 0:
        corp = 'Default'
    
    # print out the initial corp to screen to make sure I'm doing the right one.
    print('corp = ')
    print(corp)
    
    # Get all the child data from the db
    get_corp = dfg.get_group(corp).sort_values(by=['ownership'], ascending=False)
    
    ## Build arrays
    # build a relative sizes array for this depth
    sizes = get_corp['ownership']
    sizes = np.array(sizes.values.tolist())
    sizes = sq.normalize_sizes(sizes, width, height)
    
    # create array of hashes with x,y,dx,dy for each child corp
    rects = sq.squarify(sizes, x, y, width, height)    
    
    # build colors array
    colors = get_corp['color'].to_list()
    
    # build labels array
    labels = get_corp['child'].to_list()
    
    # Make labels wrap by putting in newlines if words are long (because I can't get "wrap=True" to work)
    if text and depth == 0: labels = wrap_labels(labels)

    # Build the above arrays for each depth, replacing the level above at each step
    for i in range(depth):
        sizes, rects, colors, labels = remap_corp(df, sizes, rects, colors, labels, black, text)    
        
    return sizes, rects, colors, labels

    
# Replaces a parent (node) corp with its children corps and 
# creates the data for the treemap at each level of depth
def remap_corp(df, sizes, rects, colors, labels, black, text):

    # Iterate through children nodes to create sub arrays, replacing each 
    # parent entry with its child sub array
    for i, child in enumerate(labels): 
        # Skip "self"
        if child == 'Self':
            continue
        
        dfg = df.groupby('parent')

        # check to see if the corporation is in the db, otherwise set it to Default
        in_db = df['parent'].str.contains(child)
        if in_db.sum() == 0:
            child = 'Default'
        
        # specific one off function to show Blackrock ownership by just replacing Merrill Lynch
        #if not child == 'Merrill Lynch Co Inc':
        #    continue
        
        # Get the dimensions of the current square from rects
        dims = rects[i]
        x, y, dx, dy = dims['x'], dims['y'], dims['dx'], dims['dy']
        get_corp = dfg.get_group(child).sort_values(by=['ownership'], ascending=False)
        
        ## Build arrays for each child
        # build a relative sizes array for this depth
        sizes = get_corp['ownership']
        sizes = np.array(sizes.values.tolist())
        sizes = sq.normalize_sizes(sizes, dx, dy)

        # create array of hashes with x,y,dx,dy for each child corp
        rects[i] = sq.squarify(sizes, x, y, dx, dy)

        # build colors sub array for child
        colors_temp = get_corp['color'].to_list()
        # set to black all corps not retail or insider if black flag is true
        # i.e. all corps with children that would become black with more iterations
        if black:
            if not child == 'Retail' or not child == 'Insider':
                for j, color in enumerate(colors_temp):
                    if not color == '#ffffff': # 'or' didn't work here?
                        if not color == '#797979':
                            colors_temp[j] = '#000000'        
        
        colors[i] = colors_temp
            
        # build labels sub array for child
        labels[i] = get_corp['child']
    
    # Flatten all arrays
    
    # Use smart_flat in case of multiple layers of array 
    # (e.g. looking at just Merrill Lynch for Blackrock in remap_corp)
    rects = [val for sublist in rects for val in sublist]
    colors = [val for sublist in colors for val in sublist]
    labels = [val for sublist in labels for val in sublist]
    
    # If there are partial sublists use smart_flat
    #rects = smart_flat(rects)
    #colors = smart_flat(colors)
    #labels = smart_flat(labels)
    
    return sizes, rects, colors, labels

# If "Self" is selected, create the arrays for display of just the corporation itself
def get_self(df, corp):
    corp_group = df.loc[df['parent'] == corp]
    colors = corp_group.loc[corp_group['child'] == 'Self']['color'].to_list()
    sizes = [1]
    sizes = sq.normalize_sizes(sizes, 1, 1)
    rects = sq.squarify(sizes, 0, 0, 1, 1)
    labels = [corp]

    return sizes, rects, colors, labels

# flattens an array even if not all elements are arrays
def smart_flat(lst):
    new_list = []
    for sublist in lst:
        if isinstance(sublist, list):
            for val in sublist:
                new_list.append(val)
        else:
            new_list.append(sublist)
    return new_list

# A work around for label wrapping not working on face labels
def wrap_labels(labels_ary):
    for i, label in enumerate(labels_ary):
        label_temp = label.split()
        for j, word in enumerate(label_temp):
            if len(word) > 3: # Adjust word length as required
                if not j == len(label_temp)-1:
                    label_temp[j] = word + '\n'
            else:
                label_temp[j] = word + ' '
        labels_ary[i] = "".join(label_temp)
    return labels_ary

# Begin program (main)
if self:
    sizes, rects, colors, labels = get_self(df, corp)
else:
    sizes, rects, colors, labels = build_hierarchical_arrays(df,depth,corp,x,y,width,height,colors,rects,black,text)

# Create a figure
fig = plt.figure(figsize = (15,15))

# Create an array of boxes for the plot 
axes = [fig.add_axes([rect['x'], rect['y'], rect['dx'], rect['dy'], ]) for rect in rects]

# Determine if a face color is dark enough to warrant a white label
def bright_enough(face_color):
    str = face_color
    label_color = '#000000'
    # get r g b values from color
    r = int(str[1:3],16)
    g = int(str[3:5],16)
    b = int(str[5:7],16)
    # get luminosity values. Adjust r g b thresholds for white text on color as desired
    luma = 0.134 * r + 0.125 * g + 0.147 * b
    # adjust luma threshold as needed
    if (luma < 10):
        label_color = '#ffffff'
    
    return label_color

# Wrap labels if text flag is true (because its not working in matplotlib.axes.text flags)
if text: labels = wrap_labels(labels)
    
# Set each boxes parameters
for ax, color, label in zip(axes, colors, labels):
    ax.set_facecolor(color)
    label_color = bright_enough(color)
    # Set the text height in the box
    if text:
        # Set fontsize
        if self: 
            fontsize = 36 
        else: 
            fontsize = 18
        # Get box dimensions
        dy = ax.bbox.height/1000
        dx = ax.bbox.width/1000
        # Set the distance between the bottom of the box and the label depending on the size of the box
        if dy < 0.06:
            bottom = 0.05
        elif dy < 0.1:
            bottom = 0.1
        elif dy < 0.2:
            bottom = 0.3
        elif dy < 0.3:
            bottom = 0.4
        elif dy < 0.4:
            bottom = 0.5
        else:
            bottom = 0.5
        # Add label if box is wide enough
        if dx > 0.08:
            ax.text(.5, bottom,label,fontsize=fontsize,ha="center",c=label_color,wrap=True) # Note: wrap not working? see wrap_labels()
    # Remove axis labels
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])

# Display the Treemap
plt.show()
