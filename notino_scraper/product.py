class Product:
    product_name: str
    description: str
    brand: str
    prices: list[dict]

    def __init__(self, product_info: dict) -> None:
        """
        Instantiates a new Product with the information provided. Creates an empty list of prices of none is given.
        :param product_info: The information available on the product. Usually extracted using a Scraper.
        """
        self.product_name = product_info["product_name"]
        self.description = product_info["description"]
        self.brand = product_info["brand"]
        if "prices" in product_info:
            self.prices = product_info["prices"]
        else:
            self.prices = []

    def add_price(self, price_info: dict) -> None:
        """
        Adds a price to the list of prices recorded.
        :param price_info: A dictionary containing the following information: price, volume and current date.
        """
        self.prices.append(price_info)

    def get_search_name(self) -> str:
        """
        Finds the "search name" of a product, which is what you will write down in the search bar to find it.
        :return: The search name of the product.
        """
        return f"{self.brand} {self.product_name}"
