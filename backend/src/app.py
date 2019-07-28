import logging
import sys

import aiohttp_swagger
from aiohttp.web import Application, run_app

from endpoints import *


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", stream=sys.stdout
    )

    # Create the web application.
    app = Application()

    # Register the endpoints.
    app.router.add_route('GET', "/devices", devices_get)
    app.router.add_route('POST', "/devices", devices_post)
    app.router.add_route('GET', "/sightings", sightings_get)
    app.router.add_route('POST', "/sightings", sightings_post)

    # Launch the web application with a Swagger page.
    aiohttp_swagger.setup_swagger(app, swagger_url='swagger')
    run_app(app, port=8080)
