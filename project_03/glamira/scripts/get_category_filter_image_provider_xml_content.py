import os
import requests

def main():
    with open('../data/sitemap_xml/category_filter_image_provider_xmls.txt') as file:
        content = file.read()
        urls = content.split('\n')
        for url in urls:
            if url:
                file_name = url.split('/')[-1]
                output = f'../data/category_filter_image_provider_xml/{file_name}'
                
                os.makedirs(os.path.dirname(output), exist_ok=True)
                
                response = requests.get(url)
                if response.status_code == 200:
                    with open(output, 'wb') as f:
                        f.write(response.content)
                    print(f'Wrote {url} to {output}')
                else:
                    print(f'Failed to write {url}, status code: {response.status_code}')

if __name__ == "__main__":
    main()