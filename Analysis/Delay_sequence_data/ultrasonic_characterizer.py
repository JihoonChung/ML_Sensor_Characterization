import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from joblib import load


# Merge the data

# Define `file_path` as a global variable
script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script

def get_all_files_in_directory(root_directory):
    file_paths = []
    for root, dirs, files in os.walk(root_directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths


def merge_csv_files(file_paths):
    """
    Merge multiple CSV files into a single DataFrame.

    Parameters:
    file_paths (list of str): List of file paths to the CSV files.

    Returns:
    DataFrame: Merged DataFrame containing data from all input CSV files.
    """
    dataframes = []
    for file in file_paths:
        df = pd.read_csv(file)
        dataframes.append(df)

    # Concatenate all DataFrames
    merged_df = pd.concat(dataframes, ignore_index=True)
    
    return merged_df


def identify_and_remove_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df_no_outliers = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    df_outliers_lower = df[(df[column] <= lower_bound)]
    df_outliers_upper = df[(df[column] >= upper_bound)]
    return df_no_outliers,df_outliers_lower,df_outliers_upper

def split_quartiles(df):
    # Group the data by 'Sensor ID', 'Delay (us)', and 'Range (cm)'
    df_copy = df.copy()
    grouped = df_copy.groupby(['Sensor ID', 'Delay (us)', 'Range (cm)'])

    # Identify and remove outliers for each group
    middle_quartile = []
    lower_quartile = []
    upper_quartile = []

    for name, group in grouped:
        cleaned_group = group.copy()
        for column in ['Ping Time (us)']:
            middle_quartile_group,lower_quartile_group,upper_quartile_group = identify_and_remove_outliers(cleaned_group, column)
        middle_quartile.append(middle_quartile_group)
        lower_quartile.append(lower_quartile_group)
        upper_quartile.append(upper_quartile_group)
    # Combine the cleaned groups into a single DataFrame
    df_middle_quartile= pd.concat(middle_quartile)
    df_lower_quartile = pd.concat(lower_quartile)
    df_upper_quartile = pd.concat(upper_quartile)
    
    return df_middle_quartile, df_lower_quartile, df_upper_quartile


def create_range_delay_feature(df_quartile,bound):
    # Step 1: Group and calculate mean
    df_grouped = df_quartile.groupby(['Sensor ID', 'Range (cm)', 'Delay (us)'])['Ping Time (us)'].mean().reset_index()

    # Step 2: Create `range_delay` column
    df_grouped['range_delay'] = df_grouped['Range (cm)'].astype(str) + '_' + df_grouped['Delay (us)'].astype(str)+'_'+'mean'+'_'+bound

    # Step 3: Pivot the table
    df_pivot = df_grouped.pivot(index='Sensor ID', columns='range_delay', values='Ping Time (us)').reset_index()
    
    return df_pivot


def feature_engineering_quartile_means(df):
    df=df[df["Range (cm)"].isin([13,18,23])] # this is necessary features.
    values_to_keep = [16800,10000,8000,6000,3000]
    df = df[df["Delay (us)"].isin(values_to_keep)]

    df_middle_quartile, _, df_upper_quartile = split_quartiles(df)
    df_range_delay_middle = create_range_delay_feature(df_middle_quartile,"middle")
    #df_range_delay_upper = create_range_delay_feature(df_upper_quartile,"upper")

    # List of DataFrames
    df_pivots = [df_range_delay_middle]

    # Initialize the merged DataFrame with the first DataFrame in the list
    df_range_delay_all = df_pivots[0]

    # Iteratively merge each DataFrame in the list
    for df in df_pivots[1:]:
        df_range_delay_all = df_range_delay_all.merge(df, on='Sensor ID')
        
    # Replace all NaN values with 0 in the merged DataFrame
    df_range_delay_all.fillna(0, inplace=True)

    # Define the column list
    column_list = [
        '23_6000_mean_middle', '23_16800_mean_middle', '18_3000_mean_middle',
       '18_16800_mean_middle', '23_10000_mean_middle', '13_6000_mean_middle',
       '18_6000_mean_middle', '13_3000_mean_middle', '18_8000_mean_middle',
       '13_10000_mean_middle', 'Sensor ID'
    ]

    # Select columns that are only in the list
    df_range_delay_all = df_range_delay_all[[col for col in df_range_delay_all.columns if col in column_list]]

    df = df_range_delay_all[column_list]

    df = df.reindex(columns=column_list)
    return df


def predict_KMeans(df):

    # Standardize the features
    df = df.copy()
    sensor_ids = df.index if 'Sensor ID' not in df.columns else df['Sensor ID']
    scaler = load(f"{script_dir}/best_models/final/scaler_final_mi.joblib")
    features_scaled = scaler.transform(df.drop(columns=['Sensor ID']))

    kmeans = load(f"{script_dir}/best_models/final/kmeans_model_final_df_mi.joblib")
    print("Loaded pre-trained KMeans model.")

    # Predict cluster labels
    cluster_labels = kmeans.predict(features_scaled)
    df['cluster'] = cluster_labels

    # Define the column list
    column_list = ['Sensor ID', 'cluster']

    # Select columns that are only in the list
    df = df[[col for col in df.columns if col in column_list]]

    return df




def display_cluster_figures(cluster_num, refined_category, edge_case_sensitivity, description):
    """
    Display PNG figures from a folder where filenames are prefixed with a specific string,
    along with annotations for the refined category, edge case sensitivity, and description.

    Parameters:
    cluster_num (int): Cluster number to display the corresponding figure.
    refined_category (str): Refined category of the cluster.
    edge_case_sensitivity (str): Edge case sensitivity of the cluster.
    description (str): Description of the cluster.
    """
    cluster_file = f"{script_dir}/characteristic_figure/cluster_{cluster_num}.png"

    try:
        # Load and display the image
        img = mpimg.imread(cluster_file)
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.imshow(img)
        ax.axis('off')  # Turn off axis
        
        # Add annotations below the figure
        text = (
            f"Refined Category: {refined_category}\n"
            f"Edge Case Sensitivity: {edge_case_sensitivity}\n"
            f"Description: {description}"
        )
        plt.figtext(0.5, 0.01, text, wrap=True, horizontalalignment='center', fontsize=10)
        plt.show()
    except FileNotFoundError:
        print(f"No PNG file found for cluster {cluster_num}.")



if __name__ == '__main__':
    file_path = f"{script_dir}/../processed_data/all_data_v4-1-1_cleaned_sensor211.csv"
    df_data_v4_1_1 = pd.read_csv(file_path)
    df_range_delay_all = feature_engineering_quartile_means(df_data_v4_1_1)
    df_range_delay_all = df_range_delay_all.sample(n=3)
    predicted_cluster = predict_KMeans(df_range_delay_all)

    df_characterization = pd.read_csv(f"{script_dir}/characteristic_figure/cluster_desc.csv") 
    
    with pd.option_context('display.max_colwidth', None):
        for _, row in predicted_cluster.iterrows():
            print("\n====================")
            print(f"Sensor ID: {row['Sensor ID']}, Cluster: {row['cluster']}")
            
            # Extract relevant details
            refined_category = df_characterization[df_characterization["cluster"] == row["cluster"]]["Refined Category"].values[0]
            edge_case_sensitivity = df_characterization[df_characterization["cluster"] == row["cluster"]]["Edge Case Sensitivity"].values[0]
            description = df_characterization[df_characterization["cluster"] == row["cluster"]]["Description"].values[0]
            
            # Print details
            print(f"Refined Cluster: {refined_category}")
            print(f"Edge Case Sensitivity: {edge_case_sensitivity}")
            print(f"Description: {description}")
            
            # Pass all required arguments to the function
            print("\nDisplaying figure for the cluster...")
            display_cluster_figures(row["cluster"], refined_category, edge_case_sensitivity, description)
            
            print("====================\n")
