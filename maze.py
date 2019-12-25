# Generate a circular maze into `maze.svg`.

import math
import cairo
import random

# Fix the maze so that we can reproduce the result.
random.seed(0)

# Width of a square in SVG units (pixels).
cellwidth = 10

# Size of the image, including a small margin.
dim = 22 * cellwidth

def coord(x, y):
    """Convert a maze cell coordinate to an SVG coordinate."""
    offset = cellwidth // 2
    return (x * cellwidth + offset, y * cellwidth + offset)

class Cell(object):
    """A single cell in the maze."""

    def __init__(self, x, y):
        self.loc = (x, y)
        self.neighbors = set()
        self.walls = set()
        self.border = set()
        self.parent = None

    def add_neighbor(self, n):
        """Remember a neighbor cell coordinate."""
        self.neighbors.add(n)
        self.walls.add(n)

    def add_border(self, n):
        """Remember a border cell coordinate."""
        self.border.add(n)

    def coords(self):
        """Where are we?"""
        return self.loc

    def render(self, ctx):
        """Render this cell."""

        # Offsets for line drawing, and corresponding
        # offsets to neighbor.
        path = (
            ((+1, 0), (0, -1)),
            ((0, +1), (1, 0)),
            ((-1, 0), (0, 1)),
            ((0, -1), (-1, 0)),
        )

        # Walk around the edge of the cell drawing walls
        # where appropriate.
        origin = self.loc
        x, y = origin
        prev = origin
        for delta, ndelta in path:
            dx, dy = delta
            nx, ny = ndelta
            px, py = prev
            cx, cy = px + dx, py + dy
            nb = (x + nx, y + ny)
            if nb in self.walls or nb in self.border:
                ctx.move_to(*coord(px, py))
                ctx.line_to(*coord(cx, cy))
            cur = (cx, cy)
            prev = cur
            
    def unvisit(self):
        """Mark this cell as unvisited."""
        self.parent = None

    def visit(self, parent):
        """Mark this cell as visited with the given parent."""
        self.parent = parent
    
    def visited(self):
        """Has this cell been visited?"""
        return self.parent != None
    
    def remove_wall(self, where):
        """Remove a wall from this cell."""
        self.walls.remove(where)

    def __str__(self):
        """Render this cell for debugging."""
        return "[cell {}: n:{} w:{} b:{} p:{}]".format(
            self.loc,
            self.neighbors,
            self.walls,
            self.border,
            self.parent,
        )

class Maze(object):
    """A collection of cells with auxiliary information."""
    def __init__(self, dim):
        self.dim = dim
        self.border = set()

        # Mark all the cells that are part of the maze.
        radius = dim // 2
        self.cells = dict()
        for row in range(-radius, radius + 1):
            width = int(math.sqrt(radius**2 - row**2))
            for col in range(-width, width + 1):
                r, c = row + radius, col + radius
                self.cells[(r, c)] = Cell(r, c)

        # Set up all the neighbors and borders.
        for c in self.cells:
            x, y = c
            neighbors = (
                (x + 1, y),
                (x - 1, y),
                (x, y + 1),
                (x, y - 1),
            )
            for nxy in neighbors:
                if nxy in self.cells:
                    self.cells[nxy].add_neighbor(c)
                    self.cells[c].add_neighbor(nxy)
                else:
                    self.border.add(nxy)
                    self.cells[c].add_border(nxy)
    
    def render(self, ctx):
        """Render each cell in the maze."""
        # XXX This will result in each wall being drawn
        # twice. Better would be to build up a set of walls
        # and render them all in one pass.
        for _, c in self.cells.items():
            c.render(ctx)

    def unvisit(self):
        """Unvisit all cells in the maze."""
        for _, c in self.cells.items():
            c.unvisit()

    def drill(self):
        """Path the maze."""
        # XXX This code should remove the entrance (border)
        # wall. It should probably also clear a circle for
        # Santa in the center before generation.

        # XXX Hardcode the origin for now.
        c = self.cells[(10, 20)]
        # XXX Gross hack to deal with the first cell having
        # no parent.
        c.visit(True)

        # DFS the maze, but shuffle the stack after each
        # path step. So effectively the stack is just an
        # open list.
        stack = []
        stack.append((10, 20))
        while len(stack) > 0:
            cc = stack.pop()
            c = self.cells[cc]

            # Clear path to parent.
            pc = c.parent
            if pc != None and pc != True:
                p = self.cells[pc]
                c.remove_wall(pc)
                p.remove_wall(cc)

            # Add the neighbors to the open list.
            neighbors = [n for n in c.neighbors
                         if not self.cells[n].visited()]
            for n in neighbors:
                self.cells[n].visit(cc)
            stack += neighbors
            
            # Shuffle for next round.
            random.shuffle(stack)

# Make the maze.
maze = Maze(20)
maze.drill()

# Render the maze.
surface = cairo.SVGSurface("maze.svg", dim, dim)
ctx = cairo.Context(surface)
ctx.set_tolerance(0.01)
ctx.set_line_width(0.5)
ctx.set_source_rgb(0, 0, 0)
maze.render(ctx)
ctx.stroke()
