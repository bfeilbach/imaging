import random

from imaging.ColorGenerator import ColorGenerator

# A `ColorGenerator` provides colors upon request.
# A color is a `bytearray` of three elements, one per RGB channel: red, green, blue.
#
# Every `ColorGenerator` has an `_internal_function` - a lambda that enforces the policy
# of a respective `ColorGenerator`.
# The policy for `RingColorGenerator` is this: store a pool (list) of colors and traverse it circularly
# in insertion order.
#
# This class also provides methods for populating the internal pool of colors.

class RingColorGenerator(ColorGenerator):

    # The optional parameter `initial_ring_index` is exposed for artistic control (when animating)
    def __init__(self, rgb_rel_min=ColorGenerator.RGB_MIN, rgb_rel_max=ColorGenerator.RGB_MAX, initial_ring_index=0):
        # Sanitize input and optionally limit the range of band data for this instance
        self.rgb_rel_min = min(max(rgb_rel_min, self.RGB_MIN), self.RGB_MAX)
        self.rgb_rel_max = min(max(rgb_rel_max, self.RGB_MIN), self.RGB_MAX)

        # Allocate underlying list and index pointer needed for the ring policy
        self.pool = []
        self.curr_ring_index = initial_ring_index

        # Set policy
        self._internal_function = lambda : self._grab_next_color_and_advance()

    # Perform the circular traversal and return the next color
    def _grab_next_color_and_advance(self):
        # TODO add empty pool exception
        # Maintain `self.curr_ring_index`
        if self.curr_ring_index >= len(self.pool) - 1:
            # Reset to beginning of the list
            self.curr_ring_index = 0
        else:
            self.curr_ring_index += 1
        
        return self.pool[self.curr_ring_index]

    # Methods for populating `self.pool`

    # Parse a String representing a color's rgb data and add that color to `self.pool`
    # Ex: FF0010 -> \xff\x00\x10
    def add_color_to_pool_from_rgb_string(self, rgb_str, num_insertions=1):
        # TODO validate input

        # Interpret each String slice as hex / base 16
        hex_base = 16

        # Parse String into integer channel data
        r = int(rgb_str[0:2], hex_base)
        g = int(rgb_str[2:4], hex_base)
        b = int(rgb_str[4:6], hex_base)

        # Create `bytearray` from integer channel data
        color = self.ints_to_rgb(r, g, b)

        # Append, possibly more than once per color, for artistic control
        for i in range(num_insertions):
            self.pool.append(color)

    # Parse a Coolors color palette URL and add append the palette's colors to our pool.
    #
    # Coolors is a website for creating and sharing combinations of colors called palettes.
    # The entire URL is taken as input in hopes to maintain a trace to the original palette creator. :)
    # Example input: https://coolors.co/7400b8-6930c3-5e60ce-5390d9-4ea8de-48bfe3-56cfe1-64dfdf-72efdd-80ffdb
    def add_palette_to_pool_from_url(self, url):
        total_rgb_str = url.split('/')[-1]
        rgbs = total_rgb_str.split('-')

        # Unlike most parts of the system, here, a color is represented in hex, but as a String
        for rgb_str in rgbs:
            self.add_color_to_pool_from_rgb_string(rgb_str, num_insertions=6)

    # Traverse the RGB state space to populate `self.pool` with colors from
    # a smooth rainbow gradient
    def add_rainbow_to_pool(self, step_size=1):
        # TODO santize `step_size` - can't be negative or zero

        # Alias the single-channel bounds of this `ColorGenerator`
        _min, _max = self.rgb_rel_min, self.rgb_rel_max

        # A smooth rainbow gradient is achieved by traversing the RGB state space
        # one channel at a time, while the other two channels are held constant at
        # either relative extrema:

        # Incrementing `blue` yields Red to Magenta
        for b in range(_min, _max, step_size):
            self.pool.append(self.ints_to_rgb(_max, _min, b))

        # Decrementing `red` yields Magenta to Blue
        for r in range(_max, _min, step_size * -1):
            self.pool.append(self.ints_to_rgb(r, _min, _max))

        # Incrementing `green` yields Blue to Teal
        for g in range(_min, _max, step_size):
            self.pool.append(self.ints_to_rgb(_min, g, _max))

        # Decrementing `blue` yields Teal to Green
        for b in range(_max, _min, step_size * -1):
            self.pool.append(self.ints_to_rgb(_min, _max, b))

        # Incrementing `red` yields Green to Yellow
        for r in range(_min, _max, step_size):
            self.pool.append(self.ints_to_rgb(r, _max, _min))

        # Decrementing `green` yields Yellow to Red
        for g in range(_max, _min, step_size * -1):
            self.pool.append(self.ints_to_rgb(_max, g, _min))