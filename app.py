import os

from flask import Flask, render_template, request
from flask_swagger_ui import get_swaggerui_blueprint

from engine import Indexer, Query, QueryParser, connect_db
from utils import data_response, error_response

app = Flask(__name__)

idx = Indexer()
query_engine = Query()

# Build inverted list if not exists
if not os.path.exists("shakespeares.db"):
    idx.build_inverted_list()


con = connect_db()


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/search", methods=["GET"])
def search():
    raw_query = request.args.get("query", "")
    if raw_query == "":
        return data_response([])
    else:
        parser = QueryParser(raw_query)
        query_ast = parser.parse_ast()
        filter_scenes = query_engine.boolean_filter(con, idx, query_ast)
        rankings = query_engine.bm25(con, idx, parser.tokens, filter_scenes)
        return data_response(list(rankings.keys()))


SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.yaml"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Shakespeares Search Engine"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
