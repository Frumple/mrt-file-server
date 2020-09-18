from flask import Blueprint, render_template, send_from_directory

from mrt_file_server import app
from mrt_file_server.utils.log_utils import log_info

world_blueprint = Blueprint("world", __name__, url_prefix="/world")

@app.route("/world/download/terms")
def show_world_downloads_terms():
  return render_template("world/download/terms.html", home = False)

@app.route("/world/download")
def list_world_downloads():
  return render_template("world/download/index.html", home = False)

@app.route("/world/download/<path:filename>")
def download_world(filename):
  log_info("WORLD_DOWNLOAD_SUCCESS", filename)
  return send_from_directory(app.config["WORLD_DOWNLOADS_DIR"], filename, as_attachment = True)