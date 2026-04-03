import { createBuilder, GitHubModelName } from './.modules/aspire.js';

const builder = await createBuilder();

// Parameters
var apiKey = await builder
    .addParameter("github-api-key", { secret: true });

// Infrastructure
var ai = await builder
    .addGitHubModel("ai", GitHubModelName.OpenAIGpt4oMini)
    .withApiKey(apiKey);

const cache = await builder
    .addRedis("cache");

// Services
const weather = await builder
    .addUvicornApp("weather", "./services/weather", "main:app")
    .withUv()
    .withReference(cache)
    .waitFor(cache)
    .withHttpsEndpoint();

const weatherAiOutfit = await builder
    .addUvicornApp("weather-ai-outfit", "./services/weather-ai-outfit", "main:app")
    .withUv()
    .withReference(ai)
    .waitFor(ai)
    .withHttpsEndpoint();

// Frontend
const frontend = await builder
    .addViteApp("frontend", "./frontend")
    .withExternalHttpEndpoints();

// Gateway
var gateway = await builder
    .addYarp("gateway")
    .withConfiguration(async yarp => {
        // Services
        yarp.addRouteFromResource("/weather/api/{**catch-all}", weather)
            .withTransformPathRemovePrefix("/weather");

        yarp.addRouteFromResource("/weather-ai-outfit/api/{**catch-all}", weatherAiOutfit)
            .withTransformPathRemovePrefix("/weather-ai-outfit");

        // Frontend
        const context = await builder.executionContext.get();
        if (await context.isRunMode.get()) {
            // In dev mode, proxy all other requests to Vite dev server
            yarp.addRouteFromResource("{**catch-all}", frontend);
        }
    })
    .withHttpsEndpoint()
    .withExternalHttpEndpoints();

await frontend.withReference(gateway).waitFor(gateway);
await gateway.publishWithStaticFiles(frontend);

await builder.build().run();
