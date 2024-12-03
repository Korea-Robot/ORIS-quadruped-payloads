from fastapi import APIRouter, BackgroundTasks, HTTPException
from models import StreamUrls
from inference.yolo_inference import yolo_inference
# from inference.multiprocessing_inference import yolo_inference
from typing import List, Dict, Any
from config.config import config 


router = APIRouter(
    prefix="/api/inference",  # This sets the base path for the routes
)

@router.post("/start")
async def start_yolo(stream_urls: StreamUrls, background_tasks: BackgroundTasks):
    already_running_streams = [
        url for url in stream_urls.stream_urls 
        if url in yolo_inference.streams and yolo_inference.streams[url]["running"]
    ]
    
    new_streams = [url for url in stream_urls.stream_urls if url not in already_running_streams]

    if new_streams:
        for stream in new_streams:
            background_tasks.add_task(yolo_inference.start_stream, stream)
        return {
            "status": "YOLO inference started", 
            "streams": stream_urls.stream_urls, 
            "already_running": already_running_streams
        }
    else:
        return {
            "status": "All requested streams are already being inferred", 
            "streams": stream_urls.stream_urls, 
            "already_running": already_running_streams
        }
@router.post("/stop")
async def stop_yolo(stream_urls: StreamUrls):
    running_streams_to_stop = [url for url in stream_urls.stream_urls if url in yolo_inference.streams and yolo_inference.streams[url]["running"]]
    not_running_streams = [url for url in stream_urls.stream_urls if url not in running_streams_to_stop]

    if running_streams_to_stop:
        yolo_inference.stop(running_streams_to_stop)
        return {"status": "YOLO inference stopped for requested streams", "stopped_streams": running_streams_to_stop, "not_running_streams": not_running_streams}
    else:
        return {"status": "None of the requested streams were running", "streams": stream_urls.stream_urls, "not_running_streams": not_running_streams}
