from flask import Flask, request, jsonify, send_file, Response, stream_with_context, make_response
from flask_cors import CORS
import os
import time
import json
import shutil
from flask_limiter import Limiter
from server.querying_graph.pipeline import Pipeline
from server.utils import make_file_path, undo_file_path

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, methods=["GET", "POST", "DELETE", "OPTIONS", "PUT"])
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  
limiter = Limiter(app)

@limiter.limit("10 per minute")
@app.route("/api/clients/<client_id>/files", methods=["POST"])
def upload_file(client_id):
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    file_id = request.form.get('id')
    description = request.form.get('description') or None
    tags = request.form.get('tags') or None

    if not file or not file.filename:
        return jsonify({"error": "No selected file"}), 400

    valid_files = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv', '.json', '.geojson', '.geo.json'}
    if not any(file.filename.endswith(ft) for ft in valid_files):
        return jsonify({"error": "Invalid file type"}), 400

    upload_folder = os.path.join("server/uploads", client_id)
    os.makedirs(upload_folder, exist_ok=True)

    for existing_file in os.listdir(upload_folder):
        if file.filename in undo_file_path(existing_file):
            return jsonify({"error": f"File named {file.filename} already exists."}), 409
    file_name = make_file_path(file.filename, file_id)
    file_path = os.path.join(upload_folder, file_name)

    try:
        file.save(file_path)
    except Exception as e:
        return jsonify({"error": f"Failed to save file: {e}"}), 500

    metadata = {'description': description, 'tags': tags, 'id': file_id}
    with open(f"{file_path}.meta.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return jsonify({"success": True, "filename": file_name}), 201

@app.route("/api/clients/<client_id>/files/<file_id>", methods=["DELETE"])
def delete_file(client_id, file_id):
    if request.method == "OPTIONS":
        # Handle preflight request
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response.headers["Access-Control-Allow-Methods"] = "DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response, 200

    data = request.get_json()
    file_name = data.get("file")

    if not file_name or not file_id:
        return jsonify({"error": "Missing filename or ID"}), 400
    upload_folder = os.path.join("server/uploads", client_id)
    full_path = os.path.join(upload_folder, file_name)

    try:
        os.remove(full_path)
        os.remove(f"{full_path}.meta.json")
    except Exception as e:
        return jsonify({"error": f"Failed to delete: {e}"}), 500

    return jsonify({"success": True, "file_name": file_name, 'id': file_id}), 200

@app.route("/api/clients/<client_id>/files", methods=["GET"])
def get_uploaded_files(client_id):
    upload_folder = os.path.join("server/uploads", client_id)
    if not os.path.exists(upload_folder):
        return jsonify({"success":"no files to retrieve"}), 200

    uploaded_files = []
    for filename in os.listdir(upload_folder):
        if filename.endswith(".meta.json"):
            continue
        meta_path = os.path.join(upload_folder, f"{filename}.meta.json")
        tag_list = None
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                tags = metadata.get("tags")
                if tags and tags.count(',')>0:
                    tag_list = tags.split(', ')
                elif tags:
                    tag_list = [tags]
                else:
                    tag_list = None
        except:
            metadata = {}

        uploaded_files.append({
            "file_name": filename,
            "display_name": undo_file_path(filename),
            "description": metadata.get("description"),
            "id": metadata.get("id"),
            "tags": tag_list
        })
    return jsonify({"success":"files retrieved successfully", "files": uploaded_files}), 200

@app.route("/api/clients/<client_id>/files/zip", methods=["POST"])
def zip_uploaded_files(client_id):
    upload_folder = os.path.join("server/uploads", client_id)
    output_path = os.path.join("server/uploads", f"{client_id}_zipped")

    if not os.path.exists(upload_folder) or not os.listdir(upload_folder):
        return jsonify({"message": "No files to zip"}), 204  

    try:
        shutil.make_archive(output_path, "zip", upload_folder)
        shutil.rmtree(upload_folder)
        return jsonify({"success": "Zipped and cleaned"}), 200
    except FileNotFoundError:
        return jsonify({"error": "Zip failed"}), 404
  
@app.route("/api/geojson/<filename>", methods=["GET"])
def get_geojson(filename):
    filepath = os.path.join(os.getcwd(), "data/geojson", filename)
    try:
        return send_file(filepath, mimetype='application/json')
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404


@app.route("/api/pipeline", methods=["GET"])
def run_pipeline():
    
    location = request.args.get("location")
    query = request.args.get("query")
    tag = request.args.get("tag")
    client_id = request.args.get("client_id")
    print('Query: ', query)
    pipeline = Pipeline(location, query, tag, client_id)

    def generate():
        yield f"data: Starting pipeline for query: {query}\n\n"
        time.sleep(2)
        # yield "data: Scraping documents...\n\n"
        # pipeline.scrape()
        yield "data: Adding your documents...\n\n"
        pipeline.add_context()
        yield "data: Embedding documents...\n\n"
        pipeline.embed()
        yield "data: Querying LLM...\n\n"
        result = pipeline.query_llm()
        yield f"data: DONE: {result}\n\n"
        yield "data: DONE\n\n"

    return Response(stream_with_context(generate()), content_type='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True, port=8080)

