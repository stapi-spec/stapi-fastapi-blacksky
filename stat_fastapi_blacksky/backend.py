import os
from fastapi import Request
import requests

from stat_fastapi.exceptions import NotFoundException
from stat_fastapi.models.opportunity import (
    Opportunity,
    OpportunityRequest,
)
from stat_fastapi.models.order import Order
from stat_fastapi.models.product import Product, Provider, ProviderRole

from stat_fastapi_blacksky.settings import Settings
from stat_fastapi_blacksky.models import Constraints


BLACKSKY_BASE_URL = "https://api.sit.blacksky.com/v1"


PRODUCTS = [
    Product(
        id="BS-Test:Standard",
        description="BS-Test standard product",
        license="proprietary",
        providers=[
            Provider(
                name="Blacksky",
                roles=[
                    ProviderRole.licensor,
                    ProviderRole.producer,
                    ProviderRole.processor,
                    ProviderRole.host,
                ],
                url="https://www.blacksky.com/",
            )
        ],
        parameters=Constraints,
        links=[],
    ),
]


def stat_to_oppurtunities_request(search: OpportunityRequest):
    """
    :param search_request: STAC search as passed on to find_future_items
    :return: a triple of iw request body, geom and bbox (geom and bbox needed again later to construct STAC answers)
    """
    bbs_number, bs_product = search.product_id.split(":")

    return {
        "item": {
            "name": "Blacksky_Request",
            "description": "STAT Sprint 3",
            "timeframe": {
                "lowerBoundType": "CLOSED",
                "lowerEndpoint": search.datetime[0].isoformat(),
                "upperBoundType": "CLOSED",
                "upperEndpoint": search.datetime[1].isoformat(),
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    search.geometry.model_dump()["coordinates"][0],
                    search.geometry.model_dump()["coordinates"][1],
                    0,
                ],
            },
            "frequency": "ONCE",
            "offeringId": "391327b7-f4ee-4e7f-a894-3cffef19cae0",
            "frequency": "ONCE",
            "offeringParamValues": {"priority": "STANDARD", "sensor": "blacksky"},
            "externalId": "1234",
        },
    }

def get_oppurtunities(blacksky_request: dict, token: str):
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "authorization": token,
    }

    r = requests.post(
        f"{BLACKSKY_BASE_URL}/feasibility/plan", headers=headers, json=blacksky_request
    )
    return r.json()["opportunities"]


def blacksky_oppurtunity_to_opportunity(iw: dict):
    """
    translates a Planet Imaging Windows into a STAT opportunity
    :param iw: an element from the 'imaging_windows' array of a /imaging_windows/[search_id] response
    :return: a corresponding STAT opportunity
    """

    opportunity = Opportunity(
        id=iw["satellite"],
        geometry={"type": "Point", "coordinates": [iw["longitude"], iw["latitude"], 0]},
        properties=dict(
            product_id="BS-Test:Standard",
            datetime=f"{iw['timestamp']}/{iw['timestamp']}",
            off_nadir=iw["offNadirAngleDegrees"],
        ),
    )

    return opportunity


class StatBlackskyBackend:

    def __init__(self):
        settings = Settings.load()

    def products(self, request: Request) -> list[Product]:
        """
        Return a list of supported products.
        """
        return PRODUCTS

    def product(self, product_id: str, request: Request) -> Product | None:
        """
        Return the product identified by `product_id` or `None` if it isn't
        supported.
        """
        try:
            return next((product for product in PRODUCTS if product.id == product_id))
        except StopIteration as exc:
            raise NotFoundException() from exc

    async def search_opportunities(
        self, search: OpportunityRequest, request: Request
    ) -> list[Opportunity]:
        """
        Search for ordering opportunities for the given search parameters.
        """
        token = os.environ.get("BACKEND_TOKEN")
        if authorization := request.headers.get("authorization"):
            token = authorization.replace("Bearer ", "")
                
        blacksky_request = stat_to_oppurtunities_request(search)
        oppurtunities = get_oppurtunities(blacksky_request, token)
        return [blacksky_oppurtunity_to_opportunity(iw) for iw in oppurtunities]

    async def create_order(self, search: OpportunityRequest, request: Request) -> Order:
        """
        Create a new order.
        """
        raise NotImplementedError()

    async def get_order(self, order_id: str, request: Request):
        """
        Show details for order with `order_id`.
        """
        raise NotImplementedError()
