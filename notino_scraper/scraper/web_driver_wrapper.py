from selenium import webdriver
from selenium.common.exceptions import (
    InvalidArgumentException,
)
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

    def __del__(self) -> None:
        """
        Closes the WebDriver.
        """
        self.web_driver.close()
