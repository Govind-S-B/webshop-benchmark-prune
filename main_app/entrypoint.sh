# Get the dataset size from the environment variable
data=${DATASET_SOURCE}

if [ -z "$data" ]; then
  echo "[ERROR]: Missing DATASET_SIZE environment variable"
  exit 1 # Exit script if the environment variable is not set
fi

# Check if the previous dataset source is the same as the current one
prev_data=$(cat data/prev_DATASET_SOURCE)

dataset_state_change=false
if [ "$prev_data" == "$data" ]; then
  echo "The dataset source has not changed. Moving directly to run webshop."
else
  echo "The dataset source has changed from $prev_data to $data. Proceeding with the script."
  echo "$data" > data/prev_DATASET_SOURCE
  dataset_state_change=true
fi

if [ "$dataset_state_change" = false ]; then

  # Change to the data directory
  cd data

  # Check if the file items_human_ins.json exists, if not download it
  if [ ! -f "items_human_ins.json" ]; then
    gdown https://drive.google.com/uc?id=14Kb5SPBk_jfdLZ_CDBNitW98QLDlKR5O
  fi

  # Define a function to download a file if it does not exist
  download_if_not_exists() {
    local file=$1
    local url=$2
    if [ ! -f "$file" ]; then
      gdown $url
    fi
  }

  # Switch case for different dataset sources
  case "$data" in
    "small")
      download_if_not_exists "items_shuffle_1000.json" "https://drive.google.com/uc?id=1EgHdxQ_YxqIQlvvq5iKlCrkEKR6-j0Ib"
      download_if_not_exists "items_ins_v2_1000.json" "https://drive.google.com/uc?id=1IduG0xl544V_A_jv3tHXC0kyFi7PnyBu"
      ;;
    "all")
      download_if_not_exists "items_ins_v2.json" "https://drive.google.com/uc?id=1s2j6NgHljiZzQNL3veZaAiyW_qDEgBNi"
      download_if_not_exists "items_shuffle.json" "https://drive.google.com/uc?id=1s2j6NgHljiZzQNL3veZaAiyW_qDEgBNi"
      ;;
    *)
      echo "[ERROR]: Invalid DATASET_SOURCE value"
      exit 1
      ;;
  esac

  # Change back to the previous directory
  cd ..

  # Build search engine index
  cd search_engine
  python convert_product_file_format.py # convert items.json => required doc format
  ./run_indexing.sh
  cd ..

fi

export FLASK_ENV=development
python -m web_agent_site.app --log --attrs