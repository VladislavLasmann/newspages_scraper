# newspages_scraper

This projects crawls the whole archive of the implemented newspaper websites.
The data there will be preprocessed by extracting only the human readable text and grouped.

Since crawling the whole archive of the websites could produce a lot of data, a database is necessary to mange it.
**This project needs a MongoDB database.**
To get started fast, you can use a [dockerized mongodb container](https://hub.docker.com/_/mongo?tab=description). - Don't forget the set environment variables for authentication.

##### Currently available newspaper websites:
| Newspaper      | Website                                                      |
|----------------|--------------------------------------------------------------|
|Spiegel         | [http://www.spiegel.de/](http://www.spiegel.de/)             |
|Sueddeutsche    | [https://www.sueddeutsche.de/](https://www.sueddeutsche.de/) |
|Welt            | [https://www.welt.de/](https://www.welt.de/)                 |


##### Data format
The data format of each article is like shown below:
```
{
    "_id": String,
    "newspaper_name": String,
    "url": String,
    "categories": List of String,
    "main_category": String,
    "authors": List of String,
    "publish_time": datetime.date,
    "title": String,
    "text_header": " String,
    "text_body": String
}
```

### Usage
#### Installing dependencies
Execute this command in the shell:
###### For Python 2.x
```
pip install -r requirements.txt
```
###### For Python 3.x
```
pip3 install -r requirements.txt
```

#### Setting the database configuration
Open **_/database_config.py_** and set the following parameters:
```
### MONGODB connection details
MONGODB_SERVER = "localhost"
MONGODB_PORT = "32779"
MONGODB_USER = "mongouser"
MONGODB_PW = "mongopw"
```

#### Import the client
```
from client import Client
client = Client()
```

#### Crawling Pages
##### Crawl all pages
```
# This might take a while
client.crawl_all_newspages()
```

##### Crawl certain pages
```
from models.newspage import Newspage
pages_list = [Newspage.SPIEGEL, Newspage.SUEDDEUTSCHE, Newspage.WELT]
client.crawl_newspages(pages_list)
```

#### Access to crawled data
Since all of the news pages provide publish date information with the precision of seconds, you can also filter the data
with a precision of seconds.
```
from datetime import datetime
from client import Client
from models.newspage import Newspage

pages_list = [Newspage.SPIEGEL, Newspage.SUEDDEUTSCHE, Newspage.WELT]
publish_time_min = datetime(2000, 1, 1, 18, 30)       #01.01.2000, 6:30 PM
publish_time_max = datetime.now()

client = Client()
```
##### Get all articles in a given time interval
```
# Example:
listof_articles = client.get_all_articles_in_interval(pages_list, publish_time_min, publish_time_max)
```

##### Get all articles in a given time interval from given sections
Caution: the sections are as scraped from the source website
```
# Example:
section_list = ["Politik", "Bildung", "Wirtschaft"]
listof_articles = client.get_all_articles_in_interval_pages_section(pages_list, sections, section_list, publish_time_min, publish_time_max)
```