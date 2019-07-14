import logging
import sys
from aiohttp.web import Application, run_app

from aiohttp_rest import RestResource
from models import Sighting


sightings = {}
app = Application()
sightings_resource = RestResource(
    "sightings", Sighting, sightings, ("id", "timestamp", "ip_address"), "id"
)
sightings_resource.register(app.router)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", stream=sys.stdout
    )
    run_app(app, port=8080)
