from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pyyoutube import Video
from pyyoutube import Api as yapi
from requests import get, post
from requests.sessions import Request
from tomli import loads
from tomli_w import dumps
from misilelibpy import read_once, write_once
from asyncio import sleep
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

config = loads(read_once("config.toml"))
youtubeapi = yapi(api_key=config["youtube"]["key"])
client = MongoClient(host=config["db"]["host"], port=config["db"]["port"], user=config["db"]["user"], password=config["db"]["password"])
cooltimes = {}

web = FastAPI()
limiter = Limiter(key_func=get_remote_address)
web.state.limiter = limiter
web.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@web.post("/post/{videoid}")
async def post_streamer(pvideoid: str, myid: str)
    video: Video = youtubeapi.get_video_by_id(video_id=pvideoid).items[0] # type: ignore
    videoid: str = video.snippet.channelId # type: ignore
    myid = client.get_database("twipper").get_collection("user").find_one(filter={"yid": myid}) # type: ignore
    stid = client.get_database("twipper").get_collection("user").find_one(filter={"yid": videoid}) # type: ignore
    if myid is None or stid is None or video is None or videoid is None:
        raise HTTPException(status_code=404)
    try:
        cooltimes[f"{myid['id']}-{videoid}"] # type: ignore
    except KeyError:
        cooltimes[f"{myid['id']}-{videoid}"] = 0 # type: ignore
    else:
        raise HTTPException(status_code=429)
    if video.snippet.liveBroadcastContent != "live": # type: ignore
        raise HTTPException(status_code=404)
    if client.get_database("twipper").get_collection(stid["id"]) is None: # type: ignore
        table = client.get_database("twipper").create_collection(stid["id"]) # type: ignore
    else:
        table = client.get_database("twipper").get_collection(stid["id"]) # type: ignore
    if table.find_one(filter={"id": myid["id"]}) is None: # type: ignore
        table.insert_one({"id": myid["id"], "point": 0}) # type: ignore
    p = table.find_one(filter={"id": myid["id"]})["point"] # type: ignore
    table.find_one_and_replace(filter={"id": myid}, replacement={"id": myid, "point": p + config["point"]["view"]})
    await sleep(600)
    del cooltimes[f"{myid}-{videoid}"]

@web.get("/get/point/{streamerid}")
@limiter.limit("6000/hour")
async def get_point(request: Request, streamerid: str, userid: str):
    streamer = client.get_database("twipper").get_collection("user").find_one(filter={"streamer": True, "id": streamerid})
    if streamer is None:
        raise HTTPException(status_code=404)
    stid = client.get_database("twipper").get_collection(streamer["id"]).find_one(filter={"id": userid})
    if stid is None:
        raise HTTPException(status_code=404)
    a = client.get_database("twipper").get_collection(streamer["id"]).find_one(filter={"id": userid})
    if a is None:
        raise HTTPException(status_code=404)
    return a["point"]

@web.get("/get/user/{userid}")
@limiter.limit("60/minute")
async def get_universal_id(request: Request, userid: str, twitch: bool):
    if twitch:
        a = client.get_database("twipper").get_collection("user").find_one(filter={"tid": userid})
    else:
        a = client.get_database("twipper").get_collection("user").find_one(filter={"yid": userid})
    if a is not None:
        return a
    raise HTTPException(status_code=404)

# I will make it
def divide_elements(l: list, n: int = 100):
    return []

async def main():
    c = loads(read_once("config.toml"))
    key = c.get("key", None)
    if key is None:
        c["twitch"]["key"] = post(f"https://id.twitch.tv/oauth2/token?client_id={c['id']}&client_secret={c['key']}&grant_type=client_credentials").json()["access_token"]
        write_once("config.toml", dumps(c))
        key = c["twitch"]["key"]
    while True:
        streamers = list(client.get_database("twipper").get_collection("user").find(filter={"streamer": True}))
        streamers = [x for x in streamers if x["tid"] is not None]
        lstreamers = []
        for i in divide_elements(lstreamers):
            response = get("https://api.twitch.tv/helix/streams", params={"user_login": streamers}, headers={"Authorization": f"Bearer {key}", "Client-id": c["twitch"]["id"]})
            # TODO: get some live streamer
        # TODO: check_and_insert()
        await sleep(600)

