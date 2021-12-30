from scraper import Scraper
from product_list import ProductList


class NotinoScraper:
    scraper: Scraper
    product_list: ProductList
    datafile: str

    def __init__(self) -> None:
        self.scraper = Scraper()
        self.datafile = ""
        self.product_list = ProductList(self.datafile)

    def update_datafile(self, new_datafile: str) -> None:
        self.datafile = new_datafile

    def take_snapshot(self) -> None:
        for product in self.product_list.get_products():
            product.add_price(self.scraper.get_price(product.get_search_name()))
        self.product_list.save()

    def add_product(self, product_name: str) -> None:
        self.product_list.add_product(self.scraper.get_description(product_name))
