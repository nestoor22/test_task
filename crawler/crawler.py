import argparse
import json
import logging
import random
import re
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


logger = logging.getLogger("github_search_crawler")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class GitHubSearchCrawler:
    GIT_HUB_URL = "https://github.com/"

    def __init__(self, crawl_details: dict):
        self.crawl_details = crawl_details

    def crawl(self):
        response = self.http_get(
            path=urljoin(self.GIT_HUB_URL, "search"),
            params={
                "q": ",".join(self.crawl_details["keywords"]),
                "type": self.crawl_details["type"],
            },
        )
        if not response:
            logger.warning(
                f"Failed to retrieve search results for such crawling info {self.crawl_details}"
            )
            return None

        html_parser = BeautifulSoup(response.content, features="html.parser")

        return self.parse_search_results_data(html_parser)

    def parse_search_results_data(self, html_parser: BeautifulSoup) -> list:
        extracted_data = []

        search_result_urls_blocks = html_parser.find_all(
            "div", attrs={"class": "f4 text-normal"}
        )
        for block in search_result_urls_blocks:
            item = {}
            url_tag = block.find("a")
            if not url_tag:
                continue

            item["url"] = urljoin(self.GIT_HUB_URL, url_tag.get("href"))
            if self.crawl_details["type"] == "Repositories":
                item["extra"] = self.parse_additional_info(item["url"])

            extracted_data.append(item)

        return extracted_data

    def parse_additional_info(self, url) -> dict:
        response = self.http_get(path=url)
        if response:
            html_parser = BeautifulSoup(response.content, features="html.parser")
            return {
                "owner": self.get_owner_info(html_parser),
                "language_stats": self.get_languages_stats(html_parser),
            }

        return {}

    def http_get(
        self,
        path: str,
        params: Optional[dict] = None,
    ) -> Optional[requests.Response]:
        try:
            response = requests.get(
                path,
                params,
                proxies=self.proxies,
            )
            return response
        except requests.RequestException as error:
            logger.error(f"{path} - GET request failed: {error}")

    @property
    def proxies(self):
        proxy_url = random.choice(self.crawl_details["proxies"])
        return {"http": proxy_url, "https": proxy_url}

    @staticmethod
    def get_owner_info(html_parser: BeautifulSoup) -> str:
        owner_block = html_parser.find("span", attrs={"class": "author"})
        return owner_block.get_text() if owner_block else ""

    @staticmethod
    def get_languages_stats(html_parser: BeautifulSoup):
        language_stats_info = {}
        language_stats_blocks = html_parser.find_all(
            "a", attrs={"data-ga-click": re.compile(r".*language stats.*")}
        )
        for block in language_stats_blocks:
            stats_info = block.get_text().strip().split("\n")
            if len(stats_info) == 2:
                language_stats_info[stats_info[0]] = stats_info[1]
        return language_stats_info


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crawler input')
    parser.add_argument('-d', '--details', help='Crawler input details (JSON format)', required=True)
    args = parser.parse_args()

    try:
        crawler_details = json.loads(args.details)
        crawler = GitHubSearchCrawler(crawler_details)
        results = crawler.crawl()
        print(results)
    except ValueError as error:
        logger.error(f"Input details are in incorrect format - {error}")
        exit()

