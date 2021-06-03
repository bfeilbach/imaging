import math

from imaging.CustomImage import CustomImage
from imaging.RingColorGenerator import RingColorGenerator

# Coolors is a website for sharing combinations (palettes) of colors.
# We'll use these colors in our image.
reds_url = 'https://coolors.co/641220-6e1423-85182a-a11d33-a71e34-b21e35-bd1f36-c71f37-da1e37-e01e37'

def main():

    # Define image dimensions
    x_max, y_max = 1920, 1080

    # Instantiate a `ColorGenerator`
    # This one is a bit more interesting - it has a pool of colors that it cycles through
    cg = RingColorGenerator()

    # Populate our pool with the colors of a Coolors Palette
    cg.add_palette_to_pool_from_url(reds_url)
    
    # Instantiate a `CustomImage`
    my_image = CustomImage(x_max, y_max, cg)

    # Manually invoke our `ColorGenerator` and set the background color of the image
    bg_color = cg.generate_color()
    my_image.reserve_background_color(bg_color)

    # Declare and plot sine functions over the image, using our `ColorGenerator` behind the scenes
    for y_offset in range(0, y_max, 200):
        f_sine = lambda x : 100 * math.sin(x/100) + y_offset
        my_image.draw_single_variable_function(f_sine, brush_size=40)

    # Open the `CustomImage` as a JPEG
    my_image.construct_and_show_jpeg()

if __name__ == "__main__":
    # execute only if run as a script
    main()