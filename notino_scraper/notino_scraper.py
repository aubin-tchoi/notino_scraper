from scraper import Scraper
from product_list import ProductList

if __name__ == '__main__':
    filename = ""
    scraper = Scraper()
    parser = ProductList(filename)
    print(scraper.get_description("Rochas Moustache"))
