from unittest import TestCase, mock

import requests
from bs4 import BeautifulSoup

from .crawler import GitHubSearchCrawler


MOCK_RESULT_ITEM = """
<li class="repo-list-item hx_hit-repo d-flex flex-justify-start py-4 public source">
  <div class="flex-shrink-0 mr-2">
      <svg style="color: #6a737d" aria-hidden="true" height="16" viewBox="0 0 16 16" version="1.1" width="16" data-view-component="true" class="octicon octicon-repo">
    <path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9zm10.5-1V9h-8c-.356 0-.694.074-1 .208V2.5a1 1 0 011-1h8zM5 12.25v3.25a.25.25 0 00.4.2l1.45-1.087a.25.25 0 01.3 0L8.6 15.7a.25.25 0 00.4-.2v-3.25a.25.25 0 00-.25-.25h-3.5a.25.25 0 00-.25.25z"></path>
</svg>
  </div>
  <div class="mt-n1 flex-auto">
    <div class="d-flex">
      <div class="f4 text-normal">
        <a class="v-align-middle" data-hydro-click="{&quot;event_type&quot;:&quot;search_result.click&quot;,&quot;payload&quot;:{&quot;page_number&quot;:1,&quot;per_page&quot;:10,&quot;query&quot;:&quot;openstack,nova,css&quot;,&quot;result_position&quot;:1,&quot;click_id&quot;:55005225,&quot;result&quot;:{&quot;id&quot;:55005225,&quot;global_relay_id&quot;:&quot;MDEwOlJlcG9zaXRvcnk1NTAwNTIyNQ==&quot;,&quot;model_name&quot;:&quot;Repository&quot;,&quot;url&quot;:&quot;https://github.com/atuldjadhav/DropBox-Cloud-Storage&quot;},&quot;originating_url&quot;:&quot;https://github.com/search?q=openstack%2Cnova%2Ccss&amp;type=repositories&quot;,&quot;user_id&quot;:45801713}}" data-hydro-click-hmac="81b3d6865c74589f9ae92b99a0a2a4cf5324221579affc34ca20334bd70d4b39" href="/atuldjadhav/DropBox-Cloud-Storage">atuldjadhav/DropBox-Cloud-Storage</a>

      </div>
    </div>
      <p class="mb-1">
        Technologies:- <em>Openstack</em> <em>NOVA</em>, NEUTRON, SWIFT, CINDER API's, JAVA, JAX-RS, MAVEN, JSON, HTML5, <em>CSS</em>, JAVASCRIPT, ANGUL…
      </p>
    <div>
      <div class="d-flex flex-wrap text-small color-fg-muted">
          <div class="mr-3">
          <span class="">
              <span class="repo-language-color" style="background-color: #563d7c"></span>
              <span itemprop="programmingLanguage">CSS</span>
          </span>
      </div>
      <div class="mr-3">
            Updated <relative-time datetime="2016-03-29T19:40:33Z" class="no-wrap" title="Mar 29, 2016, 10:40 PM GMT+3">on Mar 29, 2016</relative-time>
      </div>
      </div>
    </div>
  </div>
</li>
"""

MOCK_RESULT_DETAILS = """
<div>
<div class="css-truncate css-truncate-overflow color-fg-muted">
  <span class="commit-author user-mention" title="atuldjadhav">atuldjadhav</span>
  <span class="d-none d-sm-inline"> 
      <a data-pjax="true" data-test-selector="commit-tease-commit-message" title="Virtualization" class="Link--primary markdown-title" href="/atuldjadhav/DropBox-Cloud-Storage/commit/999ca054654758fdd53210e5e532e37df8f553af">Virtualization</a>
  </span>
</div>
</div>
"""

MOCK_HTML_AUTHOR_BLOCK = """<span class="author flex-self-stretch" itemprop="author">
    <a class="url fn" rel="author" data-hovercard-type="user" data-hovercard-url="/users/nestoor22/hovercard" data-octo-click="hovercard-link-click" data-octo-dimensions="link_type:self" href="/nestoor22">nestoor22</a>
  </span>
"""

MOCK_HTML_LANGUAGES_BLOCK = """
<ul class="list-style-none">
    <li class="d-inline">
        <a class="d-inline-flex flex-items-center flex-nowrap Link--secondary no-underline text-small mr-3" href="/atuldjadhav/DropBox-Cloud-Storage/search?l=css" data-ga-click="Repository, language stats search click, location:repo overview">
          <svg style="color:#563d7c;" aria-hidden="true" height="16" viewBox="0 0 16 16" version="1.1" width="16" data-view-component="true" class="octicon octicon-dot-fill mr-2">
    <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8z"></path>
</svg>
          <span class="color-fg-default text-bold mr-1">CSS</span>
          <span>52.0%</span>
        </a>
    </li>
    <li class="d-inline">
        <a class="d-inline-flex flex-items-center flex-nowrap Link--secondary no-underline text-small mr-3" href="/atuldjadhav/DropBox-Cloud-Storage/search?l=javascript" data-ga-click="Repository, language stats search click, location:repo overview">
          <svg style="color:#f1e05a;" aria-hidden="true" height="16" viewBox="0 0 16 16" version="1.1" width="16" data-view-component="true" class="octicon octicon-dot-fill mr-2">
    <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8z"></path>
</svg>
          <span class="color-fg-default text-bold mr-1">JavaScript</span>
          <span>47.2%</span>
        </a>
    </li>
    <li class="d-inline">
        <a class="d-inline-flex flex-items-center flex-nowrap Link--secondary no-underline text-small mr-3" href="/atuldjadhav/DropBox-Cloud-Storage/search?l=html" data-ga-click="Repository, language stats search click, location:repo overview">
          <svg style="color:#e34c26;" aria-hidden="true" height="16" viewBox="0 0 16 16" version="1.1" width="16" data-view-component="true" class="octicon octicon-dot-fill mr-2">
    <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8z"></path>
</svg>
          <span class="color-fg-default text-bold mr-1">HTML</span>
          <span>0.8%</span>
        </a>
    </li>
</ul>
"""


class MockResponse:
    def __init__(self, content):
        self.content = content


class TestGitHubCrawler(TestCase):
    def setUp(self) -> None:
        self.wikis_crawler = GitHubSearchCrawler(
            {
                "keywords": ["openstack", "nova", "css"],
                "proxies": ["80.48.119.28:8080"],
                "type": "Wikis",
            }
        )
        self.repos_crawler = GitHubSearchCrawler(
            {
                "keywords": ["openstack", "nova", "css"],
                "proxies": ["80.48.119.28:8080"],
                "type": "Repositories",
            }
        )

    @mock.patch(
        "crawler.crawler.GitHubSearchCrawler.http_get",
        side_effect=[MockResponse(content=MOCK_RESULT_ITEM)],
    )
    def test_extraction(self, mock_http_get):
        res = self.wikis_crawler.crawl()
        self.assertIs(mock_http_get.called, True)
        self.assertEqual(len(res), 1)
        self.assertIn(
            {"url": "https://github.com/atuldjadhav/DropBox-Cloud-Storage"}, res
        )

    @mock.patch("crawler.crawler.GitHubSearchCrawler.parse_additional_info")
    @mock.patch(
        "crawler.crawler.GitHubSearchCrawler.http_get",
        side_effect=[MockResponse(content=MOCK_RESULT_ITEM)],
    )
    def test_additional_extraction_is_not_run_for_wikis(
        self, mock_http_get, mock_parse_additional_info
    ):
        self.wikis_crawler.crawl()
        self.assertTrue(mock_http_get.called)
        self.assertFalse(mock_parse_additional_info.called)

    @mock.patch("crawler.crawler.GitHubSearchCrawler.parse_additional_info")
    @mock.patch(
        "crawler.crawler.GitHubSearchCrawler.http_get",
        side_effect=[
            MockResponse(content=MOCK_RESULT_ITEM),
            MockResponse(content=MOCK_RESULT_DETAILS),
        ],
    )
    def test_additional_extraction_is_run_for_repos(
        self, mock_http_get, mock_parse_additional_info
    ):
        res = self.repos_crawler.crawl()
        self.assertEqual(len(res), 1)
        self.assertTrue(mock_http_get.called)
        self.assertTrue(mock_parse_additional_info.called)

    @mock.patch(
        "crawler.crawler.GitHubSearchCrawler.http_get",
        side_effect=[
            MockResponse(content=MOCK_HTML_AUTHOR_BLOCK + MOCK_HTML_LANGUAGES_BLOCK),
        ],
    )
    def test_additional_extraction(self, mock_http_get):
        result = self.repos_crawler.parse_additional_info("http://test.com/")
        self.assertTrue(mock_http_get.called)
        mock_http_get.assert_called_with(path="http://test.com/")
        self.assertIn("owner", result)
        self.assertIn("language_stats", result)

    @mock.patch(
        "crawler.crawler.requests.get",
        side_effect=[requests.RequestException],
    )
    def test_request_failed(self, mock_http_get):
        res = self.wikis_crawler.crawl()
        self.assertTrue(mock_http_get.called)
        self.assertRaises(requests.RequestException)
        self.assertIsNone(res)

    def test_extract_languages(self):
        html_parser = BeautifulSoup(MOCK_HTML_LANGUAGES_BLOCK, features="html.parser")
        result = self.repos_crawler.get_languages_stats(html_parser)
        self.assertEqual(len(result), 3)
        self.assertEqual(result["CSS"], "52.0%")

    def test_extract_owner(self):
        html_parser = BeautifulSoup(MOCK_HTML_AUTHOR_BLOCK, features="html.parser")
        result = self.repos_crawler.get_owner_info(html_parser)
        self.assertEqual("nestoor22", result)
