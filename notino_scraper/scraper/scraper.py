import datetime
import traceback

from selenium.common.exceptions import (
    NoSuchElementException,
)
from selenium.webdriver.common.by import By

from .navigation_handler import NavigationHandler
from .selectors import CssSelectors


class Scraper(NavigationHandler):
    def __init__(self, url: str = "notino.fr", headless: bool = True):
        super().__init__(url, headless)

    def is_product_available(self) -> bool:
        """
        Checks if the product found on the current page is available.

        Returns:
            True if the product is available, False otherwise.
        """
        unavailable_message = "This product is not available at the moment."
        unavailable_spans = self.web_driver.find_elements(
            By.CSS_SELECTOR, f"div[id=pdSelectedVariant] + div > span"
        )
        return not (
            len(unavailable_spans) > 0
            and unavailable_spans[0].get_attribute("innerHTML") == unavailable_message
        )

    def deal_with_cookie_modal(self) -> None:
        try:
            self.web_driver.find_element(
                By.CSS_SELECTOR, CssSelectors.cookie_modal
            ).click()
        except NoSuchElementException:
            pass

    def fetch_product_info(self, product_name: str, *features: str) -> dict:
        """
        Extracts a list of information on a product.

        Args:
            product_name: The name of the product to put in the search bar.
            features: The features to extract. By default, all of them will be extracted.

        Returns:
            A dictionary containing the extracted information.
        """
        self.deal_with_cookie_modal()
        self.navigate_to_product_page(product_name)

        feature_readers, fetched_info = self.set_info_list(), {}

        for feature in features if len(features) > 0 else feature_readers.keys():
            try:
                fetched_info[feature] = feature_readers[feature]()
            except NoSuchElementException:
                print(
                    f"Issue raised when retrieving the {feature} on the product {product_name}:\n"
                )
                print(traceback.format_exc())
                if feature == "prices":
                    if not self.is_product_available():
                        fetched_info[feature] = [
                            {
                                "price": "Product not available.",
                                "date": datetime.date.today().isoformat(),
                            }
                        ]
                    else:
                        fetched_info[feature] = [
                            {
                                "price": "Price not found.",
                                "date": datetime.date.today().isoformat(),
                            }
                        ]
                else:
                    fetched_info[feature] = "Info not found."

        return fetched_info

    def get_description(self, product_name: str) -> dict:
        """
        Finds the following information on a product: name, description and brand name.

        Args:
            product_name: The name of the product to look into.

        Returns:
            A dictionary containing the information mentioned above.
        """
        return self.fetch_product_info(
            product_name, "product_name", "description", "brand"
        )

    def get_prices(self, product_name: str) -> list:
        """
        Finds the following information on a product: price as of the date the script is run, volume and current date.

        Args:
            product_name: The name of the product to look into.

        Returns:
            A dictionary containing the information mentioned above.
        """
        return self.fetch_product_info(product_name, "prices")["prices"]
