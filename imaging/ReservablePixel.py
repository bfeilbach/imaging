from imaging.exceptions import UnreservedPixelError

# A `ReservablePixel` represents a single pixel's RGB byte data.

class ReservablePixel:

    # By default, a `ReservablePixel`s is unreserved
    def __init__(self):
        reserved = False
        rgb_byte_data = b''

    # Reserve a `ReservablePixel` by assigning it a color
    def reserve(self, color):
        self.rgb_byte_data = color
        self.reserved = True

    # Return `True` if a `ReservablePixel` has been reserved
    def is_reserved(self):
        return self.reserved

    # Return the color that a `ReservablePixel` has been reserved with
    def get_rgb_byte_data(self):
        if self.reserved:
            return self.rgb_byte_data
        else:
            raise UnreservedPixelError
