from aiohttp.web import Application, run_app

from aiohttp_rest import RestResource
from models import Sighting


sightings = {}
app = Application()
person_resource = RestResource(
    "sightings", Sighting, sightings, ("id", "timestamp", "ip_address"), "id"
)
person_resource.register(app.router)


if __name__ == "__main__":
    run_app(app, host='localhost', port=9090)
