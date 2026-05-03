#!/bin/bash

# Download best.pt from Google Drive if not exists
MODEL_PATH="app/_ai/model/best.pt"

if [ ! -f "$MODEL_PATH" ]; then
    echo "Downloading best.pt from Google Drive..."
    mkdir -p app/_ai/model
    pip install gdown --quiet
    gdown "1ByugQfowm8urKSOUWs0_zqMyaemItlRj" -O "$MODEL_PATH"
    echo "Model downloaded successfully!"
else
    echo "Model already exists, skipping download."
fi

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000
