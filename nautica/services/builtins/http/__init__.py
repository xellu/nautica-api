from . import router, server
from ....manager import Config, ConfigBuilder

Config.Update(
    "nautica", ConfigBuilder()
        .add("http.host", "127.0.0.1", comment="Use 0.0.0.0 to expose your app, 127.0.0.1 to keep local")
        .add("http.port", 8100, comment="Port to host the app on, by default is set to 8100")
        .add("http.realIPHeader", "", comment="Name of the header which has the real ip, e.g. X-Real-IP, CF-Connecting-IP (if behind proxy), set to empty to use requesting machine's IP instead")
        .build()
)