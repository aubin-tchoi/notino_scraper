from typing import List

from notino_scraper.data_structures import ProductInfo, ProductPrice


class Product:
    def __init__(self, product_info: ProductInfo) -> None:
        """
        Instantiates a new Product with the information provided. Creates an empty list of prices of none is given.

        Args:
            product_info: The information available on the product. Usually extracted using a Scraper.
        """
        self.product_name = product_info["product_name"]
        self.description = product_info["description"]
        self.brand = product_info["brand"]
        self.prices = product_info["prices"]

    def __repr__(self) -> str:
        """
        Computes a string representation by displaying the main features and then listing the recorded prices if any.

        Returns:
            The string representation of a product.
        """
        product_text = f"Name: {self.product_name}\nBrand: {self.brand}\nDescription: {self.description}"
        if len(self.prices) == 0:
            return f"{product_text}\nNo price recorded."
        else:
            prices_text = "\n\t".join(repr(price) for price in self.prices)
            return f"{product_text}\nPrices recorded:\n\t{prices_text}"

    def __eq__(self, other):
        """
        Defines the equality check between two Products.

        Args:
            other: The Product to check with.

        Returns:
            True if the two Products refer to the same item on the website.
        """
        return (
            self.product_name.lower() == other.product_name.lower()
            and (self.description.lower() == other.description.lower())
            and (self.brand.lower() == other.brand.lower())
        )

    def __add__(self, other):
        """
        Defines the addition between two Products.

        Args:
            other: The Product to add to the current one.

        Returns:
            A Product that contains all the prices recorded.
        """
        if self != other:
            raise AssertionError(
                "Trying to add two Products that do not refer to the same item on the website."
            )
        else:
            self.prices += other.prices
            return self

    def add_prices(self, prices: List[ProductPrice]) -> None:
        """
        Adds a price to the list of prices recorded.

        Args:
            prices: The prices to add.
        """
        for price_info in prices:
            if all(
                (price_info.date, price_info.volume) != (price.date, price.volume)
                for price in self.prices
            ):
                self.prices.append(price_info)

    def get_search_name(self) -> str:
        """
        Finds the "search name" of a product, which is what you will write down in the search bar to find it.

        Returns:
            The search name of the product.
        """
        return f"{self.brand.replace('&amp;', '&')} {self.product_name.replace('&amp;', '&')}"
