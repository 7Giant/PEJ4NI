from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = "super_secret_key"

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# 🏠 Admin-Login
@app.route("/login", methods=["POST"])
def login():
    password = request.json.get("password")
    if password == "admin":
        session["admin"] = True
        return jsonify({"message": "Login erfolgreich"}), 200
    return jsonify({"error": "Falsches Passwort"}), 401


# 🏠 Datei-Manager (nur für Admin)
@app.route("/files", methods=["GET"])
def list_files():
    if not session.get("admin"):
        return jsonify({"error": "Nicht autorisiert"}), 403

    items = os.listdir(UPLOAD_FOLDER)
    folders = [item for item in items if os.path.isdir(os.path.join(UPLOAD_FOLDER, item))]
    files = [item for item in items if os.path.isfile(os.path.join(UPLOAD_FOLDER, item))]

    return jsonify({"folders": folders, "files": files})


# 📤 Datei hochladen (Mehrere Dateien & Drag & Drop)
@app.route("/upload", methods=["POST"])
def upload_file():
    if not session.get("admin"):
        return jsonify({"error": "Nicht autorisiert"}), 403

    if "files" not in request.files:
        return jsonify({"error": "Keine Datei ausgewählt"}), 400

    files = request.files.getlist("files")
    for file in files:
        if file.filename:
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))

    return jsonify({"message": "Upload erfolgreich"})


# 📂 Ordner erstellen
@app.route("/create_folder", methods=["POST"])
def create_folder():
    if not session.get("admin"):
        return jsonify({"error": "Nicht autorisiert"}), 403

    folder_name = request.json.get("folder_name", "").strip()
    if folder_name:
        folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    return jsonify({"message": "Ordner erstellt"})


# 📂 Datei herunterladen
@app.route("/download/<filename>")
def download_file(filename):
    if not session.get("admin"):
        return jsonify({"error": "Nicht autorisiert"}), 403

    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)


# ❌ Datei löschen
@app.route("/delete/<filename>", methods=["DELETE"])
def delete_file(filename):
    if not session.get("admin"):
        return jsonify({"error": "Nicht autorisiert"}), 403

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return jsonify({"message": "Datei gelöscht"})


# ❌ Ordner löschen
@app.route("/delete_folder", methods=["DELETE"])
def delete_folder():
    if not session.get("admin"):
        return jsonify({"error": "Nicht autorisiert"}), 403

    folder_name = request.json.get("folder_name")
    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
    if os.path.exists(folder_path):
        os.rmdir(folder_path)

    return jsonify({"message": "Ordner gelöscht"})


# 🚪 Logout
@app.route("/logout", methods=["POST"])
def logout():
    session.pop("admin", None)
    return jsonify({"message": "Logout erfolgreich"})


# 🔥 Server starten
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
