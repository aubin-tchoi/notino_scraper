import argparse
import sys

from notino_scraper import NotinoScraper


def parse_args() -> argparse.Namespace:
    """
    Parses the CLI arguments passed to the main using argparse.

    :return: The Namespace that stores the arguments passed.
    """
    parser = argparse.ArgumentParser(
        description="Main entry point for the NotinoScraper API."
    )

    parser.add_argument("--verbose", action="store_false", help="Verbose.")
    parser.add_argument(
        "--config", action="store_true", help="Sets the config in command line."
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="Change the path of the json file synchronized.",
    )
    parser.add_argument("--print", action="store_true", help="Print the product list.")
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Snapshot the prices of the products recorded.",
    )
    parser.add_argument(
        "--plot", action="store_true", help="Plot the evolution of the prices."
    )
    parser.add_argument(
        "--add_products",
        type=str,
        default="",
        help="Semicolon-separated names of the products to add.",
    )
    parser.add_argument(
        "--get_prices",
        type=str,
        default="",
        help="Semicolon-separated names of the products to get the prices of.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    argv = sys.argv[1:]
    args = parse_args()

    if args.output != "":
        NotinoScraper.update_datafile(args.output)
        exit()
    if args.config:
        NotinoScraper.set_config_parameters()
        exit()

    # This instantiation takes some time.
    notino_scraper = NotinoScraper(args.verbose)

    if args.print:
        print(notino_scraper.product_list)
    if args.snapshot:
        notino_scraper.take_snapshot()
    if args.plot:
        notino_scraper.plot_evolution()
    for product_name in args.add_products.split(";"):
        notino_scraper.add_product(product_name)
    for search_name in args.get_prices.split("; "):
        notino_scraper.get_price(search_name)

    if args.verbose:
        print("Execution successfully ended.")
