from flask import Flask
from config import Config

app = Flask(__name__)

app.config.from_object(Config)
@app.route('/index')
def index():
    return 'index'

if __name__ == '__main__':
    app.run(debug=True)