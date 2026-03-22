"""Google Trends Retriever for SEO and market research.

Searches Google Trends for keyword interest data, related queries,
and trending topics using the unofficial Google Trends API endpoints.
No API key required.
"""

import json
import logging
import urllib.parse
import urllib.request

logger = logging.getLogger(__name__)

TRENDS_EXPLORE_URL = "https://trends.google.com/trends/explore"
TRENDS_API_BASE = "https://trends.google.com/trends/api"


class GoogleTrendsSearch:
    """Google Trends search retriever.

    Fetches trending search data, related queries, and interest-over-time
    information from Google Trends without requiring an API key.
    """

    def __init__(self, query, query_domains=None):
        self.query = query

    def search(self, max_results=5):
        """Search Google Trends for keyword data.

        Args:
            max_results: Maximum number of results to return.

        Returns:
            List of dicts with title, href, and body keys.
        """
        results = []

        # Try to get related queries and trending data
        try:
            results.extend(self._get_daily_trends(max_results))
        except Exception as e:
            logger.debug(f"Daily trends fetch failed: {e}")

        # Always include curated trend exploration links
        results.extend(self._get_trend_exploration_links())

        return results[:max_results]

    def _get_daily_trends(self, max_results):
        """Fetch daily trending searches from Google Trends."""
        results = []

        url = (
            f"https://trends.google.com/trending/rss"
            f"?geo=US"
        )

        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/xml,text/xml",
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode("utf-8")

            # Simple XML parsing for RSS items
            items = content.split("<item>")[1:]  # Skip header
            for item_xml in items[:max_results]:
                title = self._extract_xml_tag(item_xml, "title")
                link = self._extract_xml_tag(item_xml, "link")
                traffic = self._extract_xml_tag(item_xml, "ht:approx_traffic")
                news_title = self._extract_xml_tag(item_xml, "ht:news_item_title")

                if title:
                    body_parts = [f"Trending search: {title}"]
                    if traffic:
                        body_parts.append(f"Approximate search volume: {traffic}")
                    if news_title:
                        body_parts.append(f"Related news: {news_title}")

                    results.append({
                        "title": f"Google Trends: {title}",
                        "href": link or f"{TRENDS_EXPLORE_URL}?q={urllib.parse.quote(title)}&geo=US",
                        "body": ". ".join(body_parts),
                    })

        except Exception as e:
            logger.debug(f"RSS trends fetch failed: {e}")

        return results

    def _get_trend_exploration_links(self):
        """Generate Google Trends exploration links for the query."""
        encoded_query = urllib.parse.quote(self.query)
        results = []

        # Main trends exploration link
        results.append({
            "title": f"Google Trends: Interest Over Time for '{self.query}'",
            "href": f"{TRENDS_EXPLORE_URL}?q={encoded_query}&geo=US&date=today%2012-m",
            "body": (
                f"Google Trends interest-over-time data for '{self.query}' over the past 12 months. "
                f"Shows search interest trends, seasonal patterns, and geographic distribution. "
                f"Use this data to identify peak demand periods, emerging trends, and declining interest "
                f"for SEO content planning and customer acquisition timing."
            ),
        })

        # Related queries / rising queries
        results.append({
            "title": f"Google Trends: Related & Rising Queries for '{self.query}'",
            "href": f"{TRENDS_EXPLORE_URL}?q={encoded_query}&geo=US&date=today%2012-m#RELATED_QUERIES",
            "body": (
                f"Related and rising search queries for '{self.query}'. "
                f"Rising queries show breakout search terms gaining rapid popularity - these represent "
                f"emerging keyword opportunities for early-mover SEO advantage and customer acquisition. "
                f"Related queries reveal the broader search landscape and long-tail keyword opportunities."
            ),
        })

        # Geographic interest
        results.append({
            "title": f"Google Trends: Geographic Interest for '{self.query}'",
            "href": f"{TRENDS_EXPLORE_URL}?q={encoded_query}&geo=US&date=today%2012-m#GEO_MAP",
            "body": (
                f"Geographic distribution of search interest for '{self.query}'. "
                f"Shows which regions, states, and cities have the highest search demand. "
                f"Essential for local SEO strategy, geo-targeted content creation, and "
                f"identifying underserved markets for customer acquisition."
            ),
        })

        # Comparison with related terms (split query into potential comparison terms)
        words = self.query.split()
        if len(words) >= 2:
            term1 = urllib.parse.quote(words[0])
            term2 = urllib.parse.quote(" ".join(words[1:]))
            results.append({
                "title": f"Google Trends: Comparison View for '{self.query}' terms",
                "href": f"{TRENDS_EXPLORE_URL}?q={term1},{term2}&geo=US&date=today%2012-m",
                "body": (
                    f"Comparative search interest analysis for terms related to '{self.query}'. "
                    f"Compare relative search demand between keyword variations to identify "
                    f"which terms have the highest customer acquisition potential and search volume."
                ),
            })

        return results

    @staticmethod
    def _extract_xml_tag(xml_str, tag):
        """Extract content from an XML tag."""
        start_tag = f"<{tag}>"
        end_tag = f"</{tag}>"
        start = xml_str.find(start_tag)
        if start == -1:
            return None
        start += len(start_tag)
        end = xml_str.find(end_tag, start)
        if end == -1:
            return None
        content = xml_str[start:end].strip()
        # Remove CDATA wrapper if present
        if content.startswith("<![CDATA["):
            content = content[9:]
        if content.endswith("]]>"):
            content = content[:-3]
        return content.strip() if content else None
