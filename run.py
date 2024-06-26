import os
import sys
import asyncio
import aiohttp
from PIL import Image


async def unscramble_image(input_image_path, output_image_path):
    try:
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
            piece = input_image.crop(
                (source_x, source_y, source_x + piece_width, source_y + piece_height)
            )

            # Paste the unscrambled piece onto the output image
            unscrambled_image.paste(piece, (piece_x, piece_y))

        # Create a new image to hold the final result
        result_image = Image.new("RGBA", (width, height))

        # Paste the original image to it
        result_image.paste(input_image, (0, 0))

        # Paste the unscrambled image on top of the original image
        result_image.paste(unscrambled_image, (0, 0), mask=unscrambled_image)

        # Convert the result image back to RGB format
        result_image = result_image.convert("RGB")

        # Create the output file name for the unscrambled image
        output_unscrambled_image_path = output_image_path.replace(
            ".jpg", "_unscrambled.jpg"
        )

        # Save the unscrambled image as JPEG
        result_image.save(output_unscrambled_image_path, "JPEG")

        pass
    except Exception as e:
        print(f"Error unscrambling image: {e}")


# Retrieve the URL of the JSON file from the command-line argument
json_url = sys.argv[1] + ".json"


async def download_image(session, image_url, folder_name):
    try:
        filename = os.path.basename(image_url)
        filename = os.path.splitext(filename)[0] + ".jpg"
        filepath = os.path.join(folder_name, filename)

        async with session.get(image_url) as response:
            with open(filepath, "wb") as file:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    file.write(chunk)

        # Return the filepath to be used for unscrambling
        return filepath
    except Exception as e:
        print(f"Error downloading image: {e}")


async def process_image(session, image_url, folder_name):
    try:
        # Download image
        downloaded_filepath = await download_image(session, image_url, folder_name)
        # Unscramble image
        await unscramble_image(downloaded_filepath, downloaded_filepath)
        # Delete the scrambled image
        os.remove(downloaded_filepath)
    except Exception as e:
    print(f"Error processing image: {e}")

async def download_comic(json_url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        }
        # Fetch the JSON file from the URL
        async with aiohttp.ClientSession() as session:
            async with session.get(json_url, headers=headers) as response:
                data = await response.json()

        series_title = data["readableProduct"]["series"]["title"]
        product_title = data["readableProduct"]["title"]

        folder_name = f"{series_title} - {product_title}"

        # Create the folder if it doesn't exist
        os.makedirs(folder_name, exist_ok=True)

        # Iterate over the list of image URLs and process each image asynchronously
        image_urls = []

        for page in data["readableProduct"]["pageStructure"]["pages"]:
            if "src" in page:
                image_urls.append(page["src"])  # Add image URL to the list

        async with aiohttp.ClientSession() as session:
            tasks = []
            for image_url in image_urls:
                task = process_image(session, image_url, folder_name)
                tasks.append(task)

            await asyncio.gather(*tasks)

        print(f"File saved in {folder_name}.")

    except Exception as e:
        print(f"Error in overall processing: {e}")


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(download_comic(json_url))
