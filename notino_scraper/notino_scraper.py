from notino_scraper.scraper import Scraper
from notino_scraper.product_list import ProductList
from yaml import safe_load, dump, YAMLError
import os


class NotinoScraper:
    # TODO: multiple prices per product
    # TODO: plot evolution of prices
    # TODO: articles indisponibles
    # TODO: remove product
    # TODO: verbose

    scraper: Scraper
    product_list: ProductList
    config_file: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "config.yml")
    verbose: bool

    def __init__(self, verbose: bool = True) -> None:
        """
        Loads the config and instantiates a Scraper and a ProductList.
        """
        self.verbose = verbose
        with open(self.config_file, 'r') as stream:
            config = safe_load(stream)
        self.scraper = Scraper()
        while True:
            try:
                self.product_list = ProductList(config["datafile"])
                break
            except (IOError, AssertionError):
                self.update_datafile(input("Please specify the path to the output json file: "))

    @staticmethod
    def update_datafile(new_datafile: str) -> None:
        """
        Updates the value associated with key "datafile" in the yaml config file.
        :param new_datafile:
        :return:
        """
        if not new_datafile.endswith(".json"):
            new_datafile += ".json"
        if not os.path.isfile(new_datafile):
            raise AssertionError("Invalid file path provided.")

        with open(NotinoScraper.config_file, 'r') as stream:
            config = safe_load(stream)

        config["datafile"] = new_datafile

        with open(NotinoScraper.config_file, "w") as stream:
            try:
                dump(config, stream, default_flow_style=False, allow_unicode=True)
            except YAMLError as exc:
                print(exc)

    def take_snapshot(self) -> None:
        """
        Snapshots the prices of every product in the list.
        """
        for product in self.product_list.get_products():
            product.add_price(self.scraper.get_price(product.get_search_name()))
        self.product_list.save()
        if self.verbose:
            print(self.product_list)

    def add_product(self, product_name: str) -> None:
        """
        Adds a product to the list of products.
        :param product_name: The name of the product to add.
        """
        self.product_list.add_product(self.scraper.get_description(product_name), self.verbose)
        self.product_list.save()

    def plot_evolution(self) -> None:
        pass
