from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from flask_restx import Api, Namespace, Resource

user = "main"
passw = ""
host = "34.175.123.19"
database = "hm"

app = Flask(__name__)

# Defining API key for authentication
api_key = "Capstone2023!"

# Define decorator for checking API key
def require_api_key(func):
    def wrapper(*args, **kwargs):
        provided_key = request.headers.get('X-API-KEY')
        if provided_key == api_key:
            return func(*args, **kwargs)
        else:
            return {'message': 'Invalid API key'}, 401
    return wrapper

app.config["SQLALCHEMY_DATABASE_URI"] = host

api = Api(app, version = '1.0',
    title = 'The famous REST API with FLASK!',
    description = """
        This RESTS API is an API to built with FLASK
        and FLASK-RESTX libraries
        """,
    contact = "gustavom@faculty.ie.edu",
    endpoint = "/api/v1"
)

def connect():
    db = create_engine(
    'mysql+pymysql://{0}:{1}@{2}/{3}' \
        .format(user, passw, host, database), \
    connect_args = {'connect_timeout': 10})
    conn = db.connect()
    return conn

def disconnect(conn):
    conn.close()

master = Namespace('master',
    description = 'All operations related to customers',
    path='/api/v1')
api.add_namespace(master)

@master.route("/master")
class get_all_users(Resource):
    @require_api_key 
    def get(self):
        conn = connect()
        select = """
            SELECT *
            FROM master
            LIMIT 10000;"""
        result = conn.execute(select).fetchall()
        disconnect(conn)
        return jsonify({'result': [dict(row) for row in result]})