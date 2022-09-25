from enum import Enum


class CssSelectors(str, Enum):
    cookie_modal = "[id='exponea-cookie-compliance'] a[class~=close]"
    search_bar = "[id='pageHeader'] input"
    right_suggestion_column = "div[id='header-suggestProductCol']"
    right_suggestion_item = "a[id='header-productWrapper']"
    left_suggestion_column = "header-suggestSectionCol"
    product_container = "data-testid='product-container'"

    def __str__(self) -> str:
        return str.__str__(self)
