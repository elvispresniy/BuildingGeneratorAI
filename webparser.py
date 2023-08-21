import os
import zipfile
import shutil

import requests
from bs4 import BeautifulSoup

root_url = r"https://www.planetminecraft.com"
original_url = r"https://www.planetminecraft.com/projects/tag/bundle/?order=order_popularity&share=schematic&p="

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.81'
}

def get_urls(url: str, __s: int, __e: int) -> list[str]:
    urls = list()
    for p in range(__s, __e + 1):
        urls.append(f'{url}{p}')
    return urls

def get_response(url: str, headers: dict = headers):
    '''Gets response object from page №?'''
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(f'Successfully connected to page №{url.split("=")[-1]} 🐠')
    else:
        print("Failed to fetch the page.")
    return response

def get_map_links(response) -> list[str]:
    '''Gets list of all useful links on page №X'''
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all r-title elements
    elements = soup.find_all("a", class_="r-title")

    # Find all links to download pages
    download_links = [element.get("href") for element in elements]
    return download_links

def  get_map_response(map_link: str, headers: dict = headers):
    '''Gets response from a map page'''
    url = root_url + map_link

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(f'Successfully connected to: {map_link}')
    else:
        print('Failed to fetch the page.')
    return response

def get_download_link(response) -> str:
    '''Gets wonload link from a map's page'''
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the script tag
    script_tag = soup.find_all('script', type='text/javascript')[-2]

    # Extract the URL from the script tag using string manipulation
    url_start = script_tag.text.find('schematic: "')
    url_end = script_tag.text.find('",', url_start)
    url = script_tag.text[url_start + len('schematic: "'):url_end]

    # Delete useless parts
    download_url = url.replace("s3.amazonaws.com/", "").split('?')[0]

    return download_url

def installation(url: str, save_path=None, headers: dict = headers):
    '''Installs a file from a download link'''
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Check the 'Content-Type' header to determine the file extension
        content_type = response.headers.get('Content-Type')

        # Get extension
        if content_type == 'application/octet-stream':
            file_extension = '.schematic'
        elif content_type == 'application/zip':
            file_extension = '.zip'
        else:
            print('Failed to install ❌')
            print(f'Unknown content type: {content_type}')
            return None
        
        # Install a file
        filename = url.split('.')[-2].split('/')[-1] + file_extension

        # Combine the save path and filename to create the full save path
        full_save_path = os.path.join(save_path, filename) if save_path else filename

        with open(full_save_path, 'wb') as file:
            file.write(response.content)

        print(f'Successfully installed ✅:\n{full_save_path}')
        return full_save_path
    else:
        print('Failed to install ❌')
    return None

def unpack_zip(zip_file_path: str, extract_to: str) -> None:
    '''Unpacks a zip and deletes it'''
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    # Delete original zip
    os.remove(zip_file_path)

def find_schematic_files(path: str) -> list[str]:
    '''Finds all .schematic files in a given directory'''
    schematic_files = []
    
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.schematic'):
                schematic_files.append(os.path.join(root, file))
    
    return schematic_files

def wipe_folders(path: str):
    '''Moves all .schematic files into a given `path`. Then removes all nested folders'''
    paths = os.listdir(path)

    # Loop through items in the `path`
    for item in paths:
        item_path = os.path.join(path, item)

        if os.path.isdir(item_path):
            # Loop through .schematic files in a nested folder
            for schematic_path in find_schematic_files(item_path):
                # Move .schematic to the `path`
                try:
                    shutil.move(schematic_path, path)
                    print(f'Moved: {schematic_path}')
                except shutil.Error as e:
                    print(e)

            # Remove a nested folder
            shutil.rmtree(item_path)
        # If a item is nor folder not .schematic, remove it
        elif not item_path.endswith('.schematic'):
            os.remove(item_path)