import math

from imaging.CustomImage import CustomImage
from imaging.RingColorGenerator import RingColorGenerator

def main():

    # Define image dimensions
    x_max, y_max = 1920, 1080

    # Instantiate a `ColorGenerator`
    # This one is a bit more interesting - it has a pool of colors that it cycles through
    cg = RingColorGenerator()

    # Populate our pool with the colors of the rainbow
    cg.add_rainbow_to_pool(step_size=30)
    
    # Instantiate a `CustomImage`
    my_image = CustomImage(x_max, y_max, cg)

    # Set the background color
    my_image.reserve_white_background()

    # Declare and plot two functions over the image, using our `ColorGenerator` behind the scenes
    linear_func = lambda x : x + 50
    my_image.draw_single_variable_function(linear_func, brush_size=3)

    sine_func = lambda x : 200 * math.sin(x/100) + y_max / 2
    my_image.draw_single_variable_function(sine_func, brush_size=20)

    # Open the `CustomImage` as a JPEG
    my_image.construct_and_show_jpeg()

if __name__ == "__main__":
    # execute only if run as a script
    main()