import os
import argparse
from PIL import Image

def unscramble_image(input_image_path, output_image_path):
    # Open the input image
    input_image = Image.open(input_image_path)

    # Get the dimensions of the input image
    width, height = input_image.size

    # Ensure the input image dimensions match the fixed size
    assert width == 844, "Image width must be 844 pixels"
    assert height == 1200, "Image height must be 1200 pixels"

    # Calculate the width and height of each piece
    piece_width = 832 // 4
    piece_height = 1184 // 4

    # Create a new image to hold the unscrambled image
    unscrambled_image = Image.new("RGBA", (width, height))

    # Define the order for unscrambling the pieces
    order = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11]

    # Iterate over each piece in the input image
    for piece_index, target_index in enumerate(order):
        # Calculate the row and column indices of the piece
        row = target_index // 4
        col = target_index % 4

        # Calculate the coordinates of the piece
        piece_x = col * piece_width
        piece_y = row * piece_height

        # Get the corresponding source piece from the input image
        source_x = piece_index % 4 * piece_width
        source_y = piece_index // 4 * piece_height
        piece = input_image.crop((source_x, source_y, source_x + piece_width, source_y + piece_height))

        # Paste the unscrambled piece onto the output image
        unscrambled_image.paste(piece, (piece_x, piece_y))

    # Create a new image to hold the final result
    result_image = Image.new("RGBA", (width, height))

    # Paste the original image on top of the unscrambled image
    result_image.paste(input_image, (0, 0))

    # Paste the unscrambled image on top of the original image
    result_image.paste(unscrambled_image, (0, 0), mask=unscrambled_image)

    # Convert the result image back to RGB format
    result_image = result_image.convert("RGB")

    # Create the output file name for the unscrambled image
    output_unscrambled_image_path = output_image_path.replace(".jpg", "_unscrambled.jpg")

    # Save the unscrambled image as JPEG
    result_image.save(output_unscrambled_image_path, "JPEG")

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Image unscrambling program")
parser.add_argument("-i", "--input", help="Input image file path or folder")
parser.add_argument("-o", "--output", help="Output image file path or folder")
args = parser.parse_args()

# Check if input and output file paths are provided
if args.input and args.output:
    # Check if input is a file
    if os.path.isfile(args.input):
        unscramble_image(args.input, args.output)
        print("Image unscrambling completed.")
    # Check if input is a folder
    elif os.path.isdir(args.input):
        # Get a list of image files in the input folder
        image_files = [file for file in os.listdir(args.input) if file.lower().endswith((".jpg", ".jpeg"))]

        # Iterate over the image files and process each one
        for image_file in image_files:
            # Construct the input and output file paths for each image
            input_image_path = os.path.join(args.input, image_file)
            output_image_path = os.path.join(args.output, image_file)

            # Process the image
            unscramble_image(input_image_path, output_image_path)

        print("Image unscrambling completed for all images in the folder.")
    else:
        print("Invalid input. Please provide a valid input file or folder.")
else:
    print("Please provide input and output file paths or folders using -i and -o options.")
