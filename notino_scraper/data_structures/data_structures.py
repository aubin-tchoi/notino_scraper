from dataclasses import dataclass
from datetime import date
from typing import List, TypedDict, Optional


@dataclass
class ProductPrice:
    price: Optional[float] = None
    """
    Price of the product.
    It is null if either the product is not available for a specific volume or it is not available at all.
    """
    volume: int = 0
    """
    Volume of the product in mL.
    It is equal to 0 iff the product is not available at all.
    """
    date: str = date.today().isoformat()
    """
    Date of the snapshot in format YYYY-MM-DD.
    """


class ProductInfo(TypedDict):
    product_name: str
    description: str
    brand: str
    prices: List[ProductPrice]
