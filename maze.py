import math
import cairo
import random

random.seed(0)

cellwidth = 10
dim = 22 * cellwidth

def coord(x, y):
    offset = cellwidth // 2
    return (x * cellwidth + offset, y * cellwidth + offset)

class Cell(object):
    def __init__(self, x, y):
        self.loc = (x, y)
        self.neighbors = set()
        self.walls = set()
        self.border = set()
        self.parent = None

    def add_neighbor(self, n):
        self.neighbors.add(n)
        self.walls.add(n)

    def add_border(self, n):
        self.border.add(n)

    def coords(self):
        return self.loc

    def render(self, ctx):
        path = (
            ((+1, 0), (0, -1)),
            ((0, +1), (1, 0)),
            ((-1, 0), (0, 1)),
            ((0, -1), (-1, 0)),
        )

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
        self.parent = None

    def visit(self, parent):
        self.parent = parent
    
    def visited(self):
        return self.parent != None
    
    def remove_wall(self, where):
        self.walls.remove(where)

    def __str__(self):
        return "[cell {}: n:{} w:{} b:{} p:{}]".format(
            self.loc,
            self.neighbors,
            self.walls,
            self.border,
            self.parent,
        )

class Maze(object):
    def __init__(self, dim):
        self.dim = dim
        self.border = set()

        radius = dim // 2
        self.cells = dict()
        for row in range(-radius, radius + 1):
            width = int(math.sqrt(radius**2 - row**2))
            for col in range(-width, width + 1):
                r, c = row + radius, col + radius
                self.cells[(r, c)] = Cell(r, c)

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
        for _, c in self.cells.items():
            c.render(ctx)

    def unvisit(self):
        for _, c in self.cells.items():
            c.unvisit()

    def drill(self):
        c = self.cells[(10, 20)]
        c.visit(True)
        stack = []
        stack.append((10, 20))
        while len(stack) > 0:
            cc = stack.pop()
            c = self.cells[cc]

            pc = c.parent
            if pc != None and pc != True:
                p = self.cells[pc]
                c.remove_wall(pc)
                p.remove_wall(cc)

            neighbors = [n for n in c.neighbors if not self.cells[n].visited()]
            for n in neighbors:
                self.cells[n].visit(cc)
            stack += neighbors
            random.shuffle(stack)

maze = Maze(20)
maze.drill()
surface = cairo.SVGSurface("maze.svg", dim, dim)
ctx = cairo.Context(surface)
ctx.set_tolerance(0.01)
ctx.set_line_width(0.5)
ctx.set_source_rgb(0, 0, 0)
maze.render(ctx)
ctx.stroke()
