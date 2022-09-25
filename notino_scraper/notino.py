import datetime
import os
from collections import defaultdict
from typing import DefaultDict, List, Tuple

import matplotlib.pyplot as plt
import seaborn as sns
from yaml import safe_load, dump, YAMLError

from .product import Product
from .product_list import ProductList
from .product_not_found import ProductNotFoundException
from .scraper import Scraper


class NotinoScraper:
    config_file: str = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "..", "config.yml"
    )

    def __init__(self, verbose: bool = True, debug: bool = False) -> None:
        """
        Loads the config and instantiates a Scraper and a ProductList.

        Args:
            verbose: The level of verbose to use. True means more messages printed.
        """
        self.verbose = verbose
        self.scraper = Scraper(headless=not debug)
        while True:
            try:
                with open(self.config_file, "r") as stream:
                    config = safe_load(stream)
                self.product_list = ProductList(config["datafile"])
                break
            except (IOError, AssertionError):
                print("An error occurred when opening the json file.")
                self.update_datafile(
                    input("Please specify the path to the output json file: ")
                )

    @staticmethod
    def update_config(key: str, new_value: str) -> None:
        """
        Updates the value associated with the provided key in the yaml config file.

        Args:
            key: The key to update.
            new_value: The value to update with.
        """
        with open(NotinoScraper.config_file, "r") as stream:
            config = safe_load(stream)

        config[key] = new_value

        with open(NotinoScraper.config_file, "w") as stream:
            try:
                dump(config, stream, default_flow_style=False, allow_unicode=True)
            except YAMLError as exc:
                print(exc)

    @staticmethod
    def update_datafile(new_datafile: str) -> None:
        """
        Updates the value associated with key "datafile" in the yaml config file.

        Args:
            new_datafile: The value to replace with.
        """
        if not new_datafile.endswith(".json"):
            new_datafile += ".json"
        assert os.path.isfile(new_datafile), "Invalid file path provided."

        NotinoScraper.update_config("datafile", new_datafile)

    @staticmethod
    def update_img_folder(new_folder: str) -> None:
        """
        Updates the value associated with key "img_folder" in the yaml config file.

        Args:
            new_folder: The value to replace with.
        """
        assert os.path.isdir(new_folder), "Invalid folder path provided."

        NotinoScraper.update_config("img_folder", new_folder)

    @staticmethod
    def set_config_parameters() -> None:
        """
        Sets every existing parameter in the configuration by asking for user input on each of them.
        Also validates the input and asks for it again if an incorrect value is passed.
        """
        enter = "(press ENTER to leave it as it is): "
        config_parameters = {
            "datafile": (
                f"Please specify the path to the output json file {enter}",
                NotinoScraper.update_datafile,
            ),
            "img_folder": (
                f"Please specify the folder in which the images will be stored {enter}",
                NotinoScraper.update_img_folder,
            ),
        }
        for parameter in config_parameters:
            # Asking for user input again and again until a correct value is provided or the default value is kept.
            while True:
                user_input = input(config_parameters[parameter][0])
                try:
                    if user_input != "":
                        config_parameters[parameter][1](user_input)
                    break
                except AssertionError:
                    print("Invalid input, please try again.")
        print("You're all set, thank you.")

    def take_snapshot(self) -> None:
        """
        Snapshots the prices of every product in the list.
        """
        for product in self.product_list.get_products():
            if self.verbose:
                print(f"Adding the price of: {product.get_search_name()}")
            try:
                product.add_prices(self.scraper.get_prices(product.get_search_name()))
            except ProductNotFoundException:
                if self.verbose:
                    print(f"Prices not found for: {product.get_search_name()}")
        self.product_list.save()
        if self.verbose:
            print(self.product_list)

    def add_product(self, product_name: str) -> None:
        """
        Adds a product to the list of products.

        Args:
            product_name: The name of the product to add.
        """
        if self.verbose:
            print(f"\nLooking for: {product_name}")
        if product_name != "":
            self.product_list.add_product(
                self.scraper.get_description(product_name), self.verbose
            )
            self.product_list.save()

    def plot_evolution(self) -> None:
        """
        Plots the evolution of the prices of each product and stores the plots in the image folder.
        """
        while True:
            try:
                with open(self.config_file, "r") as stream:
                    config = safe_load(stream)
                img_folder = config["img_folder"]
                break
            except KeyError as e:
                if e.args[0] == "img_folder":
                    self.update_img_folder(
                        input(
                            "Please specify the folder in which the images will be stored: "
                        )
                    )

        sns.set(color_codes=True)

        y_min, y_max = (
            min(
                float(price["price"].replace(",", "."))
                for product in self.product_list.products
                for price in product.prices
                if (
                    price != "Info not found."
                    and price["price"] != "Product not available."
                    and price["price"] != "Price not found."
                )
            ),
            max(
                float(price["price"].replace(",", "."))
                for product in self.product_list.products
                for price in product.prices
                if (
                    price != "Info not found."
                    and price["price"] != "Product not available."
                    and price["price"] != "Price not found."
                )
            ),
        )
        for product in self.product_list.products:
            # There can be different sizes for the same product.
            plots: DefaultDict[
                str, DefaultDict[str, List[Tuple[datetime.date, float]]]
            ] = defaultdict(lambda: defaultdict(list))
            for price in product.prices:
                if (
                    price != "Info not found."
                    and price["price"] != "Product not available."
                    and price["price"] != "Price not found."
                ):
                    plots[f"{product.get_search_name()}"][f"{price['volume']}"].append(
                        (
                            datetime.date.fromisoformat(price["date"]),
                            float(price["price"].replace(",", ".")),
                        )
                    )
            for product_name in plots:
                # Removing the products that have too few prices recorded.
                if sum(len(p) for p in plots[product_name].values()) > 10:
                    plt.figure(clear=True, figsize=(14, 14))
                    for volume in plots[product_name]:
                        plt.plot(
                            [t[0] for t in plots[product_name][volume]],
                            [t[1] for t in plots[product_name][volume]],
                            label=f"{product_name} {volume}",
                        )
                    plt.legend()
                    plt.xlabel("Temps")
                    plt.ylabel("Prix (€)")
                    plt.ylim((y_min, y_max))
                    plt.savefig(
                        os.path.join(img_folder, f"price_evolution_{product_name}")
                    )
                    plt.close()

    def get_price(self, search_name: str) -> None:
        """
        Prints the current price of a product.
        Mostly useful for debugging purposes when used without headless mode.

        Args:
            search_name: The name of the product to search for.
        """
        print(Product(self.scraper.fetch_product_info(search_name)))
