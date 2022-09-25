import datetime
import traceback
from typing import Callable, Union

import nltk
from selenium import webdriver
from selenium.common.exceptions import (
    InvalidArgumentException,
    InvalidSelectorException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

from .product_not_found import ProductNotFoundException
from .selectors import CssSelectors


# TODO: define a Price TypedDict / dataclass


class Scraper:
    @staticmethod
    def setup_webdriver(url: str = "notino.fr", headless: bool = True) -> WebDriver:
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

        web_driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options)
        try:
            web_driver.get(url)
        except InvalidArgumentException:
            if url.startswith("www"):
                web_driver.get("https://" + url)
            else:
                web_driver.get("https://www." + url)

        return web_driver

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

    def __init__(self, **kwargs: Union[str, bool]) -> None:
        """
        Sets up a geckodriver and the info list that describe the information that can be extracted on a product.

        Args:
             kwargs: Options accepted: headless (bool), url (str). See setup_webdriver method for more details.
        """
        self.web_driver = self.setup_webdriver(**kwargs)
        self.info_list = self.set_info_list()

    def __del__(self) -> None:
        """
        Closes the WebDriver.
        """
        self.web_driver.close()

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

    @staticmethod
    def result_match(
        first_string: str, second_string: str, threshold: float = 0.20
    ) -> bool:
        """
        Finds out if two strings are similar enough to consider them as describing the same product.

        Args:
            first_string: The first string to compare.
            second_string: The second string to compare.
            threshold: A threshold setting the line between a return value of True or False.

        Returns:
            True if the two strings describe the same product, False otherwise.
        """
        if first_string in second_string or second_string in first_string:
            return True

        return (
            nltk.edit_distance(first_string, second_string)
            / min(len(second_string), len(first_string))
            <= threshold
        )

    def search_finalized(self, product_name: str) -> Callable:
        """
        Instantiates a method that can be used to tell if the result section has finished loading.
        Checks the result section to see if it matches the content put in the search bar.
        Meant to be used in a WebDriverWait command.

        Args:
            product_name: The content put in the search bar.

        Returns:
            A method that will return True if the result section has finished loading and False otherwise.
        """

        def _predicate(web_driver: WebDriver) -> bool:
            try:
                elements = web_driver.find_elements(
                    By.CSS_SELECTOR,
                    "div[id='header-suggestProductCol'] a[id='header-productWrapper']",
                )
                if len(elements) <= 0:
                    return False
                else:
                    return self.result_match(
                        elements[0]
                        .find_element(By.CSS_SELECTOR, "div span")
                        .get_attribute("innerHTML"),
                        product_name,
                    )
            except InvalidSelectorException as e:
                raise e
            except StaleElementReferenceException:
                return False

        return _predicate

    def deal_with_cookie_modal(self) -> None:
        try:
            self.web_driver.find_element(
                By.CSS_SELECTOR, CssSelectors.cookie_modal
            ).click()
        except NoSuchElementException:
            pass

    def find_product_url_in_right_suggestion_column(self, product_name: str) -> str:
        WebDriverWait(self.web_driver, 3).until(self.search_finalized(product_name))

        return (
            self.web_driver.find_element(
                By.CSS_SELECTOR, CssSelectors.right_suggestion_column
            )
            .find_elements(By.CSS_SELECTOR, CssSelectors.right_suggestion_item)[0]
            .get_attribute("href")
        )

    def find_product_url_in_left_suggestion_column(self, product_name: str) -> str:
        """
        Finds the first suggestion in the suggestion section if it matches the product_name.
        """
        # taking the first suggestion in the column assuming the search results are already ordered by similarity
        suggestion = self.web_driver.find_element(
            value=CssSelectors.left_suggestion_column
        ).find_elements(By.TAG_NAME, "a")[0]

        # checking if there is a 'span' element within the 'a' element
        if (
            span := suggestion.find_elements(By.TAG_NAME, "span")
        ) and self.result_match(span[0].get_attribute("innerHTML"), product_name):
            return span[0].get_attribute("href")
        elif self.result_match(suggestion.get_attribute("innerHTML"), product_name):
            return suggestion.get_attribute("href")

        raise ProductNotFoundException(product_name)

    def find_product_url_in_search_results(self, product_name: str) -> str:
        try:
            WebDriverWait(self.web_driver, 3).until(
                lambda x: x.find_element(value=CssSelectors.product_container)
            )
            return next(
                container.get_attribute("href")
                for container in self.web_driver.find_elements(
                    By.CSS_SELECTOR, CssSelectors.product_container
                )
                if self.result_match(
                    container.find_element(By.TAG_NAME, "h3").get_attribute(
                        "innerHTML"
                    ),
                    product_name,
                )
            )
        except (StopIteration, TimeoutException):
            raise ProductNotFoundException(product_name)

    def navigate_to_product_page(self, product_name: str) -> None:
        search_bar = self.web_driver.find_element(
            By.CSS_SELECTOR, CssSelectors.search_bar
        )
        search_bar.send_keys(product_name)

        try:
            self.web_driver.get(
                self.find_product_url_in_right_suggestion_column(product_name)
            )

        except TimeoutException:
            try:
                self.web_driver.get(
                    self.find_product_url_in_left_suggestion_column(product_name)
                )
            # catching NoSuchElementException in case the left suggestion column is missing
            except (TimeoutException, ProductNotFoundException, NoSuchElementException):
                # pressing enter to display the search results
                search_bar.send_keys(Keys.ENTER)
                self.web_driver.get(
                    self.find_product_url_in_search_results(product_name)
                )

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
