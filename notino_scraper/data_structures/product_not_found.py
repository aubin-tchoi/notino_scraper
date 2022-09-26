class ProductNotFoundException(Exception):
    def __init__(self, product: str, message: str = "Product not found.") -> None:
        self.product = product
        self.message = message
        super().__init__(self.message)
