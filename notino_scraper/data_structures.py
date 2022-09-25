from dataclasses import dataclass
from datetime import date
from typing import List, TypedDict


class ProductInfo(TypedDict):
    product_name: str
    description: str
    brand: str
    prices: List[float]


@dataclass
class ProductPrice:
    price: float
    volume: int
    date: date
