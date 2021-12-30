import json
from product import Product


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
        with open(self.filename, 'w') as json_file:
            json.dump(self.products, json_file)

    def add_product(self, product_info: dict) -> None:
        """
        Adds a product to the list of product.
        :param product_info: A dictionary containing the information known on the product.
        """
        self.products.append(Product(product_info))
