import getopt
import sys
from notino_scraper import *

if __name__ == '__main__':
    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv,
                               "pso:a:v:gf:c",
                               ["print",
                                "take_snapshot",
                                "output_file=",
                                "add_products=",
                                "verbose=",
                                "plot",
                                "get_prices=",
                                "set_config"])
    verbose = True

    for opt, arg in opts:
        if opt in ("-o", "--output"):
            NotinoScraper.update_datafile(arg)
            exit()
        if opt in ("-v", "--verbose"):
            verbose = arg not in ["False", "false", "N", "n"]
        if opt in ("-c", "--set_config"):
            NotinoScraper.set_config_parameters()
            exit()

    # This instantiation takes some time.
    notino_scraper = NotinoScraper(verbose)

    for opt, arg in opts:
        if opt in ("-s", "--take_snapshot"):
            notino_scraper.take_snapshot()
        if opt in ("-a", "--add_products"):
            for product_name in arg.split("; "):
                notino_scraper.add_product(product_name)
        if opt in ("-p", "--print"):
            print(notino_scraper.product_list)
        if opt in ("-g", "--plot"):
            notino_scraper.plot_evolution()
        if opt in ("-f", "--get_prices"):
            for search_name in arg.split("; "):
                notino_scraper.get_price(search_name)
