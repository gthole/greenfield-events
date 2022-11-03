from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from django.core.management.base import BaseCommand, CommandError
from events.spiders import SPIDERS


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            help='Name of the spider to run the crawl for',
        )

    def handle(self, *args, **options):
        """
        Runs crawls in parallel
        https://docs.scrapy.org/en/latest/topics/practices.html
        """
        name = options.get('name')
        if name is None:
            spiders = SPIDERS.values()
        else:
            spiders = [SPIDERS[name]]

        settings = get_project_settings()
        process = CrawlerProcess(settings)

        for spider in spiders:
            process.crawl(spider)

        process.start()
