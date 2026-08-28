from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.responses import JSONResponse
import redis

from serving.realtime.db import get_all_vehicles, get_route_health, get_network_health
from serving.realtime.db import get_redis_client

app = FastAPI(title="GTFS Realtime Analytics API")
Instrumentator().instrument(app).expose(app)

@app.get("/api/vehicles")
def fetch_vehicles():
    return {"data": get_all_vehicles(), "source": "redis"}

@app.get("/api/route-health")
def fetch_route_health():
    return {"data": get_route_health(), "source": "redis"}

@app.get("/api/network-health")
def fetch_network_health():
    return {"data": get_network_health(), "source": "redis"}


@app.get("/health")
def health_check():
    try:
        get_redis_client().ping()
    except redis.RedisError as error:
        return JSONResponse(status_code=503, content={"status": "unavailable", "detail": str(error)})
    return {"status": "ok", "redis": "ok"}