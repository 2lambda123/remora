import os
import pandas as pd

from statistics import mean
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# todo hmm need to deal with NAN...with the 26 suffix

dirs = ["/Users/caetano/Desktop/remora_79024"]
# create an empty list to store the individual GPU DataFrames
gpu_dfs = []

# loop over all files in the directory that match the file name format
for dir_path in dirs:
    dir_path = dir_path + "/CPU"
    # loop over all files in the directory that match the file name format
    for file_name in os.listdir(dir_path):
        if file_name.startswith('cpu_') and file_name.endswith('.txt'):
            # extract the node name from the file name
            node = file_name.split('_')[1].split('.')[0]

            # read the data from the file with whitespace as the separator
            file_path = os.path.join(dir_path, file_name)
            df = pd.read_csv(file_path, sep='\s+')

            # convert the time column from unix timestamp to datetime format
            # df['time'] = pd.to_datetime(df['time'], unit='s')

            # create a list of column names for the GPU columns
            # exclude the cpu_all column
            gpu_cols = [col for col in df.columns if 'cpu_' in col and not 'cpu_all' in col]

            # create a new DataFrame with columns for gpu, used_GB, and avail_GB for each GPU
            for gpu_id in range(len(gpu_cols)//2):
                cpu_col_sys = f'cpu_{gpu_id}_sys'
                cpu_col_usr = f'cpu_{gpu_id}_usr'
                gpu_df = pd.DataFrame({
                    'node': [node] * len(df),
                    'cpu': [f'cpu_{gpu_id}'] * len(df),
                    'sys_util': df[cpu_col_sys],
                    'time': df["time"],
                    'usr_util': df[cpu_col_usr],
                    'total_util': df[cpu_col_sys] + df[cpu_col_usr]
                })
                gpu_dfs.append(gpu_df)

# merge the individual GPU DataFrames into a single DataFrame
gpu_df = pd.concat(gpu_dfs)

avgs = []

# calculate the average GPU usage for each GPU during the recorded time period, by node
for node in gpu_df['node'].unique():
    for gpu_id in gpu_df['cpu'].unique():
        gpu_data = gpu_df[(gpu_df['node'] == node) & (gpu_df['cpu'] == gpu_id)]
        avg_usage = gpu_data['total_util'].mean()
        # print(f'Average {node} {gpu_id} utilization: {avg_usage:.3f}%')
        avgs.append(avg_usage)

# used to calculate means when dealing with percentages...
print(sum(avgs)/(len(avgs)*100))

df = gpu_df

df["time"] = (df["time"] - df.iloc[0]["time"]).astype(int)
print(df["time"])

# convert the "time" column to datetime objects
df["time"] = pd.to_datetime(df["time"], unit="s")

# set the "time" column as the DataFrame's index
df = df.set_index("time")

# group the DataFrame by the "node" column and create a line plot for each group
# for node, group in df.groupby("node"):
#     group["util"].plot(label=node)

df = df.resample("40S").mean()

# plot the "used_GB" column
# df["total_util"].plot(label="CPU Util.")

# # set the x and y-axis labels
# plt.xlabel("Time")
# plt.ylabel("Util GB")

# # set the title of the plot
# plt.title("GPU Memory Usage")

# # add a legend to the plot
# plt.legend()

# # display the plot
# plt.show()


fig, ax = plt.subplots()
df["total_util"].plot(ax=ax, label="CPU Util.")
ax.set_xlabel("Time (seconds)")
ax.set_ylabel("CPU Utilization")
# print(df)
# seconds = (df["time"]).strftime('%S')
# print(df)
seconds = (df.index - df.index[0]).total_seconds().astype(int)
ax.set_xticks(df.index)
ax.set_xticklabels(seconds)
# seconds = (df.index - df.index[0]).total_seconds().astype(int)
# print(seconds)
# set the x-axis ticks to display seconds
# ax.set_xticks(seconds)
# ax.set_xticklabels(seconds)

# plt.ylim(bottom=57)

# # set the title of the plot
plt.title("HTR Resource Utilization")
plt.legend()
plt.show()

# plot the "used_GB" column
# df["total_util"].plot(label="CPU Util.")

# plt.xlabel("Time")
# plt.ylabel("Utilization (%)")
# plt.ylim(bottom=57)

# # set the title of the plot
# # plt.title("HTR Resource Utilization")


# # add a legend to the plot
# plt.legend()

# # display the plot
# plt.show()
