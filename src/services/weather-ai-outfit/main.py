import contextlib
import logging
import os
from openai import AsyncOpenAI

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

def parse_ai_conn_string(conn_str):
    if not conn_str:
        return None, None
    parts = conn_str.split(';')
    endpoint = None
    key = None
    for part in parts:
        if '=' in part:
            k, v = part.split('=', 1)
            if k.strip().lower() == 'endpoint':
                endpoint = v.strip()
            elif k.strip().lower() == 'key':
                key = v.strip()
    return endpoint, key

ai_conn_str = os.getenv("ConnectionStrings__ai")
endpoint, key = parse_ai_conn_string(ai_conn_str)

ai_client = None
if endpoint and key:
    try:
        ai_client = AsyncOpenAI(
            base_url=endpoint,
            api_key=key,
        )
    except Exception as e:
        logger.error(f"Failed to connect to AI: {e}")
elif ai_conn_str:
    logger.warning("ConnectionStrings__ai format is unexpected.")
else:
    logger.warning("ConnectionStrings__ai environment variable is missing!")


@app.post("/api/suggest-outfit")
async def suggest_outfit(request: fastapi.Request):
    """Suggest outfit endpoint."""
    weather_data = "Unknown weather"
    try:
        body = await request.json()
        weather_data = body.get("weather", weather_data)
    except Exception:
        pass

    if not ai_client:
        return fastapi.responses.PlainTextResponse("AI client not available", status_code=503)

    try:
        response = await ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful fashion assistant indicating the best outfit based on weather forecast. Make your response concise."},
                {"role": "user", "content": f"The weather forecast is: {weather_data}. What should I wear?"}
            ],
            max_tokens=150
        )
        return fastapi.responses.PlainTextResponse(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"AI prediction failed: {e}")
        return fastapi.responses.PlainTextResponse("Failed to generate outfit suggestion", status_code=500)


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
