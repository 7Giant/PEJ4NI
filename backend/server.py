from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
import os

app = Flask(__name__)

# ✅ CORS vollständig erlauben für Netlify & Preflight-Requests
CORS(app, supports_credentials=True, origins=["https://jolly-sundae-12badf.netlify.app"])

app.secret_key = "super_secret_key"

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/login", methods=["OPTIONS", "POST"])
def login():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()

    password = request.json.get("password")
    if password == "admin":
        session["admin"] = True
        return _corsify_actual_response(jsonify({"message": "Login erfolgreich"}))
    return _corsify_actual_response(jsonify({"error": "Falsches Passwort"}), 401)


@app.route("/files", methods=["OPTIONS", "GET"])
def list_files():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()

    if not session.get("admin"):
        return _corsify_actual_response(jsonify({"error": "Nicht autorisiert"}), 403)

    items = os.listdir(UPLOAD_FOLDER)
    folders = [item for item in items if os.path.isdir(os.path.join(UPLOAD_FOLDER, item))]
    files = [item for item in items if os.path.isfile(os.path.join(UPLOAD_FOLDER, item))]

    return _corsify_actual_response(jsonify({"folders": folders, "files": files}))


@app.route("/upload", methods=["OPTIONS", "POST"])
def upload_file():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()

    if not session.get("admin"):
        return _corsify_actual_response(jsonify({"error": "Nicht autorisiert"}), 403)

    files = request.files.getlist("files")
    for file in files:
        if file.filename:
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))

    return _corsify_actual_response(jsonify({"message": "Upload erfolgreich"}))


@app.route("/create_folder", methods=["OPTIONS", "POST"])
def create_folder():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()

    if not session.get("admin"):
        return _corsify_actual_response(jsonify({"error": "Nicht autorisiert"}), 403)

    folder_name = request.json.get("folder_name", "").strip()
    if folder_name:
        folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    return _corsify_actual_response(jsonify({"message": "Ordner erstellt"}))


@app.route("/logout", methods=["OPTIONS", "POST"])
def logout():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()

    session.pop("admin", None)
    return _corsify_actual_response(jsonify({"message": "Logout erfolgreich"}))


# 🚀 CORS-Helper-Funktionen, um ALLE Anfragen richtig zu behandeln
def _build_cors_preflight_response():
    response = jsonify({"message": "CORS preflight successful"})
    response.headers.add("Access-Control-Allow-Origin", "https://jolly-sundae-12badf.netlify.app")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS, DELETE")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response


def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "https://jolly-sundae-12badf.netlify.app")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
