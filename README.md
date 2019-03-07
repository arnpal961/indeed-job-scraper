## Job scrapper for indeed

Fetching first 1000 job posting from indeed for position of Software developer at location Bengaluru
then process the data and save the data in a json file using concurrency and multiprocessing.

**Description**

  For running the script open a terminal and run the commands
```
pip install -r requirements.txt
python main.py
```
* Asynchronous process is more efficient for network operations than threading or multiprocessing.
So, I fetched webpages asynchronously but html data processing is a cpu bound work for that I used
```ProcessPoolExecutor``` from python's ```concurrent.future``` library with a max worker of 15.

* I don't use threads because it has a limitation bounded by python's global interpreter lock. By using process
pooling we can avoid GIL's restrictions and can use the hardware resources.

* A ```print``` statement is provided to understand in what order fetching urls and information extraction from pages occur.

* A synchronous execution would cause the program to run minimum 15 times slower.

* Using asynchronous function can speed up more than two times than using ```ThreadPoolExecutor```.

**External library used**
   * aiohttp - For making asynchronous calls to get webpages
   * bs4 - For scraping the webpages. Here ```lxml``` is used as a parser.
