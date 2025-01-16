# RTSP Streaming System

This project aims to implement a real-time video streaming application using the RTSP protocol, Gstreamer, Flask and RestApi. It includes a web server and a client application, allowing for video streams to be shared and controlled over a network.

## Features

### Web Server (web.py)
- Hosts an RTSP stream using GStreamer.
- Provides an HTTP API for clients to request and control streams.

### Client Application (client.py)
- Connects to the RTSP server to receive video streams (also using GStreamer).
- Allows users to start, stop, or exit the stream interactively (Using REST).

## Technologies that I Used 

- Python 3.7 or higher
  - Flask
  - Requests
  - PyGObject (gi module)
- GStreamer with RTSP support

I also used MSYS2 enviroment on my Windows computer.

## Usage
After installing libraries like flask and gstreamer on your system you can do the following:

### 1. Run the Web Server

```terminal
pyhton web.py
```

The server will start on `http://0.0.0.0:5000`.

RTSP streams will be available at `rtsp://<server-ip>:8554/stream`.

### 1. Run the Client Application

```terminal
pyhton client.py
```
The client application requests and connects to the RTSP stream.

Available Commands:

  * `start` : Requests the server to start the RTSP stream and begins playback.
  * `stop` : Stops the current stream.
  * `exit` : Exits the client application.

## API Endpoints

### 1. Request RTSP Stream

GET `/request_stream_client`

Parameters: streamer_id (string)

Response: RTSP URL for the client.

### 2. Control Stream

POST `/control`

Body: `{"action": "start" | "stop"}`

Response: Success or error message based on the requested action.

## GStreamer Pipelines
These pipelines are designed for Windows os.
### Server Pipline
```sh
ksvideosrc ! video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! \
    videoconvert ! x264enc tune=zerolatency ! rtph264pay name=pay0 pt=96
```
### Client Pipeline
```sh
rtspsrc location=<rtsp_url> latency=0 ! rtph264depay ! h264parse ! openh264dec ! videoconvert ! autovideosink
```

## Example Workflow

Run `web.py` to start the RTSP server and HTTP API.

Run `client.py`

The client (`client.py`) requests the RTSP URL from the server via the `/request_stream_client endpoint`.

Use the client commands (`start`, `stop`, `exit`) to control the video stream.

## Notes to self

  * can add a video stream to localhost in flask
  * can add additional features like real time chat 











