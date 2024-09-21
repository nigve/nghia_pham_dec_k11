import os
import scrapy
from scrapy.spiders import XMLFeedSpider

class SitemapXmlSpider(XMLFeedSpider):
    name = "sitemap_xml"
    allowed_domains = ["glamira.com"]
    start_urls = ["https://www.glamira.com/sitemap.xml"]

    namespaces = [('n', 'http://www.sitemaps.org/schemas/sitemap/0.9')]
    itertag = 'n:sitemap'
    iterator = 'xml'

    def __init__(self, filter=None, *args, **kwargs):
        super(SitemapXmlSpider, self).__init__(*args, **kwargs)
        self.filter = filter
        self.dir = './glamira/data/sitemap_xml/'
        self.file_name = f'{self.dir}/{self.filter}_xmls.txt'
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

    def is_in_file(self, node_loc):
        if not os.path.exists(self.file_name):
            return False
        with open(self.file_name, 'r') as file:
            return node_loc in file.read()        

    def parse_node(self, response, node):
        node_loc = node.xpath('.//n:loc/text()').get()
        if node_loc and self.filter in node_loc:
            if not self.is_in_file(node_loc):
                with open(self.file_name, 'a') as file:
                    file.write(node_loc + '\n')