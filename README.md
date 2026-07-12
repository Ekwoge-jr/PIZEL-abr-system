# Reinforcement Learning-Based Adaptive Bitrate Streaming System for Remote Laboratory Learning

## Overview

This project implements a Reinforcement Learning (RL)-based Adaptive Bitrate (ABR) Streaming System designed for remote laboratory learning environments. The system uses a Proximal Policy Optimization (PPO) model to dynamically select video quality levels based on network conditions while supporting Region of Interest (ROI) configuration for educational laboratory content.

The objective is to improve the Quality of Experience (QoE) for students accessing laboratory demonstrations under varying network conditions.

---

## Features

* Dynamic Adaptive Bitrate Streaming (ABR)
* DASH (Dynamic Adaptive Streaming over HTTP) video delivery
* PPO-based bitrate selection
* Real-time throughput and buffer monitoring
* ROI configuration and management
* Video segmentation using FFmpeg
* ONNX model inference in the browser
* Performance logging and evaluation
* Network emulation testing using Clumsy

---

## System Architecture

The system consists of four major components:

### 1. Video Processing Layer

Responsible for:

* Video upload
* Multi-bitrate encoding
* DASH packaging
* Segment generation

### 2. Streaming Layer

Responsible for:

* DASH manifest delivery
* Segment delivery
* Flask API endpoints

### 3. Reinforcement Learning Layer

Responsible for:

* State construction
* PPO inference
* Bitrate decision making

### 4. ROI Management Layer

Responsible for:

* ROI configuration
* ROI storage
* ROI retrieval and editing

---

## Technology Stack

### Backend

* Python
* Flask
* FFmpeg
* ONNX Runtime

### Frontend

* HTML
* CSS
* JavaScript
* DASH.js

### Database

* PostgreSQL

### Evaluation Tools

* Clumsy
* Microsoft Excel

### Version Control

* Git
* GitHub

---

## Project Structure

```text
backend/
│
├── app.py
├── config.py
├── extensions.py
├── models.py
├── dash_server/
│   ├── manifest.mpd
│   └── segments/
│
├── media/
│   ├── test_video.mp4
    └── image.png
│
│
├── services/
│   ├── ffmpeg_pipeline.py
│   ├── roi_encoder.py
│   ├── roi_processor.py
│
└── routes/

frontend/
│
├── player.html
├── player.js
│
├── roi_config.html
├── roi-config.js
│
├── upload.html
│
├── broker.js
├── metrics_logger.js
├── policy.js
├── rl_engine.js
├── rl_inference.js
├── state_builder.js
├── roi-client.js
│
└── model/
    └── ppo_abr_single.onnx
```

---

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd project-folder
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## FFmpeg Installation

Download FFmpeg from:

https://ffmpeg.org/download.html

Verify installation:

```bash
ffmpeg -version
```

---

## Running the Backend

```bash
python app.py
```

Backend server runs on:

```text
http://localhost:5000
```

---

## Running the Frontend

Open:

```text
frontend/player.html
```

or serve using a local web server.

```bash
python -m http.server 8000
```

---

## ROI Configuration Workflow

1. Administrator uploads:

   * Laboratory image
   * Laboratory video

2. System stores:

   * Video and Image in backend media directory

3. FFmpeg automatically:

   * Encodes video
   * Generates DASH segments
   * Creates MPD manifest

4. Administrator defines ROIs using ROI configuration page.

5. ROI coordinates are stored in the database.

6. Students stream laboratory content using the DASH player.

---

## Reinforcement Learning Workflow

For every completed video segment:

1. Collect throughput.
2. Collect buffer occupancy.
3. Collect download time.
4. Construct RL state vector.
5. Run PPO inference.
6. Select bitrate action.
7. Switch DASH representation.

Available actions:

| Action | Bitrate   |
| ------ | --------- |
| 0      | 300 kbps  |
| 1      | 800 kbps  |
| 2      | 1500 kbps |

---

## Testing and Evaluation

### Network Emulation

The system was evaluated using Clumsy.

Tested network conditions include:

* Packet loss
* Latency
* Network instability

### Metrics Collected

* Throughput
* Buffer Occupancy
* Download Time
* Selected Bitrate
* Quality Switches
* Startup Delay
* Rebuffer Events

### Exporting Logs

Metrics are exported to CSV files for analysis in Excel, you enter the command "exportSessionLog();" on the browser terminal.

---

## Known Limitations

Current implementation:

* Supports manually configured ROIs.
* ROI-aware bitrate adaptation is not yet integrated into PPO decision making.
* Uses a fixed set of three video representations.
* Evaluation is currently performed in a controlled local environment.
* ROI encoding was set, but there was no visible changes in the video during testing because the video encoder "libx264" doesn't fully support direct ROI encoding  

---

## Future Work

* Full ROI-aware adaptive bitrate selection.
* Automatic ROI detection using computer vision.
* Multi-user streaming support.
* Live streaming support.
* Deployment on cloud infrastructure.
* Advanced QoE-based reward optimization.

---


