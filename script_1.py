#import turtle
from svg_turtle import SvgTurtle
import numpy as np

"""Todo:
- change how ending_sides is set to ensure it works with density
- change how school is drawn to have half the lines
"""

# constants:

screen_width = 1600
screen_height = screen_width

# default values:

d_pen_colour = "white" # ink: "#06080F"; grey: "#A0A0A0"
d_pen_size = 2

d_density = 1
d_shape_centre = (0,0)
d_shape_angle_offset = np.pi/2
d_precision = 0.05


# function definitions:

def get_var_name(variable):
    for name, value in globals().items(): # searching through all global variables for variable
        if value is variable:
            return name


# class definitions:

class Shape:
    """Superclass for specific shape subclasses."""
    def __init__(self, radius, centre=d_shape_centre):
        # checking attributes:
        if radius <= 0:
            raise ValueError("radius must be > 0.")
        
        # assigning attributes:
        self.radius = radius
        self.centre = centre
    
    def draw(self, pen : SvgTurtle):
        raise NotImplementedError("Subclasses must implement this method.")
    
class RegularPolygon(Shape):
    """A regular polygon with its size defined by the smallest radius of circle it can fit within.
    \n Attributes:
    - density - the number of edges "skipped" + 1 (e.g. a pentagon's is 1, but a pentagram's is 2); density <= (sides - 1) / 2 (see Wikipedia for a more in-depth explanation: https://en.wikipedia.org/wiki/Density_(polytope)#Polygons)
    - angle_offset - the amount the polygon is rotated anticlockwise about its centre (in radians)
    """
    def __init__(self, radius, sides : int, density=d_density, centre=d_shape_centre, angle_offset=d_shape_angle_offset):
        # assigning attributes:
        super().__init__(radius, centre)
        self.sides = sides
        self.density = density
        self.angle_offset = angle_offset
    
    def draw(self, pen : SvgTurtle):
        # moving to first vertex:
        pen.up()
        pen.goto(self.centre[0] + self.radius, self.centre[1])
        pen.down()

        # drawing lines between vertices:
        i = 0
        while i < self.sides:
            # moving to home vertex:
            pen.up()
            home_angle = ((2 * i * np.pi) / self.sides) + self.angle_offset
            home_x = self.radius * np.cos(home_angle) + self.centre[0]
            home_y = self.radius * np.sin(home_angle) + self.centre[1]
            pen.goto(home_x, home_y) # home vertex

            # moving to destination vertex, skipping a number of vertexes equal to density - 1:
            i += self.density
            destination_angle = ((2 * i * np.pi) / self.sides) + self.angle_offset
            destination_x = self.radius * np.cos(destination_angle) + self.centre[0]
            destination_y = self.radius * np.sin(destination_angle) + self.centre[1]
            pen.down()
            pen.goto(destination_x, destination_y) # destination vertex
            
            # set i to new home vertex (1 after the previous home vertex):
            i -= self.density - 1

class Circle(Shape):
    """A circle approximated by a regular polygon.
    \n Attributes:
    - precision - the angular step between vertexes; a smaller value gives a smoother circle
    """
    def __init__(self, radius, centre=d_shape_centre, precision=d_precision):
        # checking attributes:
        if precision <= 0:
            raise ValueError("precision must be > 0.")
    
        # assigning attributes:
        super().__init__(radius, centre)
        self.precision = precision

    def draw(self, pen : SvgTurtle):
        sides = round((2 * np.pi) / self.precision) # number of sides for the circle approximation
        poly = RegularPolygon(self.radius, sides, centre=self.centre, angle_offset=0)
        poly.draw(pen)

class CircumscribedRegularPolygon(RegularPolygon, Circle):
    """Draws a circle with a given radius and the largest regular polygon with a given number of sides that fits within it.
    \n Attributes:
    - density - the number of edges "skipped" + 1 (e.g. a pentagon's is 1, but a pentagram's is 2); density <= (sides - 1) / 2 (see Wikipedia for a more in-depth explanation: https://en.wikipedia.org/wiki/Density_(polytope)#Polygons)
    - angle_offset - the amount the polygon is rotated anticlockwise about its centre (in radians)
    - precision - the angular step between vertexes; a smaller value gives a smoother circle
    """
    def __init__(self, radius, sides, density=d_density, centre=d_shape_centre, angle_offset=d_shape_angle_offset, precision=d_precision):
        RegularPolygon.__init__(self, radius, sides, density, centre, angle_offset)
        Circle.__init__(self, radius, centre, precision)

    def draw(self, pen : SvgTurtle):
        circle = Circle(self.radius, self.centre, self.precision)
        regular_polygon = RegularPolygon(self.radius, self.sides, self.density, self.centre, self.angle_offset)

        circle.draw(pen)
        regular_polygon.draw(pen)

class Diagram:
    num_outer_circles = 6 # for the 6 attribute spell model
    # useful constants:
    sin_phi = np.sin(np.pi / num_outer_circles) # constant used for radius and position of outer circles
    position_multiplier = 1 / (1 - sin_phi)
    radius_multiplier = sin_phi * position_multiplier
    angle_offset = np.pi / 2 # makes it symmetrical across the line x=0 instead of y=0

    # new SvgTurtle means that it generates a new image each time
    pen = SvgTurtle(screen_width, screen_height)
    pen.radians()
    pen.pensize(d_pen_size)
    pen.pencolor(d_pen_colour)

    def __init__(self, school: int | None = None, _range=0, duration=0, size=0, speed=0, potency=0, central_radius : int | None = None, edge_spacing=5):
        # spell attributes:
        schools = { None : 0,
            "divination": 1,
            "elementalism": 2,
            "abjuration": 3,
            "illusion": 4,
            "restoration": 5,
            "conjuration": 6,
            "necromancy": 7,
            "evocation": 8
        }
        self.school = schools[school]
        self._range = _range
        self.duration = duration
        self.size = size
        self.speed = speed
        self.potency = potency

        # fitting diagram on screen
        if central_radius == None:
            length = min(screen_width, screen_height)
            self.central_radius = (0.5 * length / (1 + (2 * self.radius_multiplier))) - edge_spacing
        else:
            self.central_radius = central_radius
        self.outer_radius = self.radius_multiplier * self.central_radius

        centres = []
        for k in range(self.num_outer_circles):
            theta = ((2 * np.pi * k) / self.num_outer_circles) + self.angle_offset
            x = self.position_multiplier * self.central_radius * np.cos(theta)
            y = self.position_multiplier * self.central_radius * np.sin(theta)
            centres.append((x, y))
        
        # sigils:
        self.school_sigil = CircumscribedRegularPolygon(self.central_radius, 2 * self.school, self.school, centre=centres[0])
        self.range_sigil = CircumscribedRegularPolygon(self.outer_radius, 3 * self._range, self._range, centre=centres[1])
        self.duration_sigil = CircumscribedRegularPolygon(self.outer_radius, 4 * self.duration, self.duration, centre=centres[2])
        self.size_sigil = CircumscribedRegularPolygon(self.outer_radius, 5 * self.size, self.size, centre=centres[3])
        self.speed_sigil = CircumscribedRegularPolygon(self.outer_radius, 6 * self.speed, self.speed, centre=centres[4])
        self.potency_sigil = CircumscribedRegularPolygon(self.outer_radius, 7 * self.potency, self.potency, centre=centres[5])
        self.central_sigil = Circle(self.central_radius)
        self.outer_sigil = Circle(self.central_radius + 2 * self.outer_radius)

        self.sigils = [ self.school_sigil, self.range_sigil, 
                        self.duration_sigil, self.size_sigil, 
                        self.speed_sigil, self.potency_sigil, 
                        self.central_sigil, self.outer_sigil ]
        
    def draw(self):
        for shape in self.sigils:
            shape.draw(self.pen)

    def create_and_save_image(self, file_name : str | None = None):
        self.draw()

        if file_name == None:
            file_name = get_var_name(self)
        self.pen.save_as(f"{file_name}.svg")

# variables/objects:

magic_missile = Diagram(None, 3, 1, 1, 4, 1)
wall_of_fire = Diagram("evocation", 2, 2, 5, 0, 4)
blade_of_disaster = Diagram("conjuration", 2, 3, 2, 1, 9)

spells = [ magic_missile, wall_of_fire, blade_of_disaster ]

# creating images:

for spell in spells:
    spell.create_and_save_image()