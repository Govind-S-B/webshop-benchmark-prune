#!/bin/bash

# Displays information on how to use script
helpFunction()
{
  echo "Usage: $0 [-d small|all]"
  echo -e "\t-d small|all - Specify whether to download entire dataset (all) or just 1000 (small)"
  exit 1 # Exit script after printing help
}

# Get values of command line flags
while getopts d: flag
do
  case "${flag}" in
    d) data=${OPTARG};;
  esac
done

if [ -z "$data" ]; then
  echo "[ERROR]: Missing -d flag"
  helpFunction
fi

# Install Python Dependencies via conda without prompts
conda install -y spacy

# Install Python Dependencies via pip without prompts
pip install --no-input -r requirements_arm.txt

# Install Environment Dependencies via `conda` without prompts
conda install -y -c pytorch faiss-cpu
conda install -y -c conda-forge openjdk=11

# Helper function to download file if it doesn't exist
download_if_not_exists() {
  local url="$1"
  local filename="$2"
  if [ ! -f "$filename" ]; then
    echo "Downloading $filename..."
    gdown "$url" -O "$filename"
  else
    echo "File $filename already exists, skipping download."
  fi
}

mkdir -p data;
cd data;
if [ "$data" == "small" ]; then
  download_if_not_exists "https://drive.google.com/uc?id=1EgHdxQ_YxqIQlvvq5iKlCrkEKR6-j0Ib" "items_shuffle_1000.json"
  download_if_not_exists "https://drive.google.com/uc?id=1IduG0xl544V_A_jv3tHXC0kyFi7PnyBu" "items_ins_v2_1000.json"
elif [ "$data" == "all" ]; then
  download_if_not_exists "https://drive.google.com/uc?id=1A2whVgOO0euk5O13n2iYDM0bQRkkRduB" "items_shuffle.json"
  download_if_not_exists "https://drive.google.com/uc?id=1s2j6NgHljiZzQNL3veZaAiyW_qDEgBNi" "items_ins_v2.json"
else
  echo "[ERROR]: argument for \`-d\` flag not recognized"
  helpFunction
fi
download_if_not_exists "https://drive.google.com/uc?id=14Kb5SPBk_jfdLZ_CDBNitW98QLDlKR5O" "items_human_ins.json"
cd ..

# Download spaCy large NLP model
python -m spacy download en_core_web_sm

# Build search engine index
cd search_engine
mkdir -p resources resources_100 resources_1k resources_100k
python convert_product_file_format.py # convert items.json => required doc format
mkdir -p indexes
./run_indexing.sh
cd ..

mkdir -p user_session_logs/
