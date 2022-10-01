import datetime
import traceback
from typing import Optional, List

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from notino_scraper.data_structures import (
    ProductInfo,
    ProductPrice,
    ProductPriceNotFoundException,
)
from .navigation_handler import NavigationHandler
from .utils import format_info, get_volume_from_content


class Scraper(NavigationHandler):
    def __init__(self, url: str = "notino.fr", headless: bool = True):
        super().__init__(url, headless)

    def _single_selector_reader(self, css_selector: str, attribute: str) -> str:
        try:
            return format_info(
                self.web_driver.find_element(
                    By.CSS_SELECTOR, css_selector
                ).get_attribute(attribute)
            )
        except NoSuchElementException:

            return "Info not found"

    def _get_variants(self) -> List[WebElement]:
        return self.web_driver.find_element(value="pdVariantsTile").find_elements(
            By.TAG_NAME, "li"
        )

    @staticmethod
    def _read_variant_price(variant: WebElement) -> Optional[float]:
        try:
            return float(
                variant.find_element(By.CSS_SELECTOR, "div > span")
                .get_attribute("content")
                .replace(",", ".")
            )
        except NoSuchElementException:
            print(traceback.format_exc())
            return None

    @staticmethod
    def _get_variant_volume(variant: WebElement) -> int:
        return get_volume_from_content(
            variant.find_element(
                By.CSS_SELECTOR, "[class~=pd-variant-label]"
            ).get_attribute("innerHTML")
        )

    def _get_selected_variant_info(self) -> ProductPrice:
        return ProductPrice(
            price=float(
                self._single_selector_reader("[id=pd-price] span", "content").replace(
                    ",", "."
                )
            ),
            volume=get_volume_from_content(
                self._single_selector_reader(
                    "[id=pdSelectedVariant] [class*=Name] span", "innerHTML"
                )
            ),
            date=datetime.date.today().isoformat(),
        )

    def _is_product_available(self) -> bool:
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
                By.CSS_SELECTOR, "[id='exponea-cookie-compliance'] a[class~=close]"
            ).click()
        except NoSuchElementException:
            pass

    def _find_prices(self) -> List[ProductPrice]:
        try:
            return [
                ProductPrice(
                    price=self._read_variant_price(variant),
                    volume=self._get_variant_volume(variant),
                )
                for variant in self._get_variants()
            ]
        except NoSuchElementException:
            try:
                return [self._get_selected_variant_info()]
            except NoSuchElementException:
                print(traceback.format_exc())
                if not self._is_product_available():
                    return [ProductPrice()]
                else:
                    raise ProductPriceNotFoundException

    def fetch_product_info(
        self, product_name: str, get_prices: bool = True
    ) -> ProductInfo:
        """
        Extracts a list of information on a product.

        Args:
            product_name: The name of the product to put in the search bar.
            get_prices: Whether the prices should be retrieved or not.

        Returns:
            A dictionary containing the extracted information.
        """
        self.deal_with_cookie_modal()
        self.navigate_to_product_page(product_name)

        return ProductInfo(
            product_name=self._single_selector_reader(
                "div[id='pdHeader'] h1 span span", "innerHTML"
            ),
            description=self._single_selector_reader(
                "div[id='pdHeader'] h1 span + span", "innerHTML"
            ),
            brand=self._single_selector_reader(
                "div[id='pdHeader'] h1 a", "innerHTML"
            ),
            prices=self._find_prices() if get_prices else [],
        )

    def get_description(self, product_name: str) -> ProductInfo:
        """
        Finds the following information on a product: name, description and brand name.

        Args:
            product_name: The name of the product to look into.

        Returns:
            A dictionary containing the information mentioned above.
        """
        return self.fetch_product_info(product_name, False)

    def get_prices(self, product_name: str) -> List[ProductPrice]:
        """
        Finds the following information on a product: price as of the date the script is run, volume and current date.

        Args:
            product_name: The name of the product to look into.

        Returns:
            A dictionary containing the information mentioned above.
        """
        self.deal_with_cookie_modal()
        self.navigate_to_product_page(product_name)

        return self._find_prices()
