from flask import Flask
from api import endpoints

app = Flask(__name__)

app.register_blueprint(endpoints)

if __name__ == '__main__':
    app.run()