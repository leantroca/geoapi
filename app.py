from flask import Flask

from api import blueprint
from etc.config import settings

app = Flask(__name__)

app.register_blueprint(blueprint)

if __name__ == "__main__":
    app.run(
        host=settings.LISTEN_TO,
        port=settings.PORT,
        debug=settings.DEBUG,
    )
