from dataclasses import dataclass
from datetime import date
from typing import List, TypedDict, Optional


@dataclass
class ProductPrice:
    price: Optional[float] = None
    volume: int = 0
    date: str = date.today().isoformat()


class ProductInfo(TypedDict):
    product_name: str
    description: str
    brand: str
    prices: List[ProductPrice]
