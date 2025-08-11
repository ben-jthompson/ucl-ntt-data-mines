import os
import re
import traceback
from langchain_community.tools.brave_search.tool import BraveSearch  # Optional, or use your own search function

class ErrorHandler:
    def __init__(self, url, error, query=None):
        self.url = url
        self.error = error
        self.query = query or self.generate_query_from_url()
        self.brave_search = BraveSearch.from_api_key(os.getenv("BRAVE_API_KEY"))  # Optional

    def generate_query_from_url(self):
        # Try to create a simple search query based on the filename or structure of the URL
        filename = self.url.split("/")[-1].replace("_", " ").replace("-", " ")
        base_query = re.sub(r"\.pdf$", "", filename, flags=re.IGNORECASE)
        return f"{base_query} file site:gov.uk OR site:.ac.uk OR site:.org"

    def is_ssl_error(self):
        return "SSL" in str(self.error) or "handshake" in str(self.error)

    def search_alternative_source(self):
        print(f"Searching alternative source for query: {self.query}")
        # try:
        #     results = self.brave_search.invoke(self.query)
        #     for result in results["results"]:
        #         if result["url"].endswith(".pdf"):
        #             print("Alternative PDF found:", result["url"])
        #             return result["url"]
        # except Exception as e:
        #     print("Search failed:", e)
        return None

    def handle_error(self):
        print(f"Handling error for URL: {self.url}")
        if self.is_ssl_error():
            print("Detected SSL handshake error. Attempting to find alternative source...")
            alt_url = self.search_alternative_source()
            if alt_url:
                print(f"Retrying with alternative source: {alt_url}")
                # You could return or pass this URL to retry logic in your main pipeline
                return alt_url
        else:
            print("Unhandled error:", traceback.format_exc())

    def run(self):
        return self.handle_error()
