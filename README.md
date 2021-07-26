# iterative_treemap_megacorp
A recursive Treemap program to map megacorp ownership (could have other uses with directed tree data)

Each corporation is owned (stock) by other "investor" corporations.
This program is designed to make a Treemap of which corporations own which.
Since each owner corporation is also owned by other corporations
this requires an interative approach to determine real ownership.

In the end I need x, y, width (dx), height (dy), face color, amd face label for a box.
Each box in the Treemap represents the size of ownership a corporation has for 
that parent corp.
On each iteration I need to access the db to get the size (percent ownership),
corp color, and name for face label for each of the children (children are the owners) corps.
Size determines dx, dy through normalization of the containing square,
so on each iteration I need to bring along the containing square.
x, y, dx, dy of each new contained square are determined through squarify.
