"""
Used for reference: https://blog.apcelent.com/create-rest-api-using-aiohttp.html.
"""

import datetime
import inspect
import json
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
            raise HTTPBadRequest("")

        return await method(
            **{arg_name: available_args[arg_name] for arg_name in wanted_args}
        )


class SightingEndpoint(RestEndpoint):
    def __init__(self, resource):
        super().__init__()
        self.resource = resource

    async def get(self, request: Request) -> Response:
        request_body = await request.json()

        datetime_from = datetime.datetime.strptime(request_body["from"], '%Y-%m-%dT%h:%m:%s.%f')
        try:
            datetime_to = datetime.datetime.strptime(request_body["to"], '%Y-%m-%dT%h:%m:%s.%f')
            records = session.query(Sighting).filter(
                Sighting.timestamp >= datetime_from,
                Sighting.timestamp <= datetime_to,
            )
        except KeyError:
            records = session.query(Sighting).filter(
                Sighting.timestamp >= datetime_from
            )

        return Response(
            status=200,
            body=self.resource.encode(
                {
                    "notes": [
                        {
                            "id": sighting.id,
                            "ip_address": sighting.ip_address,
                            "timestamp": sighting.ip_address,
                        }
                        for sighting in records
                    ]
                }
            ),
            content_type="application/json",
        )

    async def post(self, request: Request) -> Response:
        data = await request.json()
        sighting = Sighting(ip_address=data["ip_address"])
        session.add(sighting)
        session.commit()

        record = session.query(Sighting).filter(
            Sighting.id == session.query(func.max(Sighting.id))
        )

        return Response(
            status=200,
            body=self.resource.encode(record.to_json()),
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
