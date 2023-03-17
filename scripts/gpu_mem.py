import os
import pandas as pd

# set the directory containing the files
dir_path = '/home/hpcc/gitlabci/perf/remora_74415/GPU'

# create an empty list to store the individual GPU DataFrames
gpu_dfs = []

# loop over all files in the directory that match the file name format
for file_name in os.listdir(dir_path):
    if file_name.startswith('gpu_memory_stats_') and file_name.endswith('.txt'):
        # extract the node name from the file name
        node = file_name.split('_')[3].split('.')[0]

        # read the data from the file with whitespace as the separator
        file_path = os.path.join(dir_path, file_name)
        df = pd.read_csv(file_path, sep='\s+')

        # convert the time column from unix timestamp to datetime format
        df['time'] = pd.to_datetime(df['time'], unit='s')

        # create a list of column names for the GPU columns
        gpu_cols = [col for col in df.columns if 'gpu_' in col]

        # create a new DataFrame with columns for gpu, used_GB, and avail_GB for each GPU
        for gpu_id in range(len(gpu_cols)//2):
            gpu_col_avail = f'gpu_{gpu_id}_avail_GB'
            gpu_col_used = f'gpu_{gpu_id}_used_GB'
            gpu_df = pd.DataFrame({
                'node': [node] * len(df),
                'gpu': [f'gpu_{gpu_id}'] * len(df),
                'used_GB': df[gpu_col_used],
                'avail_GB': df[gpu_col_avail]
            })
            gpu_dfs.append(gpu_df)

# merge the individual GPU DataFrames into a single DataFrame
gpu_df = pd.concat(gpu_dfs)

# calculate the average GPU usage for each GPU during the recorded time period, by node
for node in gpu_df['node'].unique():
    for gpu_id in gpu_df['gpu'].unique():
        gpu_data = gpu_df[(gpu_df['node'] == node) & (gpu_df['gpu'] == gpu_id)]
        nonzero_usage = gpu_data[gpu_data['used_GB'] > 0]['used_GB']
        avg_usage = nonzero_usage.mean()
        print(f'Average {node} {gpu_id} usage: {avg_usage:.3f} GB')
# TODO want average value across all nodes...and other metrics?
