import datetime
from typing import Callable

from selenium import webdriver
from selenium.common.exceptions import (
    InvalidArgumentException,
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from webdriver_manager.firefox import GeckoDriverManager


class WebDriverWrapper:
    @staticmethod
    def setup_webdriver(url: str, headless: bool) -> WebDriver:
        """
        Sets up a Selenium WebDriver and opens the main page.

        Args:
            url: the base url to log on to.
            headless: whether the WebDriver will be run in headless mode or not.

        Returns:
            A Firefox (geckodriver) WebDriver logged into the provided url (default: notino.fr).
        """

        options = webdriver.FirefoxOptions()
        options.headless = headless

        web_driver = webdriver.Firefox(
            executable_path=GeckoDriverManager().install(), options=options
        )
        try:
            web_driver.get(url)
        except InvalidArgumentException:
            if url.startswith("www"):
                web_driver.get("https://" + url)
            else:
                web_driver.get("https://www." + url)

        return web_driver

    def __init__(self, url: str, headless: bool) -> None:
        """
        Sets up a geckodriver and the info list that describe the information that can be extracted on a product.
        """
        self.web_driver = self.setup_webdriver(url, headless)
        self.info_list = self.set_info_list()

    def __del__(self) -> None:
        """
        Closes the WebDriver.
        """
        self.web_driver.close()

    def set_info_list(self) -> dict:
        """
        Sets up a list of features that can be extracted from a product's page and the methods that extracts them.
        The values in the returned dict are thus methods that have to be run when logged on to the product's page.

        Returns:
            A dictionary whose keys are features and values methods that extract them.
        """

        def format_info(fetched_info: str) -> str:
            return fetched_info.replace("<!-- -->", "").replace("&nbsp;", " ").strip()

        def _single_selector_reader(css_selector: str, attribute: str) -> Callable:
            return lambda: format_info(
                self.web_driver.find_element(
                    By.CSS_SELECTOR, css_selector
                ).get_attribute(attribute)
            )

        def _read_variant_price(variant) -> str:
            try:
                return variant.find_element(
                    By.CSS_SELECTOR, "div > span"
                ).get_attribute("content")
            except NoSuchElementException:
                return "Price not found."

        def _find_prices():
            try:
                return [
                    {
                        "price": _read_variant_price(variant),
                        "volume": format_info(
                            variant.find_element(
                                By.CSS_SELECTOR, "[class~=pd-variant-label]"
                            ).get_attribute("innerHTML")
                        ),
                        "date": datetime.date.today().isoformat(),
                    }
                    for variant in self.web_driver.find_element(
                        value="pdVariantsTile"
                    ).find_elements(By.TAG_NAME, "li")
                ]
            except NoSuchElementException:
                return [
                    {
                        "price": _single_selector_reader(
                            "[id=pd-price] span", "content"
                        )(),
                        "volume": _single_selector_reader(
                            "[id=pdSelectedVariant] [class*=Name] span", "innerHTML"
                        )(),
                        "date": datetime.date.today().isoformat(),
                    }
                ]

        return {
            "product_name": _single_selector_reader(
                "div[id='pdHeader'] [class*=ProductName] span", "innerHTML"
            ),
            "description": _single_selector_reader(
                "div[id='pdHeader'] [class*=Description]", "innerHTML"
            ),
            "brand": _single_selector_reader(
                "div[id='pdHeader'] [class*=Brand]", "innerHTML"
            ),
            "prices": _find_prices,
        }
