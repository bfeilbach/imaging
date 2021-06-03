from imaging.CustomImage import CustomImage
from imaging.RingColorGenerator import RingColorGenerator

# Coolors is a website for sharing combinations (palettes) of colors.
# We'll use these colors in our image.
reds_url = 'https://coolors.co/641220-6e1423-85182a-a11d33-a71e34-b21e35-bd1f36-c71f37-da1e37-e01e37'
yellows_url = 'https://coolors.co/007f5f-2b9348-55a630-80b918-aacc00-bfd200-d4d700-dddf00-eeef20-ffff3f'
oranges_url = 'https://coolors.co/ff4800-ff5400-ff6000-ff6d00-ff7900-ff8500-ff9100-ff9e00-ffaa00-ffb600'
blues_url = 'https://coolors.co/03045e-023e8a-0077b6-0096c7-00b4d8-48cae4-90e0ef-ade8f4-caf0f8'

def main():

    # Define image dimensions
    x_max, y_max = 1920, 1080

    # Instantiate a `ColorGenerator`
    # This one is a bit more interesting - it has a pool of colors that it cycles through
    cg = RingColorGenerator()

    # Populate our pool with the colors of a few Coolors Palettes
    cg.add_palette_to_pool_from_url(reds_url)
    cg.add_palette_to_pool_from_url(yellows_url)
    cg.add_palette_to_pool_from_url(oranges_url)
    cg.add_palette_to_pool_from_url(blues_url)
    
    # Instantiate a `CustomImage`
    my_image = CustomImage(x_max, y_max, cg)

    # Set the background color
    my_image.reserve_black_background()

    # Place random `vertical_slices` across the entire image
    my_image.create_random_vertical_slices(0, x_max, x_step_size=9)

    # Reserve each `vertical_slice` using our `ColorGenerator`
    my_image.reserve_all_vertical_slices()

    # Open the `CustomImage` as a JPEG
    my_image.construct_and_show_jpeg()

if __name__ == "__main__":
    # execute only if run as a script
    main()