import math
import cairo

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

    def add_neighbor(self, x, y):
        self.neighbors.add((x, y))
        self.walls.add((x, y))

    def add_border(self, x, y):
        self.border.add((x, y))

    def coords(self):
        return self.loc

    def render(self, ctx):
        origin = self.loc
        x, y = origin
        ctx.move_to(*coord(x, y))
        path = (
            ((+1, 0), (0, 1)),
            ((0, +1), (1, 0)),
            ((-1, 0), (0, -1)),
            ((0, -1), (-1, 0)),
        )

        prev = origin
        for delta, ndelta in path:
            px, py = prev
            dx, dy = delta
            cx, cy = px + dx, py + dy
            cur = (cx, cy)
            nx, ny = ndelta
            nb = (x + nx, y + ny)
            if nb in self.walls or nb in self.border:
                ctx.line_to(*coord(cx, cy))
            else:
                ctx.move_to(*coord(cx, cy))
            prev = cur
            

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
                    self.cells[nxy].add_neighbor(*c)
                    self.cells[c].add_neighbor(*nxy)
                else:
                    self.border.add(nxy)
                    self.cells[c].add_border(*nxy)
    
    def render(self, ctx):
        for c in self.cells:
            self.cells[c].render(ctx)

maze = Maze(20)
surface = cairo.SVGSurface("maze.svg", dim, dim)
ctx = cairo.Context(surface)
ctx.set_tolerance(0.01)
ctx.set_line_width(0.5)
ctx.set_source_rgb(0, 0, 0)
maze.render(ctx)
ctx.stroke()
