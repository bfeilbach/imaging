import random

# A `ColorGenerator` provides colors upon request.
# A color is a `bytearray` of three elements, one per RGB channel: red, green, blue.
#
# `ColorGenerator` is at the top of an inheritance hierarchy. Derivative instances
# generate colors under different policies. This allows for artistic control.
# Every `ColorGenerator` has an `_internal_function` - a lambda that enforces the policy
# of a respective `ColorGenerator`.
# The policy for the parent-level `ColorGenerator` is this: always generate the color black.
#
# Lastly, being at the top of the inheritance hierarchy, `ColorGenerator` provides
# general utility functions for channel data transformation.

class ColorGenerator:

    # Constant bounds:
    # A single byte can only represent integer values within (0, 2^8 - 1) == (0, 255).
    # This range can be restricted further via `rgb_rel_min` and `rgb_rel_max`.
    RGB_MIN = 0
    RGB_MAX = 255

    def __init__(self, rgb_rel_min=RGB_MIN, rgb_rel_max=RGB_MAX):
        # Sanitize input and optionally limit the range of band data for this instance
        self.rgb_rel_min = min(max(rgb_rel_min, self.RGB_MIN), self.RGB_MAX)
        self.rgb_rel_max = min(max(rgb_rel_max, self.RGB_MIN), self.RGB_MAX)

        # Set policy
        always_generate_black = lambda : self.int_to_grey_rgb(0)
        self._internal_function = always_generate_black

    # Invoke the internal function
    # NOTE: Every `ColorGenerator` derivative will also call this, but with a
    # different `_internal_function`, and thus, a different policy
    def generate_color(self):
        return self._internal_function()

    # Utility functions:
    
    # Transform one integer channel value into a single hex component.
    # A hex component is a byte of hex data, without the prepended '0x'.
    # Ex: 255 -> ff
    # Ex: 5 -> 05
    def _int_to_hex_component(self, i: int):
        # An integer of value < 16 will be represented as `0x{foo}`, where `len(foo)` == 1.
        # This must be detected and accounted for.
        _SINGLE_HEX_THRESHOLD = 16

        # In either case, remove the prepended '0x' so that we can combine rgb into one string
        if i < _SINGLE_HEX_THRESHOLD:
            # Ensure a two-digit hex component is returned
            return '0' + hex(i)[2:]
        else:
            return hex(i)[2:]

    # Transform three integer channel values into a single `bytearray`.
    # Ex: (255, 0, 15) -> \xff\x00\x0e
    def ints_to_rgb(self, r: int, g: int, b: int):
        # Maintain range / sanitize input for each channel
        r = min(max(r, self.rgb_rel_min), self.rgb_rel_max)
        g = min(max(g, self.rgb_rel_min), self.rgb_rel_max)
        b = min(max(b, self.rgb_rel_min), self.rgb_rel_max)

        # Construct r, g, and b and represent the three channels as a `bytearray`
        rgb = self._int_to_hex_component(r) + self._int_to_hex_component(g) + self._int_to_hex_component(b)
        return bytearray.fromhex(rgb)

    # Transform an integer intensity into a single `bytearray` representing a grey color.
    # NOTE: By definition, greys have equal channel values for r, g, b.
    # Thus, `i` represents intensity/brightness
    def int_to_grey_rgb(self, i: int):
        return self.ints_to_rgb(i, i, i)