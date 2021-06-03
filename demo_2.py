from imaging.CustomImage import CustomImage
from imaging.RingColorGenerator import RingColorGenerator

# Coolors is a website for sharing combinations (palettes) of colors.
# We'll use these colors in our image.
oranges_url = 'https://coolors.co/ff4800-ff5400-ff6000-ff6d00-ff7900-ff8500-ff9100-ff9e00-ffaa00-ffb600'

def main():

    # Define image dimensions
    x_max, y_max = 1920, 1080

    # Instantiate a `ColorGenerator`
    # This one is a bit more interesting - it has a pool of colors that it cycles through
    cg = RingColorGenerator()

    # Populate our pool with the colors of a Coolors Palette
    cg.add_palette_to_pool_from_url(oranges_url)
    
    # Instantiate a `CustomImage`
    my_image = CustomImage(x_max, y_max, cg)

    # Set the background color
    my_image.reserve_white_background()

    # Repetitively divide the image into `RectangularRegion`s
    num_divisions = 35

    for _ in range(num_divisions):
        my_image.divide_random_rectangular_region_in_two()

    # Apply a color to each `RectangularRegion` using our `ColorGenerator` behind the scenes
    my_image.reserve_all_rectangular_regions()

    # Open the `CustomImage` as a JPEG
    my_image.construct_and_show_jpeg()

if __name__ == "__main__":
    # execute only if run as a script
    main()