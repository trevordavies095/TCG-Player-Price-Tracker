# TCGCardTracker

TCGCardTracker is a program that will allow you to track the TCG Player market value of your Pokemon* collection.

The prices are acquired by web scraping the data from tcgplayer.com and storing in a SQLite database.

(*) This has only been tested with Pokemon cards on TCG Player.

## Prerequisites

You must have Python3 to run this program.

A few pip installs are also needed as well.

```bash
python3 -m pip install -r requirements.txt
```

## Usage
```bash
python3 TCGCardTracker.py <required_argument> <optional_argument>
```

### add
```bash
python3 TCGCardTracker.py add "https://shop.tcgplayer.com/pokemon/xy-evolutions/mewtwo-ex"
```
Adds a card to your collection.

### delete
```bash
python3 TCGCardTracker.py delete "https://shop.tcgplayer.com/pokemon/xy-evolutions/mewtwo-ex"
```
Deletes a card from your collection.

### update
```bash
python3 TCGCardTracker.py update
```
Updates pricing data for every card in your collection.

### export
```bash
python3 TCGCardTracker.py export
```
Exports a text file of your collection in the form of TCG Player URLs. This text file can be ingested by using the import argument.

### export_collection
```bash
python3 TCGCardTracker.py export_collection
```
Exports your collection to a .csv including most recent price data.

### import
```bash
python3 TCGCardTracker.py import "my_collection.txt"
```
Imports a text file of TCG Player URLs and adds them to your collection.

### worth
```bash
python3 TCGCardTracker.py worth
```
Outputs the total worth of your collection by using the most recent pricing data.

### graph
```bash
python3 TCGCardTracker.py graph_card_worth "https://shop.tcgplayer.com/pokemon/xy-evolutions/mewtwo-ex"
```
Displays a graph of a given card's historical pricing data. Also includes a trend line.

![graph_card_worth example](https://i.imgur.com/VHzGVBJ.png)

### ticker
```bash
python3 TCGCardTracker.py ticker
python3 TCGCardTracker.py ticker 30
```
Displays a ticker grid of the change in value over a given time. If run without the days back parameter it will default to 7 days.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)