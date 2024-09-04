#!/bin/bash

# Install Python Dependencies via conda without prompts
conda install -y spacy

# Install Python Dependencies via pip without prompts
pip install --no-input -r requirements_arm.txt

# Install Environment Dependencies via `conda` without prompts
conda install -y -c pytorch faiss-cpu
conda install -y -c conda-forge openjdk=11

mkdir -p data;
echo "none" > data/prev_DATASET_SOURCE

# Download spaCy large NLP model
python -m spacy download en_core_web_sm

# Build search engine index
cd search_engine
mkdir -p resources resources_100 resources_1k resources_100k
mkdir -p indexes
cd ..

mkdir -p user_session_logs/