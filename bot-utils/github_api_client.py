#!/usr/bin/env python3
"""
GitHub API Client for Bot Documentation Access
Provides API-based access to bsw-arch documentation
"""

import requests
import base64
import json
from typing import Optional, List, Dict

class GitHubDocsClient:
    """Client for accessing bsw-arch documentation via GitHub API"""

    def __init__(self, owner: str = "bsw-arch", repo: str = "bsw-arch", token: Optional[str] = None):
        self.owner = owner
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"

    def get_metadata(self) -> Dict:
        """Fetch metadata.json"""
        url = f"{self.base_url}/contents/docs/metadata.json"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        content = base64.b64decode(response.json()['content']).decode('utf-8')
        return json.loads(content)

    def get_catalogue(self) -> Dict:
        """Fetch catalogue.yaml"""
        url = f"{self.base_url}/contents/docs/catalogue.yaml"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        content = base64.b64decode(response.json()['content']).decode('utf-8')
        import yaml
        return yaml.safe_load(content)

    def get_document(self, path: str) -> str:
        """Fetch a document by path"""
        url = f"{self.base_url}/contents/{path}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return base64.b64decode(response.json()['content']).decode('utf-8')

    def list_directory(self, path: str = "docs") -> List[Dict]:
        """List contents of a directory"""
        url = f"{self.base_url}/contents/{path}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return response.json()

    def search_documents(self, query: str) -> List[Dict]:
        """Search for documents containing query"""
        url = f"https://api.github.com/search/code"
        params = {
            "q": f"{query}+repo:{self.owner}/{self.repo}+extension:md"
        }
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json().get('items', [])

# Example usage
if __name__ == "__main__":
    client = GitHubDocsClient()

    print("📊 Fetching metadata...")
    metadata = client.get_metadata()
    print(f"Repository: {metadata['repository']['name']}")
    print(f"Version: {metadata['repository']['version']}")
    print(f"Total documents: {metadata['statistics']['total_documents']}")
    print(f"Bots supported: {metadata['statistics']['bots_supported']}")

    print("\n📋 Fetching catalogue...")
    catalogue = client.get_catalogue()
    print(f"Catalogue version: {catalogue['version']}")
    print(f"Documents in catalogue: {len(catalogue['documents'])}")

    print("\n📄 Fetching sample document...")
    doc = client.get_document("docs/INDEX.md")
    print(f"INDEX.md length: {len(doc)} characters")
    print(f"First 200 chars: {doc[:200]}...")
