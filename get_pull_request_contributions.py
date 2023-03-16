#!/usr/bin/python3

import asyncio
import os
from typing import Dict, List, Optional, Set, Tuple, Any, cast
from datetime import datetime, timedelta

import aiohttp
import requests

class PRStats(object):
    
    def __init__(
        self,
        username: str,
        access_token: str,
        session: aiohttp.ClientSession,
        repo_owner: str = None,
        startDateTime: datetime = datetime.now() - timedelta(days = 365),
        endDateTime: datetime = datetime.now(),
    ):
        self.username = username
        self.access_token = access_token
        self.session = session
        
        self.repo_owner = repo_owner
        self.startDateTime = startDateTime
        self.endDateTime = endDateTime
        self.maxNumberOfRepos = 100
        
        self._prContributions: Optional[int] = None

    async def to_str(self) -> str:
        """
        :return: summary of all available statistics
        """
        return f"""Pull Request Contributions: {await self.prContributions}"""
      
    @property
    async def prContributions(self) -> int:
        """
        :return: total number of pull request contributions the user has performed (approvals, etc.)
        """
        if self._prContributions is not None:
            return self._prContributions
        await self.get_stats()
        assert self._prContributions is not None
        return self._prContributions

    async def get_stats(self) -> None:
        """
        Get lots of summary statistics using one big query. Sets many attributes
        """
        self._prContributions = 0

        url = 'https://api.github.com/graphql'
        query = (
        f"""
        {{
          user(login: "{self.username}") {{
            contributionsCollection(from: "{self.startDateTime.isoformat(sep='T', timespec='seconds')}", to: "{self.endDateTime.isoformat(sep='T', timespec='seconds')}") {{
              pullRequestReviewContributionsByRepository(maxRepositories: {self.maxNumberOfRepos}) {{
                contributions {{
                  totalCount
                }}
                repository {{
                  nameWithOwner
                }}
              }}
            }}
          }}
        }}
        """
        )
        json = { 'query' : query}
        api_token = f"{self.access_token}"
        headers = {'Authorization': 'token %s' % api_token}
        r = requests.post(url=url, json=json, headers=headers)
        
        #print(f"query: {query}")
        
        print(f"json_data {r.json()}")
        json_data = r.json()['data']['user']['contributionsCollection']['pullRequestReviewContributionsByRepository']
        if repo_owner is None:
            self._prContributions = sum([i['contributions']['totalCount'] for i in json_data])
        else:
            self._prContributions = sum([i['contributions']['totalCount'] for i in json_data if i['repository']['nameWithOwner'].startswith(self.repo_owner)])
        print(f'Number of reviews: {self._prContributions}')
        self._prContributions = self._prContributions
        

###############################################################################
# Main Function
###############################################################################


async def main() -> None:
    """
    Used mostly for testing; this module is not usually run standalone
    """
    access_token = os.getenv("ACCESS_TOKEN")
    user = os.getenv("GITHUB_ACTOR")
    if access_token is None or user is None:
        raise RuntimeError(
            "ACCESS_TOKEN and GITHUB_ACTOR environment variables cannot be None!"
        )
    async with aiohttp.ClientSession() as session:
        s = PRStats(user, access_token, session)
        print(await s.to_str())


if __name__ == "__main__":
    asyncio.run(main())
