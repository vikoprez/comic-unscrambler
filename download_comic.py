import sys
import os
import requests

json_url = sys.argv[1]
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
response = requests.get(json_url + '.json', headers=headers)
data = response.json()

series_title = data["readableProduct"]["series"]["title"]
product_title = data["readableProduct"]["title"]

folder_name = f"{series_title} - {product_title}"
os.makedirs(folder_name, exist_ok=True)

image_urls = []

for page in data["readableProduct"]["pageStructure"]["pages"]:
    if 'src' in page:
        image_urls.append(page['src'])

for image_url in image_urls:
    filename = os.path.basename(image_url)
    filename = os.path.splitext(filename)[0] + ".jpg"  # Set the filename with the JPG extension
    filepath = os.path.join(folder_name, filename)  # Construct the file path within the folder
    response = requests.get(image_url)
    with open(filepath, 'wb') as file:
        file.write(response.content)
        print(f"Downloaded: {filename}")

print(f"Files saved in {folder_name}")