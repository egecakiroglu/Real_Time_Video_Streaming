import os
import sys
import time

import gi
import requests

gi.require_version("Gst", "1.0")
gi.require_version("GstRtspServer", "1.0")

from gi.repository import GLib, GObject, Gst, GstRtspServer

stream_req_url = "http://192.168.2.65:5000/request_stream_client"
control_url = "http://192.168.2.65:5000/control"

streamer_id = "192.168.2.65"

Gst.init(None)

pipeline = None


def request_rtsp_stream():
    print("requesting rtsp stream connection...")
    response = requests.get(stream_req_url, params={"streamer_id": streamer_id})
    if response.status_code == 200:
        rtsp_url = response.json().get("rtsp_url")
        print(f"rtsp url acquired : {rtsp_url}")
        return rtsp_url
    else:
        print("connection issue")
        sys.exit(1)


"""
def create_pipeline(rtsp_url):

    pipeline_str = (
        f"rtspsrc location={rtsp_url} latency=0 ! "
        "rtph264depay ! h264parse ! openh264dec ! "
        "videoconvert ! autovideosink"
    )
    try:
        pipeline = Gst.parse_launch(pipeline_str)
        print("created")
        return pipeline
    except GLib.GError as e:
        print(f"Failed to create pipeline: {e}")
        sys.exit(1)  # Exit the program if pipeline creation fails
"""


def start_stream(rtsp_url):
    global pipeline
    if pipeline:
        print("Stream is already running.")
        return
    print(f"Starting stream with URL: {rtsp_url}")
    pipeline_str = (
        f"rtspsrc location={rtsp_url} latency=0 ! "
        "rtph264depay ! h264parse ! openh264dec ! "
        "videoconvert ! autovideosink"
    )
    try:
        pipeline = Gst.parse_launch(pipeline_str)
        pipeline.set_state(Gst.State.PLAYING)
        print("Stream started.")
    except Exception as e:
        print(f"Error starting stream: {e}")
        pipeline = None


def stop_stream():
    global pipeline
    if not pipeline:
        print("No active stream to stop.")
        return
    print("Stopping stream...")
    pipeline.set_state(Gst.State.NULL)
    pipeline = None
    print("Stream stopped.")


def main(rtsp_url):
    global pipeline
    print("Client is ready. Enter commands to control the stream:")
    print("  'start' - Start the RTSP stream")
    print("  'stop'  - Stop the RTSP stream")
    print("  'exit'  - Exit the program")

    while True:
        try:
            command = input("Command: ").strip().lower()
            if command == "start":
                # Send start request to the server
                response = requests.post(control_url, json={"action": "start"})
                if response.status_code == 200:

                    start_stream(rtsp_url)
                else:
                    print(
                        f"Error: {response.json().get('message', 'Unable to start stream')}"
                    )
            elif command == "stop":
                # Send stop request to the server
                response = requests.post(control_url, json={"action": "stop"})
                if response.status_code == 200:
                    stop_stream()
                else:
                    print(
                        f"Error: {response.json().get('message', 'Unable to stop stream')}"
                    )
            elif command == "exit":
                print("Exiting...")
                stop_stream()
                break
            else:
                print("Invalid command. Please use 'start', 'stop', or 'exit'.")
        except KeyboardInterrupt:
            print("\nKeyboard interrupt detected. Exiting...")
            stop_stream()
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    rtsp_url = request_rtsp_stream()
    main(rtsp_url=rtsp_url)
