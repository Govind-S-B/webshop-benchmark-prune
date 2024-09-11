import os
import zipfile
import pandas as pd
import shutil

def extract_and_process_zip_files(zip_folder, observer_logs_folder, zip_file_order):
    # Create observer_logs_folder if it doesn't exist
    if not os.path.exists(observer_logs_folder):
        os.makedirs(observer_logs_folder)
    else:
        # Clear the contents of the observer_logs_folder
        for filename in os.listdir(observer_logs_folder):
            file_path = os.path.join(observer_logs_folder, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
    
    # Initialize an empty list to hold dataframes for merging CSVs
    dataframes = []

    # Temporary extraction folder
    temp_extract_folder = os.path.join(observer_logs_folder, 'temp_extract')
    if not os.path.exists(temp_extract_folder):
        os.makedirs(temp_extract_folder)

    # Iterate over each zip file in the specified order
    for zip_filename in zip_file_order:
        zip_path = os.path.join(zip_folder, zip_filename)
        if os.path.exists(zip_path) and zip_filename.endswith('.zip'):
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extract all files to the temporary folder
                zip_ref.extractall(temp_extract_folder)
                
                # Process each file in the extracted folder
                for file in zip_ref.namelist():
                    file_path = os.path.join(temp_extract_folder, file)
                    
                    if file.endswith('.jsonl'):
                        # Move JSONL files to observer_logs folder
                        shutil.move(file_path, os.path.join(observer_logs_folder, file))
                    
                    elif file == 'session_details.csv':
                        # Read and append session_details.csv to the list of dataframes
                        df = pd.read_csv(file_path)
                        if dataframes:
                            df = df[:]  # Remove header if not the first file
                        dataframes.append(df)
                    
                    elif file == 'observer_termination_cause':
                        # Rename and move observer_termination_cause files
                        new_filename = f"{os.path.splitext(zip_filename)[0]}.observer_termination_cause"
                        shutil.move(file_path, os.path.join(observer_logs_folder, new_filename))
    
    # Merge all session_details.csv dataframes
    if dataframes:
        merged_df = pd.concat(dataframes, ignore_index=True)
        merged_df.to_csv(os.path.join(observer_logs_folder, 'session_details.csv'), index=False)

    # Clean up the temporary extraction folder
    shutil.rmtree(temp_extract_folder)

# Example usage
zip_folder = 'analytics_script/observer_zips'
observer_logs_folder = 'analytics_script/observer_logs'
zip_file_order = ['0_20_run.zip', '21_50_run.zip', '51_200_run.zip']
extract_and_process_zip_files(zip_folder, observer_logs_folder, zip_file_order)