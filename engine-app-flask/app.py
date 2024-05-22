from flask import Flask, session
from flask_session import Session
import redis

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.StrictRedis(host='redis', port=6379)

Session(app)

@app.route('/')
def index():
    session['key'] = 'value'
    return "Session Example"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)