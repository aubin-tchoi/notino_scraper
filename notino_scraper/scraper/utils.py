from typing import Callable

import nltk
from selenium.common.exceptions import (
    InvalidSelectorException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver



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
