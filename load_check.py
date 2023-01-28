import asyncio
import copy
import uuid
from datetime import datetime

import aiohttp

headers = {"Content-Type": "application/json; charset=utf-8"}

timeout = aiohttp.ClientTimeout(total=60)

body = {
    "user": {
        "email": "user@example.com",
        "password": "string",
        "full_name": "string",
        "username": "string",
    }
}


async def post(url):
    async with aiohttp.ClientSession(timeout=timeout) as session:
        s = datetime.now()
        body_m = copy.deepcopy(body)
        body_m["user"]["email"] = "user" + str(uuid.uuid4()) + "@example.com"
        body_m["user"]["username"] = "user" + str(uuid.uuid4())
        async with session.post(url, headers=headers, json=body_m) as resp:
            time_taken = datetime.now() - s
            return resp.status, time_taken


async def get(url):
    async with aiohttp.ClientSession(timeout=timeout) as session:
        s = datetime.now()
        async with session.get(url, headers=headers) as resp:
            time_taken = datetime.now() - s
            return resp.status, time_taken


try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

coroutines = [post("http://localhost:8000/api/users") for i in range(500)]


results = loop.run_until_complete(asyncio.gather(*coroutines))

codes = {}
count = 0
for s, r in results:
    codes[s] = codes.get(s, 0) + 1
    if r.seconds > 2:
        count += 1

print(codes, count)
