from flask import Flask, request, jsonify, send_from_directory, session, make_response
from flask_cors import CORS
import os

app = Flask(__name__)

# ✅ CORS manuell erlauben
CORS(app, supports_credentials=True, origins=["https://jolly-sundae-12badf.netlify.app"])

app.secret_key = "super_secret_key"

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# 🔥 CORS-Preflight-Requests richtig behandeln
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "https://jolly-sundae-12badf.netlify.app")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS, DELETE")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response


@app.route("/login", methods=["POST"])
def login():
    password = request.json.get("password")
    if password == "admin":
        session["admin"] = True
        return corsify_response(jsonify({"message": "Login erfolgreich"}))
    return corsify_response(jsonify({"error": "Falsches Passwort"}), 401)


@app.route("/files", methods=["GET"])
def list_files():
    if not session.get("admin"):
        return corsify_response(jsonify({"error": "Nicht autorisiert"}), 403)

    items = os.listdir(UPLOAD_FOLDER)
    folders = [item for item in items if os.path.isdir(os.path.join(UPLOAD_FOLDER, item))]
    files = [item for item in items if os.path.isfile(os.path.join(UPLOAD_FOLDER, item))]

    return corsify_response(jsonify({"folders": folders, "files": files}))


@app.route("/upload", methods=["POST"])
def upload_file():
    if not session.get("admin"):
        return corsify_response(jsonify({"error": "Nicht autorisiert"}), 403)

    files = request.files.getlist("files")
    for file in files:
        if file.filename:
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))

    return corsify_response(jsonify({"message": "Upload erfolgreich"}))


@app.route("/create_folder", methods=["POST"])
def create_folder():
    if not session.get("admin"):
        return corsify_response(jsonify({"error": "Nicht autorisiert"}), 403)

    folder_name = request.json.get("folder_name", "").strip()
    if folder_name:
        folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    return corsify_response(jsonify({"message": "Ordner erstellt"}))


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("admin", None)
    return corsify_response(jsonify({"message": "Logout erfolgreich"}))


# ✅ Antwort mit CORS-Headern zurückgeben
def corsify_response(response):
    response.headers.add("Access-Control-Allow-Origin", "https://jolly-sundae-12badf.netlify.app")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
