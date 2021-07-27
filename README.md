# iterative_treemap_megacorp
A recursive Treemap program to map megacorp ownership (could have other uses with directed tree data)

Each corporation is owned (stock) by other "investor" corporations.
This program is designed to make a Treemap of which corporations own which.
Since each owner corporation is also owned by other corporations
this requires an iterative approach to determine real ownership.

Starting with percentage of ownership data gathered from public databases, e.g.
finance.yahoo.com or wallstreetzen.com this produces arrays of (x, y, width (dx), 
height (dy)), face color, and face label for boxes of ownership. These are zipped
up and matplotlib.axes creates the boxes. The Treemap is plotted from these boxes.
Each box in the Treemap represents the size of ownership a corporation has for 
some starting parent corp.
On each iteration I access the db to get the size (percent ownership),
corp color, and name for face label for each of the children corporations 
(children are the owners).
Size determines dx, dy of the children through normalization of the constraining 
square, so on each iteration I need to bring along the containing squares.
x, y, dx, dy of each new contained square are determined through squarify.
