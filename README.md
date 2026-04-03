# Aspire TS Micro Template

An Aspire template for a Python-based microservices solution orchestrated using TypeScript and Node.js.

This GitHub template provides a starting point for building a modern web application featuring a React front-end, a Python/FastAPI back-end, and Redis caching. It uses `Microsoft Aspire` (via the Aspire CLI) to easily orchestrate and run the application locally.

## Prerequisites

Before you start, make sure you have the following installed on your machine:
- **Node.js**: Version 20.19.0+ or 22.13.0+
- **Docker Desktop**: Required for spinning up the Redis cache container locally.
- **Aspire CLI**: Used to build and orchestrate the microservices.
- **Python / uv**: The back-end microservice is built with Python, and uses `uv` for dependency management.

## Setup

Since this is a GitHub template, you can generate a new repository from it or clone it directly:

```bash
# Clone your newly created repository
git clone https://github.com/gorindev/aspire-ts-micro-template.git
cd aspire-ts-micro-template

# Remove the .git directory to start fresh
rm -rf .git

# Initialize a new git repository
git init
git add .
git commit -m "Initial commit from template"
```

Or create a new repo from this template using the following command:

```bash
# Clone your newly created repository
gh repo create <new-repo-name> --template gorindev/aspire-ts-micro-template --public --clone
```

## Usage

To run the application locally with all services (Frontend, Python API, Redis, and Gateway) orchestrated automatically:

```bash
# Navigate to the src directory
cd src

# Start the application using Aspire
aspire run
```

Running this command will start the Aspire dashboard, where you can easily monitor logs, traces, and metrics for all of your services. The dashboard will provide you with the URLs to access the application.

## Project Structure

The codebase is organized as follows:

- `src/apphost.ts`: The central Aspire orchestration file written in TypeScript. It defines the topology of the application, incorporating Redis, the Python weather service, the Vite frontend, and a YARP gateway.
- `src/frontend/`: A React + Vite front-end application.
- `src/services/weather/`: A Python-based back-end microservice using FastAPI and Uvicorn. It exposes a `/api/weatherforecast` endpoint and connects to Redis for caching.
- `src/services/weather-ai-outfit/`: A Python-based back-end microservice using FastAPI and Uvicorn. It exposes a `/api/weather-ai-outfit` endpoint and connects to Redis for caching.
- `src/aspire.config.json` / `src/package.json`: Configuration and script definitions for the orchestrator.

## Development

Here is how you can start coding and expand the template:

1. **Frontend Development**: Navigate to `src/frontend/`. You can continue adding React components. It proxies unknown routes natively through the Vite proxy or YARP gateway during development.
2. **Backend Development**: Navigate to `src/services/weather/`. The API is built with FastAPI. Add your Python logic in `main.py` and manage your dependencies using `uv` in `pyproject.toml`.
3. **Gateway Routing**: The `YARP` gateway is configured in `src/apphost.ts`. Currently, all requests prefixed with `/weather/api` are routed and transformed to the Python backend. If you add new microservices, make sure to add them to the `builder` in `apphost.ts` and set up their corresponding routes using `yarp.addRouteFromResource`.
4. **Caching**: Redis is provisioned automatically by Aspire via Docker Desktop. The Python weather service connects to it securely to cache API responses.
5. **AI Outfit Service**: Navigate to `src/services/weather-ai-outfit/`. The API is built with FastAPI. Add your Python logic in `main.py` and manage your dependencies using `uv` in `pyproject.toml`.

Make your changes in the respective sub-projects, and `aspire run` will often hot-reload your code for immediate feedback!

## License

This project is licensed under the terms of the license found in the `LICENSE` file.
