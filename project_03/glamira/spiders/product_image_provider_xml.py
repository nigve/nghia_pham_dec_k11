import sys
import os
import psycopg2
import re
import requests
import scrapy
from scrapy.spiders import XMLFeedSpider
from minio import Minio
from io import BytesIO
from urllib.parse import urlparse

class ProductImageProviderXmlSpider(XMLFeedSpider):
    name = "product_image_provider_xml"
    allowed_domains = ["glamira.com"]
    itertag = 'n:url'
    iterator = 'xml'
    namespaces = [('n', 'http://www.sitemaps.org/schemas/sitemap/0.9'), ('image', 'http://www.google.com/schemas/sitemap-image/1.1'), ('pagemap', 'http://www.google.com/schemas/sitemap-pagemap/1.0')]

    #Generate start_urls
    def get_start_urls():
        with open('./glamira/data/sitemap_xml/product_image_provider_xmls.txt') as file:
            urls = file.read().split('\n')
            return urls
    start_urls = get_start_urls()

    #  Setup logging
    logs_file_path = './glamira/logs/product_image_provider_xml/logs.txt'
    err_logs_file_path = './glamira/logs/product_image_provider_xml/err_logs.txt'
    def ensure_log_files(self):
        logs_dir = os.path.dirname(self.logs_file_path)
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        if not os.path.exists(self.logs_file_path):
            open(self.logs_file_path, 'w').close()

        if not os.path.exists(self.err_logs_file_path):
            open(self.err_logs_file_path, 'w').close()

    # Get already crawled images 
    def get_crawled_images(self):
        self.postgres_cursor.execute("SELECT image_url FROM images_metadata")
        crawled_image_urls = [url[0] for url in self.postgres_cursor.fetchall()]

        return crawled_image_urls

    def __init__(self, *args, **kwargs):
        super(ProductImageProviderXmlSpider, self).__init__(*args, **kwargs)        

        # Minio config
        self.minio_client = Minio(
            "localhost:9000",
            access_key="accesskey",
            secret_key="secretkey",
            secure=False
        )
        self.bucket_name = "glamira-images"
        if not self.minio_client.bucket_exists(self.bucket_name):
            self.minio_client.make_bucket(self.bucket_name)

        # Postgres config
        self.postgres_conn = psycopg2.connect(
            dbname="glamira",
            user="scrapy",
            password="password",
            host="localhost"
        )
        self.postgres_cursor = self.postgres_conn.cursor()            

        self.crawled_image_urls = self.get_crawled_images()
        self.ensure_log_files()

    def generate_image_path(self, image_url):
        parsed_url = urlparse(image_url)
        path = parsed_url.path

        # Extract SKU
        sku_match = re.search(r'/sku/([^/]+)', path)
        sku = sku_match.group(1) if sku_match else None
        
        path_transformed = path.replace('/', '-')

        image_path = f'{sku}/{path_transformed}'

        return image_path

    def generate_image_metadata(self, image_url):
        parsed_url = urlparse(image_url)
        path = parsed_url.path

        # Extract SKU
        sku_match = re.search(r'/sku/([^/]+)', path)
        sku = sku_match.group(1) if sku_match else None

        # Extract view
        view_match = re.search(r'/view/([^/]+)', path)
        view = view_match.group(1) if view_match else None

        # Extract womenstone
        womenstone_match = re.search(r'/womenstone/([^/]+)', path)
        womenstone = womenstone_match.group(1) if womenstone_match else None

        # Extract diamond
        diamond_match = re.search(r'/diamond/([^/]+)', path)
        diamond = diamond_match.group(1) if diamond_match else None

        # Extract stone2
        stone2_match = re.search(r'/stone2/([^/]+)', path)
        stone2 = stone2_match.group(1) if stone2_match else None

        # Extract stone3
        stone3_match = re.search(r'/stone3/([^/]+)', path)
        stone3 = stone3_match.group(1) if stone3_match else None

        # Extract alloycolour and remove .jpg
        alloycolour_match = re.search(r'/alloycolour/([^/]+)', path)
        if alloycolour_match:
            alloycolour = alloycolour_match.group(1)
            alloycolour = re.sub(r'\.jpg$', '', alloycolour)
        else:
            alloycolour = None

        # Extract accent
        accent_match = re.search(r'/accent/([^/]+)', path)
        accent = accent_match.group(1) if accent_match else None

        # Extract wood
        wood_match = re.search(r'/wood/([^/]+)', path)
        wood = wood_match.group(1) if wood_match else None

        return {
            "image_url": image_url,
            "sku": sku,
            "view": view,
            "womenstone": womenstone,
            "diamond": diamond,
            "stone2": stone2,
            "stone3": stone3,
            "alloycolour": alloycolour,
            "accent": accent,
            "wood": wood
        }      

    def save_image_to_minio(self, response, image_path):
        try:
            self.minio_client.put_object(
                bucket_name=self.bucket_name,
                object_name=image_path,
                data=BytesIO(response.content),
                length=len(response.content),
                content_type='image/jpeg'
            )
            self.logger.info(f"Image {image_path} saved to Minio.")
            return True
        except Exception as e:
            print(f"Error saving image to minio: {e}")    
            with open(self.err_logs_file_path, 'a') as file:
                file.write(f"Error saving image to minio: {e}\n")
            return False

    def save_metadata_to_postgres(self, metadata, image_url):
        try:
            delete_statement = f"""DELETE FROM images_metadata WHERE image_url = '{image_url}'"""

            insert_query = """
            INSERT INTO images_metadata (response_url, product_url, product_name, lastmod, sku, image_url, view, womenstone, diamond, stone2, stone3, alloycolour, accent, wood, minio_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """

            self.postgres_cursor.execute(delete_statement)
            self.postgres_conn.commit()

            self.postgres_cursor.execute(insert_query, (
                metadata['response_url'], metadata['product_url'], metadata['product_name'], metadata['lastmod'],
                metadata['sku'], metadata['image_url'], metadata['view'], metadata['womenstone'],
                metadata['diamond'], metadata['stone2'], metadata['stone3'], metadata['alloycolour'],
                metadata['accent'], metadata['wood'], metadata['minio_path']
            ))
            self.postgres_conn.commit()
            print("Image metadata inserted successfully")
            return True
        except Exception as e:
            print(f"Error saving metadata: {e}")
            self.postgres_conn.rollback()
            with open(self.err_logs_file_path, 'a') as file:
                file.write(f"Error saving metadata: {e}\n")
            return False

    def rollback_metadata(self, metadata, image_url):
        try:
            delete_statement = f"""DELETE FROM images_metadata WHERE image_url = '{image_url}'"""
            self.postgres_cursor.execute(delete_statement)
            self.postgres_conn.commit()
            self.logger.info(f"Rolled back metadata for {image_url}")
        except Exception as e:
            self.logger.error(f"Error rolling back metadata for {image_url}: {e}")
            self.postgres_conn.rollback()
            with open(self.err_logs_file_path, 'a') as file:
                file.write(f"Error rolling back metadata for {image_url}: {e}\n")

    # parse_node_count=0
    def parse_node(self, response, node):
        # pass
        # self.parse_node_count += 1
        # if self.parse_node_count > 1:
        #     sys.exit(0)
        xml_response_url = response.url
        product_url = node.xpath('.//n:loc/text()').get()
        image_caption = node.xpath('.//image:caption/text()').get()
        lastmod = node.xpath('.//n:lastmod/text()').get()
        image_locs = node.xpath('.//image:loc/text()').getall()
        for image_loc in image_locs:
            image_url = image_loc
            if not image_url in self.crawled_image_urls:
                response = requests.get(image_url)
                if response.status_code == 200:
                    image_path = self.generate_image_path(image_url)
                    image_metadata = self.generate_image_metadata(image_url)
                    image_metadata['response_url'] = xml_response_url
                    image_metadata['product_url'] = product_url
                    image_metadata['product_name'] = image_caption
                    image_metadata['lastmod'] = lastmod
                    image_metadata['minio_path'] = image_path

                    try:
                        # First save_metadata_to_postgres, if success then save_image_to_minio, if both success then log
                        if self.save_metadata_to_postgres(image_metadata, image_url):
                            if self.save_image_to_minio(response, image_path):
                                with open(self.logs_file_path, 'a') as file:
                                    file.write(f"Processed {image_url} successfully.\n")
                            else:
                                # If save_image_to_minio failed then rollback_metadata
                                self.rollback_metadata(image_metadata, image_url)
                                with open(self.err_logs_file_path, 'a') as file:
                                    file.write(f"Failed to save image {image_url} to Minio. Metadata rolled back.\n")
                        else:
                            # If save_metadata_to_postgres failed then skip save_image_to_minio
                            with open(self.err_logs_file_path, 'a') as file:
                                file.write(f"Failed to save metadata for {image_url}.\n")
                    except Exception as e:
                        self.logger.error(f"Error saving image or metadata for {image_url}: {e}")
                        with open(self.err_logs_file_path, 'a') as file:
                            file.write(f"Error saving image or metadata for {image_url}: {e}\n")
                else:
                    self.logger.warning(f"Failed to download image {image_url}. Status code: {response.status_code}")
                    with open(self.err_logs_file_path, 'a') as file:
                            file.write(f"Failed to download image {image_url}. Status code: {response.status_code}\n")
            else:
                self.logger.info(f'Skipping {image_url}')