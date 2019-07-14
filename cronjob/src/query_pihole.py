import logging
import os
import sys
import time
from collections import defaultdict

import requests

LOGGER = logging.getLogger("query_pihole")
LOGGER.setLevel(logging.INFO)
PIHOLE_HOST = os.environ["PIHOLE_HOST"]
PIHOLE_TOKEN = os.environ["PIHOLE_TOKEN"]


def get_dns_requests():
    epoch_now = int(time.time())
    api = f"http://{PIHOLE_HOST}/admin/api.php?getAllQueries"
    params = {"from": epoch_now - 3600, "to": epoch_now, "auth": PIHOLE_TOKEN}
    LOGGER.info("Making request to %s with params %s", api, params)
    response = requests.get(url=api, params=params)
    LOGGER.info("Received response from %s", response.url)
    response.raise_for_status()
    return response.json()


def post_sighting(alias: str, epoch_ts: int):
    api = f'http://{os.environ["BACKEND_HOST"]}/sightings'
    LOGGER.info("Making request to %s", api)
    test = requests.get(api)
    LOGGER.info("Test %s", test)
    response = requests.post(api, json={"alias": alias, "timestamp": epoch_ts})
    response.raise_for_status()


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", stream=sys.stdout
    )
    dns_requests = get_dns_requests()

    last_sightings = defaultdict(lambda: 0)
    for dns_request in dns_requests["data"]:
        LOGGER.debug("Processing %s", dns_request)
        if int(dns_request[0]) > int(last_sightings[dns_request[3]]):
            last_sightings[dns_request[3]] = dns_request[0]
    LOGGER.info(
        "Received %s DNS requests, contained %s last sightings",
        len(dns_requests["data"]),
        len(last_sightings),
    )

    for key, value in last_sightings.items():
        post_sighting(key, value)
