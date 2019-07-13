from aiohttp.web import Application, run_app

from aiohttp_rest import RestResource
from models import Sighting


sightings = {}
app = Application()
person_resource = RestResource('sightings', Sighting, sightings, ('id', 'timestamp', 'ip_address'), 'id')
person_resource.register(app.router)


if __name__ == '__main__':
    run_app(app)

"""
import datetime

from models import session, Sighting

# POST
test = Sighting(datetime.datetime.now(), "test")
session.add(test)
session.commit()

# GET
instance = session.query(Sighting).first()
print(instance.id)

print("Test done")
"""