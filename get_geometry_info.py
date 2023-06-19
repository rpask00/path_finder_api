import asyncio

import aiohttp

from app import API_KEY


async def fetch_place(session, url):
    async with session.get(url) as response:
        return await response.json()


async def fetch_all_places(place_ids):
    url = "https://maps.googleapis.com/maps/api/place/details/json?key={}&place_id={}"

    tasks = []
    async with aiohttp.ClientSession() as session:
        for place_id in place_ids:
            task = fetch_place(session, url.format(API_KEY, place_id))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        return responses


# def get_places_details(place_ids):
#     loop = asyncio.get_event_loop()
#     places_details = loop.run_until_complete(fetch_all_places(place_ids))
#     return places_details
