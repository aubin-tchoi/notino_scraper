from scraper import Scraper
from product_list import ProductList
from yaml import load, dump, YAMLError
import os


class NotinoScraper:
    # TODO: multiple prices per product
    # TODO: plot evolution of prices

    scraper: Scraper
    product_list: ProductList
    config: dict
    config_file: str

    def __init__(self) -> None:
        """
        Loads the config and instantiates a Scraper and a ProductList.
        """
        self.config_file = "../config.yml"
        with open(self.config_file, 'r') as stream:
            self.config = load(stream)
        self.scraper = Scraper()
        self.product_list = ProductList(self.config["datafile"])

    def update_datafile(self, new_datafile: str) -> None:
        """
        Updates the value associated with key "datafile" in the yaml config file.
        :param new_datafile:
        :return:
        """
        if not new_datafile.endswith(".json"):
            new_datafile += ".json"
        if not os.path.isfile(new_datafile):
            raise AssertionError("Invalid file path provided.")
        self.config["datafile"] = new_datafile
        with open(self.config_file, "w") as stream:
            try:
                dump(self.config, stream, default_flow_style=False, allow_unicode=True)
            except YAMLError as exc:
                print(exc)

    def take_snapshot(self) -> None:
        """
        Snapshots the prices of every product in the list.
        """
        for product in self.product_list.get_products():
            product.add_price(self.scraper.get_price(product.get_search_name()))
        self.product_list.save()

    def add_product(self, product_name: str) -> None:
        """
        Adds a product to the list of products.
        :param product_name: The name of the product to add.
        """
        self.product_list.add_product(self.scraper.get_description(product_name))

    def plot_evolution(self) -> None:
        pass
