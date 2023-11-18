import os
import pandas as pd

from statistics import mean
import matplotlib.pyplot as plt

# TODO need to try to do it so the timestamp starts at 0

dirs = ["/Users/caetano/Desktop/remora_79024"]
# create an empty list to store the individual GPU DataFrames
gpu_dfs = []

# loop over all files in the directory that match the file name format
for dir_path in dirs:
    dir_path = dir_path + "/GPU"
    # loop over all files in the directory that match the file name format
    for file_name in os.listdir(dir_path):
        if file_name.startswith('gpu_util_stats_') and file_name.endswith('.txt'):
            # extract the node name from the file name
            node = file_name.split('_')[3].split('.')[0]

            # read the data from the file with whitespace as the separator
            file_path = os.path.join(dir_path, file_name)
            df = pd.read_csv(file_path, sep='\s+')

            # convert the time column from unix timestamp to datetime format
            # df['time'] = pd.to_datetime(df['time'], unit='s')

            # create a list of column names for the GPU columns
            gpu_cols = [col for col in df.columns if 'gpu_' in col]

            # create a new DataFrame with columns for gpu, used_GB, and avail_GB for each GPU
            for gpu_id in range(len(gpu_cols)):
                gpu_col_used = f'gpu_{gpu_id}_util'
                gpu_df = pd.DataFrame({
                    'node': [node] * len(df),
                    'time': df["time"],
                    'gpu': [f'gpu_{gpu_id}'] * len(df),
                    'util': df[gpu_col_used],
                })
                gpu_dfs.append(gpu_df)

# merge the individual GPU DataFrames into a single DataFrame
gpu_df = pd.concat(gpu_dfs)

avgs = []

# calculate the average GPU usage for each GPU during the recorded time period, by node
for node in gpu_df['node'].unique():
    for gpu_id in gpu_df['gpu'].unique():
        gpu_data = gpu_df[(gpu_df['node'] == node) & (gpu_df['gpu'] == gpu_id)]
        avg_usage = gpu_data['util'].mean()
        print(f'Average {node} {gpu_id} utilization: {avg_usage:.3f}%')
        avgs.append(avg_usage)

print(sum(avgs)/(len(avgs)*100))

df = gpu_df

# convert the "time" column to datetime objects
df["time"] = pd.to_datetime(df["time"], unit="s")

# set the "time" column as the DataFrame's index
df = df.set_index("time")

# # group the DataFrame by the "node" column and create a line plot for each group
# for node, group in df.groupby("node"):
#     group_resampled = group.resample("80S").mean()
#     group_resampled["util"].plot(label=node)

df = df.resample("60S").mean()

# plot the "used_GB" column
df["util"].plot(label="GPU Util.")

# set the x and y-axis labels
plt.xlabel("Time")
plt.ylabel("Util GB")

# set the title of the plot
plt.title("HTR Resource Utilization")

# add a legend to the plot
plt.legend()

# display the plot
plt.show()
