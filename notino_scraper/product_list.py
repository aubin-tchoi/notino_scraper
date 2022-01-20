import json
from notino_scraper.product import Product
import traceback


class ProductList:
    filename: str
    products: list[Product]

    def __init__(self, filename: str) -> None:
        """
        Parses the json file under the name filename and dumps the data read into the 'products' attribute.
        :param filename: The path that leads to the json file to read.
        """
        self.filename = filename
        assert filename.endswith(".json")
        with open(filename) as json_file:
            products = json.load(json_file)
        self.products = [Product(product) for product in products]

    def __repr__(self) -> str:
        """
        Computes a string representation of this object by listing each product one after the other.
        :return: The string representation of a list of products.
        """
        return "\n\n".join([repr(product) for product in self.products]) +\
               f"\n\nFound prices for {len(self.products)} products."

    def get_products(self) -> list[Product]:
        """
        Getter for the product list.
        :return: The list of the products.
        """
        return self.products

    def save(self) -> None:
        """
        Saves the content back into the json file.
        """
        with open(self.filename) as json_file:
            backup = json.load(json_file)

        try:
            with open(self.filename, 'w') as json_file:
                json.dump([product.__dict__ for product in self.products], json_file)
        except:
            print(f"An issue was raised when saving the json file:\n")
            print(traceback.format_exc())
            with open(self.filename, 'w') as json_file:
                json.dump(backup, json_file)

    def add_product(self, product_info: dict, verbose: bool) -> None:
        """
        Adds a product to the list of product.
        :param product_info: A dictionary containing the information known on the product.
        :param verbose: Verbose.
        """
        new_product = Product(product_info)
        for product in self.products:
            if product == new_product:
                product += new_product
                if verbose:
                    print("Product already in the list.")
                    print(product)
                break
        # else clause if new_product has not been found in the list of products.
        else:
            self.products.append(new_product)
            if verbose:
                print(new_product)
