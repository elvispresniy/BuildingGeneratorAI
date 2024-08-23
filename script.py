import webparser

original_url = r"https://www.planetminecraft.com/projects/tag/bundle/?order=order_popularity&share=schematic&p="
save_path = r'C:\Users\rualz\Desktop\Dekstop\Code\ai_roadmap\voxel_mesh\neg'

start = int(input('Input start page: '))
end = int(input('Input end page: '))

urls = webparser.get_urls(original_url, start, end)

for url in urls:
    # Get response from a page
    response = webparser.get_response(url)

    if not response.status_code == 200:
        continue

    # Get all links from a page
    links = webparser.get_map_links(response)

    # Iterate through links
    for link in links:
        flag = bool(input(f'{link}\nContinue?'))
        if not flag:
            continue

        # Get response from a map
        map_response = webparser.get_map_response(link)

        if not map_response.status_code == 200:
            continue

        # Get download link
        download_link = webparser.get_download_link(map_response)

        # Download and get a filepath
        filepath = webparser.installation(download_link, save_path)

        if filepath is not None:
            if '.zip' in filepath:
                # Unpack if .zip
                webparser.unpack_zip(filepath, save_path)

webparser.wipe_folders(save_path)
