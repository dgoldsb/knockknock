"""
Used for reference: https://blog.apcelent.com/create-rest-api-using-aiohttp.html.
"""

import inspect
import json
from collections import OrderedDict

from aiohttp.web import HTTPBadRequest, HTTPMethodNotAllowed, Request, Response, UrlDispatcher

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
        data = []

        sightings = session.query(Sighting).all()
        for instance in self.resource.collection.values():
            data.append(self.resource.render(instance))
        data = self.resource.encode(data)
        return Response ( status=200, body=self.resource.encode({
            'notes': [
                {'id': note.id, 'title': note.title, 'description': note.description,
                 'created_at': note.created_at, 'created_by': note.created_by, 'priority': note.priority}

                for note in session.query(Note)

            ]
        }), content_type='application/json')


    async def post(self, request: Request):
        data = await request.json()
        note=Note(title=data['title'], description=data['description'], created_at=data['created_at'], created_by=data['created_by'], priority=data['priority'])
        session.add(note)
        session.commit()

        return Response(status=201, body=self.resource.encode({
            'notes': [
                {'id': note.id, 'title': note.title, 'description': note.description,
                 'created_at': note.created_at, 'created_by': note.created_by, 'priority': note.priority}

                for note in session.query(Note)

            ]
        }), content_type='application/json')


class RestResource:
    def __init__(self, sightings, factory, collection, properties, id_field):
        self.sightings = sightings
        self.factory = factory
        self.collection = collection
        self.properties = properties
        self.id_field = id_field

        self.sighting_endpoint = SightingEndpoint(self)

    def register(self, router: UrlDispatcher):
        router.add_route('*', '/{sightings}'.format(sightings=self.sightings), self.sighting_endpoint.dispatch)

    def render(self, instance):
        return OrderedDict((notes, getattr(instance, notes)) for notes in self.properties)

    @staticmethod
    def encode(data):
        return json.dumps(data, indent=4).encode('utf-8')

    def render_and_encode(self, instance):
        return self.encode(self.render(instance))
