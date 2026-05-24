from ...manager import Config, ConfigBuilder

Config.Update(
    "nautica", ConfigBuilder()
        .add("services.http", True, "Enables the HTTP Server service")
        .build()
)