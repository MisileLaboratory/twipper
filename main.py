from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pyyoutube import Video
from pyyoutube import Api as yapi
from requests import get
from tomli import loads
from json import loads as jloads
from misilelibpy import read_once
from asyncio import sleep

config = loads(read_once("config.toml"))
web = FastAPI()
youtubeapi = yapi(api_key=config["youtube"]["key"])
client = MongoClient(host=config["db"]["host"], port=config["db"]["port"], user=config["db"]["user"], password=config["db"]["password"])
cooltimes = {}

@web.post("/post/{videoid}")
async def post_streamer(videoid: str, myid: str):
    video: Video = youtubeapi.get_video_by_id(video_id=videoid).items[0] # type: ignore
    try:
        cooltimes[f"{myid}-{videoid}"]
    except KeyError:
        cooltimes[f"{myid}-{videoid}"] = 0
    else:
        raise HTTPException(status_code=429)
    if video.snippet.liveBroadcastContent != "live": # type: ignore
        raise HTTPException(status_code=404)
    if client.get_database("twipper").get_collection(video.snippet.channelId) == None: # type: ignore
        table = client.get_database("twipper").create_collection(video.snippet.channelId) # type: ignore
    else:
        table = client.get_database("twipper").get_collection(video.snippet.channelId) # type: ignore
    if table.find_one(filter={"id": myid}) is None:
        table.insert_one({"id": myid, "point": 0})
    p = table.find_one(filter={"id": myid})["point"] # type: ignore
    table.find_one_and_replace(filter={"id": myid}, replacement={"id": myid, "point": p + config["point"]["view"]})
    await sleep(600)
    del cooltimes[f"{myid}-{videoid}"]

