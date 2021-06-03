class RectangularRegion:

    # Instantiate a `RectangularRegion` from its four containing edges
    def __init__(self, x_min, x_max, y_min, y_max):
        # TODO enforce x_min < x_max, etc?

        # Save the edges
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

        # Calculate the dimensions of this region
        self.width = x_max - x_min
        self.height = y_max - y_min

    # Return a 4-tuple of a `RectangularRegion`s edges
    def get_edges(self):
        return self.x_min, self.x_max, self.y_min, self.y_max

    # Return the width of a `RectangularRegion`
    def get_width(self):
        return self.width
    
    # Return the height of a `RectangularRegion`
    def get_height(self):
        return self.height