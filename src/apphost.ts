import { createBuilder } from './.modules/aspire.js';

const builder = await createBuilder();

// Infrastructure
const cache = await builder
    .addRedis("cache");

// Services
const weather = await builder
    .addUvicornApp("weather", "./services/weather", "main:app")
    .withUv()
    .withReference(cache)
    .waitFor(cache)
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
