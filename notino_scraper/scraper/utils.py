import nltk
import re


def format_info(fetched_info: str) -> str:
    return fetched_info.replace("<!-- -->", "").replace("&nbsp;", " ").strip()


def get_volume_from_content(html_content: str) -> int:
    return int(re.sub(r"\s?ml", "", format_info(html_content).lower()))


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
    first_string, second_string = first_string.lower(), second_string.lower()
    if first_string in second_string or second_string in first_string:
        return True

    return (
        nltk.edit_distance(first_string, second_string)
        / min(len(second_string), len(first_string))
        <= threshold
    )
