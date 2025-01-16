import threading
import time

import gi
from flask import Flask, Response, jsonify, render_template, request

gi.require_version("Gst", "1.0")
gi.require_version("GstRtspServer", "1.0")

from gi.repository import GLib, GObject, Gst, GstRtspServer

app = Flask(__name__)

Gst.init(None)

rtsp_url = "rtsp://192.168.2.65:8554/stream"


class RTSPServer(GstRtspServer.RTSPMediaFactory):
    def __init__(self):
        super().__init__()
        self.set_launch(
            (
                "ksvideosrc ! "
                "video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! "
                "videoconvert ! "
                "x264enc tune=zerolatency ! "
                "rtph264pay name=pay0 pt=96"
            )
        )
        self.set_shared(True)


class RTSPServerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = False
        self.loop = None

    def run(self):
        self.running = True
        server = GstRtspServer.RTSPServer()
        factory = RTSPServer()
        server.get_mount_points().add_factory("/stream", factory)
        server.attach(None)
        print(f"RTSP server running at {rtsp_url}")

        try:
            self.loop = GLib.MainLoop()
            self.loop.run()
        except Exception as e:
            print(f"Exception in RTSP server: {e}")

    def stop(self):
        if self.loop and self.running:
            self.loop.quit()
            self.running = False
            print("RTSP Server Stopped")


rtsp_thread = None


@app.route("/request_stream_client", methods=["GET"])
def client_request():
    streamer_id = request.args.get("streamer_id")
    print(f"rtsp stream connection request from {streamer_id}")
    return jsonify({"rtsp_url": rtsp_url})


@app.route("/control", methods=["POST"])
def stop_stream():
    global rtsp_thread
    action = request.json.get("action")

    if action == "stop":
        if rtsp_thread and rtsp_thread.running:
            rtsp_thread.stop()
            return jsonify({"message": "Stream stopped successfully!"}), 200
        else:
            return jsonify({"message": "Stream is not running!"}), 400
    elif action == "start":
        if rtsp_thread and rtsp_thread.running:
            return jsonify({"message": "Stream is already running!"}), 400

        rtsp_thread = RTSPServerThread()
        rtsp_thread.daemon = True
        rtsp_thread.start()
        return jsonify({"message": "Stream started successfully"}), 200
    else:
        return jsonify({"error": "invalid action"}), 400


@app.route("/")
def index():
    return """
    <html>
    <head><title>web app</title></head>
    <body>
        <h1>web app</h1>
        
    </body>
    </html>
    """


if __name__ == "__main__":
    try:

        app.run(host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        print(f"there is an issue{e}")
    except KeyboardInterrupt as k:
        print("Keyboard interruption")
