import contextlib
import datetime
import json
import logging
import os
import random
import redis.asyncio as redis

import fastapi
import fastapi.responses
import fastapi.staticfiles
import opentelemetry.instrumentation.fastapi as otel_fastapi
import telemetry


@contextlib.asynccontextmanager
async def lifespan(app):
    telemetry.configure_opentelemetry()
    yield


app = fastapi.FastAPI(lifespan=lifespan)
otel_fastapi.FastAPIInstrumentor.instrument_app(app, exclude_spans=["send"])


logger = logging.getLogger(__name__)
def parse_redis_conn_string(conn_str):
    if not conn_str:
        return None
    if any(conn_str.startswith(s) for s in ["redis://", "rediss://", "unix://"]):
        return conn_str
    
    # Handle StackExchange.Redis format: host:port,password=...,ssl=...
    parts = conn_str.split(',')
    host_port = parts[0]
    options = {}
    for part in parts[1:]:
        if '=' in part:
            k, v = part.split('=', 1)
            options[k.strip().lower()] = v.strip()
            
    scheme = "rediss" if options.get("ssl") == "true" else "redis"
    password = options.get("password", "")
    auth = f":{password}@" if password else ""
    return f"{scheme}://{auth}{host_port}"

redis_url = parse_redis_conn_string(os.getenv("ConnectionStrings__cache"))

if not redis_url:
    logger.warning("ConnectionStrings__cache environment variable is missing!")
    cache = None
else:
    try:
        # Note: Using redis.asyncio, not using hiredis as requested
        cache = redis.from_url(redis_url, decode_responses=True)
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        cache = None


if not os.path.exists("static"):
    @app.get("/", response_class=fastapi.responses.HTMLResponse)
    async def root():
        """Root endpoint."""
        return "API service is running. Navigate to <a href='/api/weatherforecast'>/api/weatherforecast</a> to see sample data."

@app.get("/api/weatherforecast")
async def weather_forecast():
    """Weather forecast endpoint."""
    cache_key = "weather_forecast"
    
    if cache:
        try:
            cached_data = await cache.get(cache_key)
            if cached_data:
                logger.info("Returning cached forecast")
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Error reading from cache: {e}")

    # Generate fresh data
    summaries = [
        "Freezing",
        "Bracing",
        "Chilly",
        "Cool",
        "Mild",
        "Warm",
        "Balmy",
        "Hot",
        "Sweltering",
        "Scorching",
    ]

    forecast = []
    for index in range(1, 6):  # Range 1 to 5 (inclusive)
        temp_c = random.randint(-20, 55)
        forecast_date = datetime.datetime.now() + datetime.timedelta(days=index)
        forecast_item = {
            "date": forecast_date.isoformat(),
            "temperatureC": temp_c,
            "temperatureF": int(temp_c * 9 / 5) + 32,
            "summary": random.choice(summaries),
        }
        forecast.append(forecast_item)

    if cache:
        try:
            # Store in cache for 60 seconds
            await cache.set(cache_key, json.dumps(forecast), ex=60)
            logger.info("Stored new forecast in cache")
        except Exception as e:
            logger.error(f"Error writing to cache: {e}")

    return forecast


@app.get("/health", response_class=fastapi.responses.PlainTextResponse)
async def health_check():
    """Health check endpoint."""
    return "Healthy"


# Serve static files directly from root, if the "static" directory exists
if os.path.exists("static"):
    app.mount(
        "/",
        fastapi.staticfiles.StaticFiles(directory="static", html=True),
        name="static"
    )
