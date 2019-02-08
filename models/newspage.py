from enum import Enum
from scraper.spiders.spiegelDE import SpiegeldeSpider
from scraper.spiders.sueddeutsche import SueddeutscheSpider
from scraper.spiders.weltDE import WeltdeSpider


class Newspage(Enum):
    SPIEGEL = SpiegeldeSpider()
    SUEDDEUTSCHE = SueddeutscheSpider()
    WELT = WeltdeSpider()

    def get_spider(self):
        return self.value

