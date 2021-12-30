import getopt
import sys
from notino_scraper import NotinoScraper

if __name__ == '__main__':
    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, "pso:a:", ["print", "take_snapshot", "output_file=", "add_product="])

    for opt, arg in opts:
        if opt in ("-o", "--output"):
            NotinoScraper.update_datafile(arg)
            break

    # This instantiation takes some time.
    notino_scraper = NotinoScraper()

    for opt, arg in opts:
        if opt in ("-s", "--take_snapshot"):
            notino_scraper.take_snapshot()
        if opt in ("-a", "--add_product"):
            notino_scraper.add_product(arg)
        if opt in ("-p", "--print"):
            print(notino_scraper.product_list)
