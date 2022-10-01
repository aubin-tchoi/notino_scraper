from typing import Callable

from selenium.common.exceptions import (
    InvalidSelectorException,
    StaleElementReferenceException,
    InvalidArgumentException,
)
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from notino_scraper.data_structures.product_not_found import ProductNotFoundException
from .utils import result_match
from .web_driver_wrapper import WebDriverWrapper


class NavigationHandler(WebDriverWrapper):
    def __init__(self, url: str, headless: bool):
        super().__init__(url, headless)

    @staticmethod
    def search_finalized(product_name: str) -> Callable[[WebDriver], bool]:
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
                    return result_match(
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

    def find_product_url_in_right_suggestion_column(self, product_name: str) -> str:
        WebDriverWait(self.web_driver, 3).until(self.search_finalized(product_name))

        return (
            self.web_driver.find_element(
                By.CSS_SELECTOR, "div[id='header-suggestProductCol']"
            )
            .find_elements(By.CSS_SELECTOR, "a[id='header-productWrapper']")[0]
            .get_attribute("href")
        )

    def find_product_url_in_left_suggestion_column(self, product_name: str) -> str:
        """
        Finds the first suggestion in the suggestion section if it matches the product_name.
        """
        # taking the first suggestion in the column assuming the search results are already ordered by similarity
        suggestion = self.web_driver.find_element(
            value="header-suggestSectionCol"
        ).find_elements(By.TAG_NAME, "a")[0]

        # checking if there is a 'span' element within the 'a' element
        if (span := suggestion.find_elements(By.TAG_NAME, "span")) and result_match(
            span[0].get_attribute("innerHTML"), product_name
        ):
            return span[0].get_attribute("href")
        elif result_match(suggestion.get_attribute("innerHTML"), product_name):
            return suggestion.get_attribute("href")

        raise ProductNotFoundException(product_name)

    def find_product_url_in_search_results(self, product_name: str) -> str:
        try:
            WebDriverWait(self.web_driver, 3).until(
                lambda x: x.find_element(
                    By.CSS_SELECTOR, "[data-testid='product-container']"
                )
            )
            return next(
                container.get_attribute("href")
                for container in self.web_driver.find_elements(
                    By.CSS_SELECTOR, "[data-testid='product-container']"
                )
                if result_match(
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
            By.CSS_SELECTOR, "[id='pageHeader'] input"
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
            except (
                TimeoutException,
                ProductNotFoundException,
                NoSuchElementException,
                InvalidArgumentException,
            ):
                # pressing enter to display the search results
                search_bar.send_keys(Keys.ENTER)
                self.web_driver.get(
                    self.find_product_url_in_search_results(product_name)
                )
