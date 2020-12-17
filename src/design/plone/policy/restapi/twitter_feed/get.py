# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from plone import api
from plone.restapi.search.utils import unflatten_dotted_dict
from copy import deepcopy

import logging
import requests
import six

logger = logging.getLogger(__name__)
ENDPOINT = "https://api.twitter.com/2/tweets/search/recent"


@implementer(IPublishTraverse)
class TwitterFeedGet(Service):
    def reply(self):

        token = api.portal.get_registry_record(
            name="design.plone.policy.twitter_token"
        )
        if not token:
            msg = "BEARER token not set: please set it into plone registry to be able to fetch Tweets."  # noqa
            logger.error(msg)
            self.request.response.setStatus(500)
            return dict(error=dict(message=msg))

        query = self.generate_query()
        if query.get("error", ""):
            self.request.response.setStatus(400)
            return dict(error=dict(message=query["error"]))

        resp = requests.get(
            url=ENDPOINT,
            params=query,
            headers={"Authorization": "Bearer {}".format(token)},
        )
        return self.convert_tweets(data=resp.json())

    def generate_query(self):
        query = self.request.form.copy()
        query = unflatten_dotted_dict(query)
        if not query:
            return {"error": "You need to provide at least an author."}
        max_results = int(query.get("max_results", "10"))
        if max_results < 10 or max_results > 100:
            return {"error": "max_results should be between 10 and 100."}
        authors = query.get("authors", [])
        if not authors:
            return {"error": "You need to provide at least an author."}
        if isinstance(authors, six.string_types):
            authors = [authors]
        res = {
            "query": " OR ".join(["from: {}".format(x) for x in authors]),
            # additional infos for tweets
            "tweet.fields": "entities,source,public_metrics",
            "expansions": "attachments.media_keys,author_id",
            "media.fields": "type,preview_image_url,height,media_key,public_metrics,url,width",  # noqa
            "user.fields": "name,profile_image_url,username",
        }
        return res

    def convert_tweets(self, data):
        tweets = data.get("data", [])
        users = data.get("includes", {}).get("users", [])

        if not tweets:
            return []

        res = []
        for tweet in tweets:
            html = self.convert_data_to_html(data=tweet)
            if html:
                tweet_data = {
                    "text": html,
                    "id": tweet["id"],
                    "retweet_count": tweet["public_metrics"]["retweet_count"],
                    "reply_count": tweet["public_metrics"]["reply_count"],
                    "like_count": tweet["public_metrics"]["like_count"],
                }
                author_id = tweet.get("author_id", "")
                for user in users:
                    if author_id == user["id"]:
                        tweet_data["author"] = user
                res.append(tweet_data)
        return res

    def convert_data_to_html(self, data):
        entities = data.get("entities", {})
        text = data.get("text")
        if not entities:
            return text
        html = deepcopy(text)
        href_template = (
            '<a href="{url}" title="{title}" target="_blank">{text}</a>'
        )
        #  replace hashtags
        for hashtag in entities.get("hashtags", []):
            tag_text = text[hashtag["start"] : hashtag["end"]]
            replaced = href_template.format(
                url="https://twitter.com/hashtag/{}".format(hashtag["tag"]),
                title=tag_text,
                text=tag_text,
            )
            html = html.replace(tag_text, replaced,)

        # replace mentions
        for mention in entities.get("mentions", []):
            mention_text = text[mention["start"] : mention["end"]]
            replaced = href_template.format(
                url="https://twitter.com/{}".format(mention["username"]),
                title=mention_text,
                text=mention_text,
            )
            html = html.replace(mention_text, replaced,)

        #  replace urls
        occurrences = {}
        for url_data in entities.get("urls", []):
            url = url_data["url"]
            if url not in occurrences:
                occurrences[url] = 1
            else:
                occurrences[url] += 1
        for url_data in entities.get("urls", []):
            url = url_data["url"]
            to_replace = text[url_data["start"] : url_data["end"]]
            if occurrences[url] > 1:
                html = html.replace(to_replace, "")
            else:
                if url_data["display_url"].startswith("pic.twitter.com"):
                    html = html.replace(to_replace, "")
                else:
                    replaced = href_template.format(
                        url=url,
                        title=url_data.get("title", url_data["display_url"]),
                        text=url_data["display_url"],
                    )
                    html = html.replace(to_replace, replaced,)
        return html
