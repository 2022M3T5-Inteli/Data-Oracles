from unicodedata import category
from flask_cors import CORS

from flask import Flask, jsonify, request


from modelo_geral import ModelTools
from modelos import LGBM_MODELO, SCALER, convert_single_input

import numpy as np

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


# @app.route('/<path:path>')
# def static_file(path):
#     return app.send_static_file("index2.html")


# @app.route("/api/knn/rat", methods=["POST", "OPTION"])
# # @cross_origin()
# def knn_rat():
#     input_json = request.get_json(force=True)
#     print(input_json)
#     input_x = convert_single_input(
#         input_json["data_hora"], input_json["feriado"], input_json["categoria"])
#     X = np.array([input_x])
#     X_transformed = ModelTools().transform_input(X, SCALER)

#     predict_rat_raw = KNN_MODELO.predict_rat(X_transformed)

#     predict_rat = ModelTools().parse_predict_rat(predict_rat_raw)

#     return_obj = {"predictions": predict_rat}

#     response = jsonify(return_obj)
#     response.headers.add("Access-Control-Allow-Origin", "*")
#     return response


# @app.route("/api/knn/share", methods=["POST"])
# def knn_share():
#     input_json = request.get_json(force=True)
#     input_x = convert_single_input(
#         input_json["data_hora"], input_json["feriado"], input_json["categoria"])
#     X = np.array([input_x])
#     X_transformed = ModelTools().transform_input(X, SCALER)

#     predict_share_raw = KNN_MODELO.predict_share(X_transformed)

#     predict_share = ModelTools().parse_predict_share(predict_share_raw)

#     return_obj = {"predictions": predict_share}
#     response = jsonify(return_obj)
#     response.headers.add("Access-Control-Allow-Origin", "*")
#     return response


# @app.route("/api/knn/fid", methods=["POST"])
# # @cross_origin()
# def knn_fid():
#     input_json = request.get_json(force=True)
#     input_x = convert_single_input(
#         input_json["data_hora"], input_json["feriado"], input_json["categoria"])
#     X = np.array([input_x])
#     X_transformed = ModelTools().transform_input(X, SCALER)

#     predict_fid_raw = KNN_MODELO.predict_fid(X_transformed)

#     predict_fid = ModelTools().parse_predict_fid(predict_fid_raw)

#     return_obj = {"predictions": predict_fid}
#     response = jsonify(return_obj)
#     response.headers.add("Access-Control-Allow-Origin", "*")

#     return response

@app.route("/api/lgbm/rat", methods=["POST", "OPTION"])
# @cross_origin()
def knn_rat():
    input_json = request.get_json(force=True)
    print(input_json)
    input_x = convert_single_input(
        input_json["data_hora"], input_json["feriado"], input_json["categoria"])
    X = np.array([input_x])

    predict_rat_raw_hour = LGBM_MODELO.predict_rat_hour(X)

    predict_rat = ModelTools().parse_predict_rat(predict_rat_raw_hour)

    return_obj = {"predictions": predict_rat}

    response = jsonify(return_obj)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/api/lgbm/share", methods=["POST"])
def knn_share():
    input_json = request.get_json(force=True)
    input_x = convert_single_input(
        input_json["data_hora"], input_json["feriado"], input_json["categoria"])
    X = np.array([input_x])
    predict_share_raw_hour = LGBM_MODELO.predict_share_hour(X)

    predict_share = ModelTools().parse_predict_share(predict_share_raw_hour)

    return_obj = {"predictions": predict_share}
    response = jsonify(return_obj)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


# @app.route("/api/lgbm/rat")
# def lgbm_rat():
#     return 'Rat lgbm'


# @app.route("/api/lgbm/share")
# def lgbm_share():
#     return 'Share lgbm'


# @app.route("/api/lgbm/fid")
# def lgbm_fid():
#     return 'Fid lgbm'


# @app.route("/api/rf/rat")
# def rf_rat():
#     return 'Rat rf'


# @app.route("/api/rf/share")
# def rf_share():
#     return 'Share rf'


# @app.route("/api/rf/fid")
# def rf_fid():
#     return 'Fid rf'
