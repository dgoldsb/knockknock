"""
Used for reference:
- https://blog.apcelent.com/create-rest-api-using-aiohttp.html
- https://medium.com/@chimamireme/setting-up-a-modern-python-web-application-with-aiohttp-graphql-and-docker-149c52657142
"""

import json
import logging

from aiohttp.web import Request, Response
from sqlalchemy import func

from models import Device, Sighting, session


LOGGER = logging.getLogger("endpoints")
LOGGER.setLevel(logging.INFO)


def encode(data):
    return json.dumps(data, indent=4).encode("utf-8")


async def devices_get(request: Request) -> Response:
    """
    ---
    summary: Get device
    description: This endpoint allows users to retrieve the devices that were registered in the KnockKnock backend
    tags:
    - Devices
    produces:
    - application/json
    responses:
        "200":
            description: Return all devices
    """
    LOGGER.info("Received %s request on %s", request.method, request.url)

    devices = session.query(Device).distinct()

    return Response(
        status=200,
        body=encode(
            {
                "devices": [device.to_json() for device in devices]
            }
        ),
        content_type="application/json",
    )


async def devices_post(request: Request) -> Response:
    """
    ---
    summary: Post device alias
    description: This endpoint allows users to store device aliases.
    tags:
    - Devices
    produces:
    - application/json
    parameters:
    - in: body
      name: body
      schema:
        type: object
        properties:
          alias:
            type: string
      description: A device alias to store in the KnockKnock backend
      required: true
    responses:
        "200":
            description: Device has been stored successfully, return device as it was persisted
        "400":
            description: Invalid ``alias`` parameter or unable to parse the request body
        "500":
            description: An existing record was found, but the data model is malformed
    """
    LOGGER.info("Received %s request on %s", request.method, request.url)

    # Try to parse the Request body.
    try:
        data = await request.json()
        device = Device(
            alias=data["alias"]
        )
    except BaseException as e:
        return Response(status=400, reason=f"Unable to parse body ({e})")
    
    # Check if the device has been sighted before.
    existing_device = session.query(Device).filter(Device.alias == device.alias)
    try:
        LOGGER.info("Found existing Device %s", device.alias)
        return Response(
            status=200,
            body=encode(existing_device[0].to_json()),
            content_type="application/json",
        )
    except IndexError as _:
        LOGGER.info("Creating new Device %s", device.alias)
    except AttributeError as e:
        LOGGER.error(f"Existing device found, but the data model is malformed ({e})")
        return Response(status=500, reason=f"Data model is malformed ({e})")

    session.add(device)
    session.commit()

    new_device = session.query(Device).filter(
        Device.alias == device.alias
    )

    return Response(
        status=200,
        body=encode(new_device[0].to_json()),
        content_type="application/json",
    )

# TODO: device_update

# TODO: knock_get


async def sightings_get(request: Request) -> Response:
    """
    ---
    summary: Get device sighting
    description: This endpoint allows users to retrieve sightings of devices on the local network.
    tags:
    - Sightings
    produces:
    - application/json
    parameters:
    - in: query
      name: from
      schema:
        type: integer
      description: The epoch timestamp (seconds) from which to query sightings
      required: true
    - in: query
      name: to
      schema:
        type: integer
      description: The epoch timestamp (seconds) until which to query sightings
      required: false
    responses:
        "200":
            description: Return sightings that match the period query
        "400":
            description: Invalid ``from`` parameter or unable to parse the request body
    """
    LOGGER.info("Received %s request on %s", request.method, request.url)

    # Try to decode the JSON payload.
    try:
        request_body = await request.json()
    except BaseException as e:
        return Response(status=400, reason=f"Could not parse Request ({e})")

    # Get the ``from``, this is a required parameter.
    try:
        datetime_from = int(request_body["from"])
    except BaseException as e:
        return Response(status=400, reason=f"Did not find valid `from` parameter in Request, which is required ({e})")

    # Try to get the ``to``, this is optional and will default to an open window.
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

    return Response(
        status=200,
        body=encode(
            {
                "sightings": [{"alias": sighting.alias, "last_activity_timestamp": sighting.last_activity_timestamp} for sighting in sightings]
            }
        ),
        content_type="application/json",
    )


async def sightings_post(request: Request) -> Response:
    """
    ---
    summary: Post device sighting
    description: This endpoint allows users to store sightings of devices on the local network.
    tags:
    - Sightings
    produces:
    - application/json
    parameters:
    - in: body
      name: body
      schema:
        type: object
        properties:
          timestamp:
            type: integer
            format: int64
          alias:
            type: string
      description: A sighting to store in the KnockKnock backend
      required: true
    responses:
        "200":
            description: Sighting has been stored successfully, return sighting as it was persisted
        "400":
            description: Invalid ``from`` parameter or unable to parse the request body
    """
    LOGGER.info("Received %s request on %s", request.method, request.url)

    # Try to parse the Request body.
    try:
        data = await request.json()
        sighting = Sighting(
            alias=data["alias"], last_activity_timestamp=data["timestamp"]
        )
    except BaseException as e:
        return Response(status=400, reason=f"Unable to parse body ({e})")

    session.add(sighting)
    session.commit()

    records = session.query(Sighting).filter(
        Sighting.id == session.query(func.max(Sighting.id))
    )

    return Response(
        status=200,
        body=encode(records[0].to_json()),
        content_type="application/json",
    )
