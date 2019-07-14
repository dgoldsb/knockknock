"""
Used for reference:
- https://blog.apcelent.com/create-rest-api-using-aiohttp.html
- https://medium.com/@chimamireme/setting-up-a-modern-python-web-application-with-aiohttp-graphql-and-docker-149c52657142
"""

import inspect
import json
import logging
from collections import OrderedDict

from aiohttp.web import (
    HTTPBadRequest,
    HTTPMethodNotAllowed,
    Request,
    Response,
    UrlDispatcher,
)
from sqlalchemy import func

from models import Sighting, session


DEFAULT_METHODS = ("GET", "POST", "PUT", "DELETE")
LOGGER = logging.getLogger("query_pihole")
LOGGER.setLevel(logging.INFO)


class RestEndpoint:
    def __init__(self):
        self.methods = {}

        for method_name in DEFAULT_METHODS:
            method = getattr(self, method_name.lower(), None)
            if method:
                self.register_method(method_name, method)

    def register_method(self, method_name, method):
        self.methods[method_name.upper()] = method

    async def dispatch(self, request: Request):
        method = self.methods.get(request.method.upper())
        if not method:
            raise HTTPMethodNotAllowed("", DEFAULT_METHODS)

        wanted_args = list(inspect.signature(method).parameters.keys())
        available_args = request.match_info.copy()
        available_args.update({"request": request})

        unsatisfied_args = set(wanted_args) - set(available_args.keys())
        if unsatisfied_args:
            # Expected match info that doesn't exist.
            raise HTTPBadRequest

        return await method(
            **{arg_name: available_args[arg_name] for arg_name in wanted_args}
        )


class SightingEndpoint(RestEndpoint):
    def __init__(self, resource):
        super().__init__()
        self.resource = resource

    async def get(self, request: Request) -> Response:
        LOGGER.info("Received %s request on %s", request.method, request.url)
        try:
            request_body = await request.json()

            datetime_from = int(request_body["from"])
            try:
                datetime_to = int(request_body["to"])
                sightings = (
                    session.query(Sighting.alias, Sighting.last_activity_timestamp)
                    .distinct()
                    .filter(
                        Sighting.last_activity_timestamp >= datetime_from,
                        Sighting.last_activity_timestamp <= datetime_to,
                    )
                )
            except KeyError:
                sightings = (
                    session.query(Sighting.alias, Sighting.last_activity_timestamp)
                    .distinct()
                    .filter(Sighting.last_activity_timestamp >= datetime_from)
                )
        except json.decoder.JSONDecodeError:
            sightings = session.query(
                Sighting.alias, Sighting.last_activity_timestamp
            ).distinct()

        return Response(
            status=200,
            body=self.resource.encode(
                {
                    "sightings": [
                        {
                            "alias": sighting.alias,
                            "timestamp": sighting.last_activity_timestamp,
                        }
                        for sighting in sightings
                    ]
                }
            ),
            content_type="application/json",
        )

    async def post(self, request: Request) -> Response:
        LOGGER.info("Received %s request on %s", request.method, request.url)
        data = await request.json()
        sighting = Sighting(
            alias=data["alias"], last_activity_timestamp=data["timestamp"]
        )
        session.add(sighting)
        session.commit()

        records = session.query(Sighting).filter(
            Sighting.id == session.query(func.max(Sighting.id))
        )

        return Response(
            status=200,
            body=self.resource.encode(records[0].to_json()),
            content_type="application/json",
        )


class RestResource:
    def __init__(self, sightings, factory, collection, properties, id_field):
        self.sightings = sightings
        self.factory = factory
        self.collection = collection
        self.properties = properties
        self.id_field = id_field

        self.sighting_endpoint = SightingEndpoint(self)

    def register(self, router: UrlDispatcher):
        router.add_route(
            "*",
            "/{sightings}".format(sightings=self.sightings),
            self.sighting_endpoint.dispatch,
        )

    def render(self, instance):
        return OrderedDict(
            (notes, getattr(instance, notes)) for notes in self.properties
        )

    @staticmethod
    def encode(data):
        return json.dumps(data, indent=4).encode("utf-8")

    def render_and_encode(self, instance):
        return self.encode(self.render(instance))
