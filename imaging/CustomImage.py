import random
import math

from PIL import Image   # Only used for `bytes -> `JPEG` transformation

from imaging.ReservablePixel import ReservablePixel
from imaging.RectangularRegion import RectangularRegion
from imaging.ColorGenerator import ColorGenerator

# A `CustomImage` is a wrapper object around a two-dimensional list of `ReservablePixel`s.
# The `CustomImage` can be manipulated by reserving `ReservablePixel`s - in other words,
# by assigning a color to a `ReservablePixel`.
#
# Image manipulation can be done in four ways:
#   1) Dividing a `CustomImage` into `RectangularRegion`s
#   2) Plotting any single-variable function across the `CustomImage`
#   3) Placing points (dots) on the `CustomImage`
#   4) Placing vertical lines (slices) on the `CustomImage`
#
# Once all image manipuation is complete, a `CustomImage` can be realized as
# a `JPEG` via `PIL.Image.frombytes()`

# Reservation visualization:
#
# (x, y)
#
# (0, 0), (1, 0), (2, 0), (3, 0) -> x
# (0, 1), (1, 1), (2, 1), (3, 1)
#   |
#   v
#   y

class CustomImage:

    # Provide dimensions and a `ColorGenerator` reference to instantiate a `CustomImage`
    def __init__(self, x_max, y_max, color_generator):
        # Populate image dimensions and underlying `ReservablePixel`s
        self.size = (x_max, y_max)
        self.reservations = [[ReservablePixel() for _ in range(x_max)] for _ in range(y_max)]
        self.final_image_byte_data = b''

        # Save reference to the provided `ColorGenerator`
        self.cg = color_generator

        # Populate `PIL`-specific arguments for eventual `bytes -> JPEG` construction
        self.mode = 'RGB'
        self.decoder_name = 'raw'
        self.decoder_args = (self.mode, 0, 1)

        # Allocate underlying data structures for image manipulation:

        # An image can be manipulated through `RectangularRegions`
        # By default, there is one `RectangularRegion` over the entire image.
        self.rec_regions = [RectangularRegion(0, x_max, 0, y_max)]

        # An image can be manipulated through the plotting of points, referred to as `dot`s
        # A single `dot` is simply a tuple of coordinates: `(x, y)`
        self.dots = [] 

        # An image can be manipulated through the plotting of vertical lines, referred to as slices

        # `self.vertical_slices` is of the type `{int : [(float, float)]}`
        # Each key `x` values to a `[(y_min, y_max)]`
        # This allows for multiple, non-contiguous `slice`s per `x` coordinate
        self.vertical_slices = {}
    
    # Internal getters and utilities

    def _get_x_max(self):
        return self.size[0]

    def _get_y_max(self):
        return self.size[1]

    # The internal `ReservablePixel`s are stored "upside down" compared to a cartesian grid.
    # Perform the translation to allow for normal cartesian plotting
    def _translate_y_coord_cartesian(self, y):
        return self._get_y_max() - 1 - y

    # Image construction

    # Transform all `ReservablePixel`s into a single `bytearray`
    def _construct_final_byte_string(self):
        # Extreme speed-up achieved via:
        # https://www.guyrutenberg.com/2020/04/04/fast-bytes-concatenation-in-python/

        # TODO error handling for when not all pixels are reserved

        # Allocate list to aggregate into
        byte_array = []

        # Append all `ReservablePixel`s
        for j in range(self._get_y_max()):
            for i in range(self._get_x_max()):
                byte_array.append(self.reservations[j][i].get_rgb_byte_data())

        # Concatenate all bytes
        self.final_image_byte_data = b''.join(byte_array)

    # Turn a `CustomImage` into a `JPEG` and open it
    def construct_and_show_jpeg(self):
        # `CustomImage` -> `bytes`
        self._construct_final_byte_string()

        # `bytes` -> `JPEG` using the default decoder
        jpeg = Image.frombytes(self.mode, self.size, self.final_image_byte_data,
            self.decoder_name, self.decoder_args)
        
        # Open the image
        jpeg.show()

    # Return `True` if all `ReservablePixel`s are reserved
    def are_all_pixels_reserved(self):
        for j in range(self._get_y_max()):
            for i in range(self._get_x_max()):
                if not self.reservations[j][i].is_reserved():
                    return False
        return True

    # General / direct image manipulation

    # Reserve a square of pixels with side length of `2k + 1`
    # This is similar to a brush/stroke size
    def _reserve_square(self, center_x: int, center_y: int, k: int, color=None):
        # Give the caller artistic control via optional `color` argument.
        # The user is in control of how often colors are generated.
        if color is None:
            color = self.cg.generate_color()

        # Avoid per-pixel bounds check by enforcing ranges now
        low_y = min(max(center_y - k, 0), self._get_y_max() - 1)
        high_y = min(max(center_y + k, 0), self._get_y_max() - 1)

        low_x = min(max(center_x - k, 0), self._get_x_max() - 1)
        high_x = min(max(center_x + k, 0), self._get_x_max() - 1)

        # Reserve all pixels within the square
        for j in range(low_y, high_y + 1):
            for i in range(low_x, high_x + 1):
                self.reservations[j][i].reserve(color)
    
    # Reserve the entire image as a single color
    def reserve_background_color(self, color):
        for j in range(self._get_y_max()):
            for i in range(self._get_x_max()):
                self.reservations[j][i].reserve(color)

    # Reserve the entire image as white
    def reserve_white_background(self):
        self.reserve_background_color(b'\xff\xff\xff')

    # Reserve the entire image as black
    def reserve_black_background(self):
        self.reserve_background_color(b'\x00\x00\x00')

    # Image manipulation via `RectangularRegion`s

    # Reserve all pixels within a `RectangularRegion` as a single color
    def _reserve_single_region_single_color(self, reg):
        color = self.cg.generate_color()
        xMin, xMax, yMin, yMax = reg.get_edges()

        for x in range(xMin, xMax):
            for y in range(yMin, yMax):
                self.reservations[y][x].reserve(color)
    
    # Reserve all `RectangularRegion`s, using the supplied `ColorGenerator` for each region
    def reserve_all_rectangular_regions(self):
        for reg in self.rec_regions:
            self._reserve_single_region_single_color(reg)

    # Pick a `RectangularRegion` at random and divide it into two `RectangularRegion`s
    def divide_random_rectangular_region_in_two(self):
        # Grab a `RectangularRegion` at random and alias it as `super_reg`
        super_reg_index = random.randrange(0, len(self.rec_regions))
        super_reg = self.rec_regions[super_reg_index]

        # Alias the dimensions and edges of `super_reg`
        super_width, super_height = super_reg.get_width(), super_reg.get_height()
        super_x_min, super_x_max, super_y_min, super_y_max = super_reg.get_edges()

        # Ensure `super_reg` is large enough to split in two
        _MIN_SIZE_TO_SPLIT = 2

        if super_width < _MIN_SIZE_TO_SPLIT or super_height < _MIN_SIZE_TO_SPLIT:
            # `super_reg` is too small to divide
            return

        # Determine if `super_reg` will be divided horizontally or vertically
        horiz_vert = bool(random.getrandbits(1))

        if horiz_vert:
            # Calculate the `x` coordinate that vertically divides `super_reg` into two
            halfway_x = super_x_min + (super_width // 2)

            # Instantiate the two new `RectangularRegion`s
            # Note that the `y` edges remain unchanged from `super_reg`
            reg_to_replace_super = RectangularRegion(super_x_min, halfway_x, super_y_min, super_y_max)
            reg_to_append        = RectangularRegion(halfway_x, super_x_max, super_y_min, super_y_max)

        else:
            # Calculate the `y` coordinate that horizontally divides `super_reg` into two
            halfway_y = super_y_min + (super_height // 2)     

            # Instantiate the two new `RectangularRegion`s
            # Note that the `x` edges remain unchanged from `super_reg`
            reg_to_replace_super = RectangularRegion(super_x_min, super_x_max, super_y_min, halfway_y)
            reg_to_append        = RectangularRegion(super_x_min, super_x_max, halfway_y, super_y_max)
        
        # Avoid O(n) removal of `super_reg` from our list by replacing it directly
        self.rec_regions[super_reg_index] = reg_to_replace_super
        self.rec_regions.append(reg_to_append)

    # Image manipulation via single-variable function plotting
    
    # Plot a single-variable function `func` over a `CustomImage`
    # If `color` is not specified, then use the `ColorGenerator` for each `x`
    def draw_single_variable_function(self, func, brush_size=1, color=None):
        # A function `f(x)` can be represented as a dictionary of the form `{x : f(x)}`
        # Currently, functions are plotted and reserved immediately, leaving no reason
        # to store the function for later. Thus, avoid the O(n) space cost of populating
        # the dictionary form of a function by immediately reserving it.

        for x in range(self._get_x_max()):
            # Invoke lambda to caluclate `f(x)`
            f_x = func(x)

            # Translate the y coordinate to cartesian
            f_x_cartesian = self._translate_y_coord_cartesian(f_x)

            # Reserve this `(x, f(x))` pair
            self._reserve_square(x, math.floor(f_x_cartesian), brush_size, color)

    # Image manipulation via `dots`

    # Add a `dot` at random coordinates to the `CustomImage`
    def add_random_dot(self):
        # Generate coordinates
        x = random.randrange(0, self._get_x_max())
        y = random.randrange(0, self._get_y_max())

        # Add `dot` to our underlying list
        dot = (x, y)
        self.dots.append(dot)

    # Given two `dot`s, plot a line between them
    def _connect_two_dots(self, dot_0, dot_1, brush_size):
        # Calculate the slope `m` and the intersect `b` of this line

        # Alias the `dot` coordinates
        # Recall: `dot` == `(x, y)`
        x_0, y_0 = dot_0
        x_1, y_1 = dot_1

        # Point-slope form:
        m = 0
        try:
            m = (y_1 - y_0) / (x_1 - x_0)
        except ZeroDivisionError:
            # If a slope of infinity is needed to connect the `dot`s,
            # effectively replace slope with the height of the image
            m = self._get_y_max()

        # With the slope `m`, use either `dot` to find the intersect `b`
        # of the connecting line.
        # This is just algebra applied to `y = mx + b`
        b = y_0 - (m * x_0)

        # Ensure the intercept `b` is an integer
        b = int(round(b))

        func = lambda x : (m * x) + b
        self.draw_single_variable_function(func, brush_size)

    # Calulate and plot lines between all of this `CustomImage`s `dot`s 
    def connect_all_dots(self, brush_size=1):
        # TODO validate optional variable
        # TODO raise exception when there are not enough dots to connect
        # Each `dot` has random coordinates, so simply traverse linearly through the list
        for i in range(0, len(self.dots) - 1):
            self._connect_two_dots(self.dots[i], self.dots[i + 1], brush_size)

    # Image manipulation via `vertical_slices`

    # Enforce image bounds and tuck away the logic of adding to `vertical_slices`
    # Recall: `vertical_slices` is keyed by `x` and valued by a list of `y` bounds
    def _add_vertical_slice(self, x, y_min, y_max):
        # TODO bounds check x as well

        # sanitize/saturate y
        y_min = min(max(math.floor(y_min), 0), self._get_y_max() - 1)
        y_max = min(max(math.floor(y_max), 0), self._get_y_max() - 1)
        new_val = (y_min, y_max)

        if x in self.vertical_slices:
            self.vertical_slices[x].append(new_val)
        else:
            self.vertical_slices[x] = [new_val]
        
    # Reserve all `vertical_slice`s, using the supplied `ColorGenerator` once per slice
    def reserve_all_vertical_slices(self):
        # Recall type of `vertical_slices`: `{x : [(y_min, y_max)]}`
        for x, slice_list in self.vertical_slices.items():
            # Each `x` may have multiple slices
            for curr_slice in slice_list:
                # Generate a color for this slice
                color = self.cg.generate_color()

                # Alias the slice as its underlying data: a range over `y`
                (curr_y_min, curr_y_max) = curr_slice

                # Reserve the entire slice
                for curr_y in range(curr_y_min, curr_y_max):
                    self.reservations[curr_y][x].reserve(color)

    # Add `vertical_slice`s of random heights to the `CustomImage` spanning
    # from `x_min` to `x_max`
    def create_random_vertical_slices(self, x_min, x_max, x_step_size=1):
        # TODO sanitize input
        for x in range(x_min, x_max, x_step_size):
            # Generate random `y` bounds for the slice
            y_bound_1 = random.randint(0, self._get_y_max())
            y_bound_2 = random.randint(0, self._get_y_max())

            # Order the random bounds
            curr_y_min = min(y_bound_1, y_bound_2)
            curr_y_max = max(y_bound_1, y_bound_2)

            self._add_vertical_slice(x, curr_y_min, curr_y_max)

    # Add `vertical_slice`s of random heights to the `CustomImage` spanning
    # from `x_min` to `x_max`. Each slice will be symmetric across the center of the image.
    # The image can optionally be partitioned vertically, where each partition will have its own
    # relative center.
    def create_symmetric_vertical_slices_from_center(self, x_min, x_max, x_step_size=1, num_partitions=1):
        # `n` partitions can be described by `n+1` bounds.
        # Ex: Drawing three parallel lines through a rectangle results in four segments.
        num_bounds = num_partitions + 1

        # Get the absolute height of the image
        abs_y_max = self._get_y_max()
        
        # Calculate the height of each partition
        partition_height = abs_y_max // num_partitions

        # Calculate the bounds that describe the desired partitions
        # Ex: for an image with height of 100,
        #   and `num_partitions` of 4: `y_bounds` == `[0, 25, 50, 75, 100]`
        #   and `num_partitions` of 1: `y_bounds` == `[0, 100]`
        y_bounds = [partition_height * i for i in range(num_bounds)]

        # Add slices to the `i`th partition
        for i in range(num_partitions):
            # Alias the bounds that describe this partition
            rel_y_min, rel_y_max = y_bounds[i], y_bounds[i + 1]
            
            # Calculate the relative center of this partition
            rel_center_y = rel_y_min + (partition_height // 2)

            # Traverse the `i`th partition horizontally
            for x in range(x_min, x_max, x_step_size):
                # For symmetric slices, it's easier to think about an `offset` that is applied
                # both above and below the relative center of the image, as opposed to a standard `height`.
                # Calculate the slice `offset` upper bound with two considerations:

                # Account for partition height
                partition_height_restraint = 1 / num_partitions

                # Account for the symmetry of the slice - the offset will be applied in two directions
                symmetric_slice_restraint = .4

                # Apply the considerations to calculate the upper bound
                slice_offset_upper_bound = abs_y_max * partition_height_restraint * symmetric_slice_restraint

                # Choose the actual slice offset
                curr_y_offset = random.randint(0, math.floor(slice_offset_upper_bound))

                # Calculate the symmetric `y` bounds for this slice
                curr_y_min = rel_center_y - curr_y_offset
                curr_y_max = rel_center_y + curr_y_offset

                # Add the symmetric slice
                self._add_vertical_slice(x, curr_y_min, curr_y_max)