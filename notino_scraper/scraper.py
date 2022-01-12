from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from selenium.common.exceptions import InvalidArgumentException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import InvalidSelectorException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

from typing import Callable
import datetime
import nltk
import traceback


class Scraper:
    web_driver: WebDriver
    info_list: dict

    @staticmethod
    def setup_webdriver(**kwargs) -> WebDriver:
        """
        Sets up a Selenium WebDriver.
        Supports the following parameters:
        - url: the base url to log on to.
        - headless: whether the WebDriver will be run in headless mode or not.
        :param kwargs: A dictionary containing the parameters listed above.
        :return: A Firefox (geckodriver) WebDriver logged into the provided url (default: notino.fr).
        """
        url = kwargs["url"] if "url" in kwargs else "notino.fr"
        headless = kwargs["headless"] if "headless" in kwargs else True

        options = webdriver.FirefoxOptions()
        options.headless = headless

        web_driver = webdriver.Firefox(options=options)
        try:
            web_driver.get(url)
        except InvalidArgumentException:
            if url.startswith('www'):
                web_driver.get('https://' + url)
            else:
                web_driver.get('https://www.' + url)

        return web_driver

    def set_info_list(self) -> dict:
        """
        Sets up a list of features that can be extracted from a product's page and the methods that extracts them.
        The values in the returned dict are thus methods that have to be run when logged on to the product's page.
        :return: A dictionary whose keys are features and values methods that extract them.
        """

        def format_info(fetched_info: str) -> str:
            return fetched_info.replace("<!-- -->", "").replace("&nbsp;", " ").strip()

        def _single_selector_reader(css_selector: str, attribute: str) -> Callable:
            return lambda: format_info(
                self.web_driver.find_element(By.CSS_SELECTOR, css_selector).get_attribute(attribute))

        def _find_prices():
            try:
                return [{
                    "price": variant.find_element(By.CSS_SELECTOR, "div > span").get_attribute("content"),
                    "volume": format_info(variant.find_element(
                        By.CSS_SELECTOR, "[class~=pd-variant-label]").get_attribute("innerHTML"))
                } for variant in
                    self.web_driver.find_element(value="pdVariantsTile").find_elements(By.TAG_NAME, "li")]
            except NoSuchElementException:
                return [{"price": _single_selector_reader("[id=pd-price] span", "content")(),
                         "volume": _single_selector_reader("[id=pdSelectedVariant] [class*=Name] span", "innerHTML")()}]

        return {
            "product_name": _single_selector_reader("div[id='pdHeader'] [class*=ProductName] span", "innerHTML"),
            "description": _single_selector_reader("div[id='pdHeader'] [class*=Description]", "innerHTML"),
            "brand": _single_selector_reader("div[id='pdHeader'] [class*=Brand]", "innerHTML"),
            "prices": _find_prices
        }

    def __init__(self, **kwargs) -> None:
        """
        Sets up a geckodriver and the info list that describe the information that can be extracted on a product.
        :param kwargs: Options accepted: headless (bool), url (str). See setup_webdriver method for more details.
        """
        self.web_driver = self.setup_webdriver(**kwargs)
        self.info_list = self.set_info_list()

    def __del__(self):
        """
        Closes the WebDriver.
        :return:
        """
        self.web_driver.close()

    def is_product_available(self) -> bool:
        """
        Checks if the product found on the current page is available.
        :return: True if the product is available, False otherwise.
        """
        unavailable_message = "Cet article n'est pas disponible actuellement"

        return len(self.web_driver.find_elements(
            By.CSS_SELECTOR, f"div[id=pdSelectedVariant] + div > span[innerHTML*='{unavailable_message}']")) == 0

    @staticmethod
    def result_match(first_string: str, second_string: str, threshold: float = 0.20) -> bool:
        """
        Finds out if two strings are similar enough to consider them as describing the same product.
        :param first_string: The first string to compare.
        :param second_string: The second string to compare.
        :param threshold: A threshold setting the line between a return value of True or False.
        :return: True if the two strings describe the same product, False otherwise.
        """
        if first_string in second_string or second_string in first_string:
            return True

        return nltk.edit_distance(first_string, second_string) / min(len(second_string), len(first_string)) <= threshold

    def search_finalized(self, product_name: str) -> Callable:
        """
        Instantiates a method that can be used to tell if the result section has finished loading.
        Checks the result section to see if it matches the content put in the search bar.
        Meant to be used in a WebDriverWait command.
        :param product_name: The content put in the search bar.
        :return: A method that will return True if the result section has finished loading and False otherwise.
        """

        def _predicate(web_driver: WebDriver):
            try:
                elements = web_driver.find_elements(By.CSS_SELECTOR,
                                                    "div[id='header-suggestProductCol'] a[id='header-productWrapper']")
                if len(elements) <= 0:
                    return False
                else:
                    return self.result_match(elements[0]
                                             .find_element(By.CSS_SELECTOR, "div span")
                                             .get_attribute("innerHTML"),
                                             product_name)
            except InvalidSelectorException as e:
                raise e
            except StaleElementReferenceException:
                return False

        return _predicate

    def fetch_product_info(self, product_name: str, *features: str) -> dict:
        """
        Extracts a list of information on a product.
        :param product_name: The name of the product to put in the search bar.
        :param features: The features to extract. By default, all of them will be extracted.
        :return: A dictionary containing the extracted information.
        """
        searchBar = self.web_driver.find_element(By.CSS_SELECTOR, "div[id='pageHeader'] input")
        searchBar.send_keys(product_name)

        try:
            WebDriverWait(self.web_driver, 3).until(self.search_finalized(product_name))
            self.web_driver.get(self.web_driver.find_element(By.CSS_SELECTOR, "div[id='header-suggestProductCol']")
                                .find_elements(By.CSS_SELECTOR, "a[id='header-productWrapper']")[0]
                                .get_attribute("href"))
        except TimeoutException:
            self.web_driver.get(self.web_driver.find_element(value="header-suggestSectionCol")
                                .find_elements(By.TAG_NAME, "a")[0]
                                .get_attribute("href"))
            self.web_driver.get(self.web_driver.find_element(value="productsList")
                                .find_element(By.TAG_NAME, "a")
                                .get_attribute("href"))

        feature_readers, fetched_info = self.set_info_list(), {}

        for feature in features if len(features) > 0 else feature_readers.keys():
            try:
                fetched_info[feature] = feature_readers[feature]()
            except NoSuchElementException:
                print(f"Issue raised when retrieving the {feature} on the product {product_name}:\n")
                print(traceback.format_exc())
                if feature == "prices":
                    if not self.is_product_available():
                        fetched_info[feature] = [{"price": "Product not available."}]
                else:
                    fetched_info[feature] = "Info not found."

        return fetched_info

    def get_description(self, product_name: str) -> dict:
        """
        Finds the following information on a product: name, description and brand name.
        :param product_name: The name of the product to look into.
        :return: A dictionary containing the information mentioned above.
        """
        return self.fetch_product_info(product_name, "product_name", "description", "brand")

    def get_prices(self, product_name: str) -> list:
        """
        Finds the following information on a product: price as of the date the script is run, volume and current date.
        :param product_name: The name of the product to look into.
        :return: A dictionary containing the information mentioned above.
        """
        product_info = self.fetch_product_info(product_name, "prices")

        for price in product_info["prices"]:
            price.update({"date": datetime.date.today().isoformat()})
        return product_info["prices"]
