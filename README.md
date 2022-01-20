# Notino scraper

This tool is designed to track the prices of some products available on the website notino.fr over time.

This website offers a large range of discounts and choosing the right moment to buy a product can save a lot of money.

---

## Description

This project can be used in command line by calling the project directory:

- `python notino_scraper <options>`

This tool is meant to record the prices of a list of products over time in a `.json` file. This `.json` file will take
the form of an array of products, each product being described by the following fields:

- `name`: the name of the product as displayed on the website.
- `description`: usually indicates the concentration (edp, edt, cologne, ...).
- `brand`: the brand that markets the product.
- `prices`: a list of all the prices recorded using this tool. A price consists in a date, a volume and a price in
  euros (I will consider adding the currency).

A few use cases are described below, and you can also develop your own tools to process the data extracted for a more
customized use.

---

## Extracting data

#### Adding products to the list of products

You can use the following commands to add a product or a list of products to the list of tracked products.

- `python notino_scraper -a: <product_name>`: adds a single product.
- `python notino_scraper -m: <product_names; product_2; ...>`: adds a list of products. Make sure you separate each
  product name with a semicolon and a space.

> *Note*: there is no need to be exactly accurate on the names of the product you wish to add.
> The product added will be the first result that appears in the search bar when typing the name you entered.

### Snapshotting the prices of every product in the list

You can use the following command to record the prices of every product in the list:

- `python notino_scraper -s`

This command will loop over each product already recorded in the `.json` file and append to its list of prices the price
found as of the current date. If there is already a price in the file for the same date and volume it will not be added.

---

## Processing the data

### Plotting the evolution of the prices of each product over time

You can use the following command to generate a series of graphs representing the evolution of the prices of every
product tracked in the `.json` file:

- `python notino_scraper -g`

By default `5` products will be put on the same graph but this can be customized.  
The plots will be stored in a directory specified in the configuration (please check the dedicated section below).

### Printing the prices recorded

You can use the following command to pretty-print the data stored in the `.json` file:

- `python notino_scraper -p`

### Predicting the optimal buying date of a product

Work in progress.

---

## Additional feature

You can also use the following command to use this tool directly instead of using it through the `.json` file:

- `python notino_scraper -f: <product_1; product_2, ...>`: prints the prices of a list of products. Make sure you
  separate each product name with a semicolon and a space.

> This feature is mostly useful for debugging purposes
> considering that it will be faster to go on the website and see for yourself.

---

## Verbose

You can set the level of verbose through the command line parameter `-v`. There are currently two levels available, by
default the highest level of verbose will be used and you will have to use the following syntax for less verbose:

- `python notino_scraper -v: "false" <other_parameters>`

The other parameters are the ones mentioned above (`-p` to print, `-s` to snapshot, `-a` to add a product, ...).

---

## Configuration

The parameters needed to run this program are stored in the `config.yml` file.

During an execution, when the program finds out a parameter is missing or is incorrect (for instance when the parameter
points to a non-existing file), it will ask for a replacement value. Specifying the correct value then will also update
the `config.yml` file.  
Basically you do not really need to worry about configuration.

You can use the following commands to set the parameters:

- `python notino_scraper -o: <filepath>`: sets the path of the `.json` file that stores the data.
- `python notino_scraper -c`: sets every existing parameter with a series of questions/inputs. You might want to run
  that one the first time you use this tool.

---

## Tech

This tool is entirely written in Python and uses a Selenium WebDriver to extract data from the website. The browser in
run in headless mode.

> *Note:* if you interrupt an execution of this program the instance of Firefox used might not be closed.
> In that case you will have to close it manually using your task manager.
