import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def identify_outliers(series):
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return ((series < lower_bound) | (series > upper_bound)).sum()

def average_variability_metrics(df_cluster, all_cleaned_df):
    """
    Calculate the average number of outliers and average standard deviation of ping time for each cluster,
    and the weighted averages of these values.

    Parameters:
    df_cluster (DataFrame): The DataFrame containing sensor ID and their respective clusters.
    all_cleaned_df (DataFrame): The DataFrame containing the cleaned data.

    Returns:
    DataFrame: A DataFrame with columns for cluster, average number of outliers, and average std ping time.
    float: The weighted average of the average number of outliers across clusters.
    float: The weighted average of the average standard deviation of ping time across clusters.
    """

    # List to store the results
    results = []

    # Iterate over each cluster
    for target in df_cluster["cluster"].unique():
        # Get the sensor IDs for the current cluster
        cluster_sensors = df_cluster[df_cluster["cluster"] == target]["Sensor ID"].unique()

        # Filter the all_cleaned_df for the current cluster sensors
        all_cleaned_df_target = all_cleaned_df[all_cleaned_df['Sensor ID'].isin(cluster_sensors)]

        # Group by 'Delay (us)' and 'Range (cm)', then calculate the number of outliers in 'Ping Time (us)'
        grouped_outliers = all_cleaned_df_target.groupby(['Delay (us)', 'Range (cm)'])['Ping Time (us)'].apply(identify_outliers).reset_index(name='outliers')
        
        # Calculate the average number of outliers for the current cluster
        avg_count_outliers = grouped_outliers['outliers'].mean()
        max_count_outliers = grouped_outliers['outliers'].max()

        # Group by sensor ID, delay, and range, then calculate the standard deviation of ping time
        grouped_std = all_cleaned_df_target.groupby(['Sensor ID', 'Delay (us)', 'Range (cm)']).agg(
            std_ping_time=('Ping Time (us)', 'std')
        ).reset_index()

        # Calculate the average std ping time for the current cluster
        avg_std_ping_time = grouped_std['std_ping_time'].mean()

        # Append the results to the list
        results.append({'cluster': target, 'max_count_outliers':max_count_outliers, 'avg_count_outliers': avg_count_outliers, 'avg_std_ping_time': avg_std_ping_time, 'count': len(cluster_sensors)})
    
    # Convert the results list to a DataFrame
    results_df = pd.DataFrame(results)
    
    # Calculate the weighted average of the average number of outliers
    alpha = 0.5

    results_df['weighted_avg_count_outliers'] =(results_df['max_count_outliers']-results_df['avg_count_outliers']) /results_df['count']
    weighted_avg_count_outliers_score = results_df['weighted_avg_count_outliers'].mean() + alpha*np.log(results_df['cluster'].max() + 1)

    # Calculate the weighted average of the average std ping time
    results_df['weighted_avg_std_ping_time'] = results_df['avg_std_ping_time'] /results_df['count']
    weighted_avg_std_ping_time_score = results_df['weighted_avg_std_ping_time'].mean()+ alpha*np.log(results_df['cluster'].max() + 1)

    return results_df, weighted_avg_count_outliers_score, weighted_avg_std_ping_time_score

def visualize_lineplot_ping_time_with_variability(df, target = []):
    """
    Visualize the effect of range on ping time for each delay separately with variability.

    Parameters:
    df (DataFrame): The DataFrame containing the data.
    """
    # Group by sensor ID, delay, and range, then calculate the mean and standard deviation of ping time
    grouped_df = df.groupby(['Sensor ID', 'Delay (us)', 'Range (cm)']).agg(
        mean_ping_time=('Ping Time (us)', 'mean'),
        std_ping_time=('Ping Time (us)', 'std')
    ).reset_index()

    target_df = grouped_df[grouped_df['Sensor ID'].isin(target)]
    # Get unique delays
    unique_delays = target_df['Delay (us)'].unique()

    for delay in unique_delays:
        subset_df = target_df[target_df['Delay (us)'] == delay]

        fig = px.line(

        )

        # Adding error bars
        for sensor_id in subset_df['Sensor ID'].unique():
            sensor_data = subset_df[subset_df['Sensor ID'] == sensor_id]
            fig.add_trace(
                go.Scatter(
                    x=sensor_data['Range (cm)'],
                    y=sensor_data['mean_ping_time'],
                    mode='lines+markers',
                    name=f'Sensor {sensor_id}',
                    error_y=dict(
                        type='data',
                        array=sensor_data['std_ping_time'],
                        visible=True
                    )
                )
            )

        # Plot reference line
        ranges = np.linspace(subset_df['Range (cm)'].min(), subset_df['Range (cm)'].max(), 100)
        reference_ping_times = 57 * ranges
        fig.add_trace(
            go.Scatter(
                x=ranges,
                y=reference_ping_times,
                mode='lines',
                line=dict(color='red', dash='dash'),
                name='Reference Line'
            )
        )

        fig.update_layout(
            xaxis_title='Range (cm)',
            yaxis_title='Mean Ping Time (us)',
            legend_title='Sensor ID',
            template='plotly_white'
        )

        fig.show()


def visualize_lineplot_ping_time_with_variability_simple(df, target=[]):
    """
    Visualize the effect of range on ping time for each delay separately with variability.

    Parameters:
    df (DataFrame): The DataFrame containing the data.
    target (list): List of target sensor IDs to visualize.
    """
    # Group by sensor ID, delay, and range, then calculate the mean and standard deviation of ping time
    grouped_df = df.groupby(['Sensor ID', 'Delay (us)', 'Range (cm)']).agg(
        mean_ping_time=('Ping Time (us)', 'mean'),
        std_ping_time=('Ping Time (us)', 'std')
    ).reset_index()

    target_df = grouped_df[grouped_df['Sensor ID'].isin(target)]
    # Get unique delays
    unique_delays = target_df['Delay (us)'].unique()

    # Define the number of columns for subplots
    num_columns = 2  # 2 columns for the grid
    num_rows = 3  # 3 rows for the grid

    # Create subplots
    fig = make_subplots(rows=num_rows, cols=num_columns, subplot_titles=[f'Delay: {delay} us' for delay in unique_delays])

    for i, delay in enumerate(unique_delays):
        subset_df = target_df[target_df['Delay (us)'] == delay]

        # Get the row and column position for the subplot
        row = (i // num_columns) + 1
        col = (i % num_columns) + 1

        # Adding error bars
        for sensor_id in subset_df['Sensor ID'].unique():
            sensor_data = subset_df[subset_df['Sensor ID'] == sensor_id]
            fig.add_trace(
                go.Scatter(
                    x=sensor_data['Range (cm)'],
                    y=sensor_data['mean_ping_time'],
                    mode='lines+markers',
                    name=f'Sensor {sensor_id}',
                    error_y=dict(
                        type='data',
                        array=sensor_data['std_ping_time'],
                        visible=True
                    )
                ),
                row=row, col=col
            )

        # Plot reference line
        ranges = np.linspace(subset_df['Range (cm)'].min(), subset_df['Range (cm)'].max(), 100)
        reference_ping_times = 57 * ranges
        fig.add_trace(
            go.Scatter(
                x=ranges,
                y=reference_ping_times,
                mode='lines',
                line=dict(color='red', dash='dash'),
                name='Reference Line'
            ),
            row=row, col=col
        )

    fig.update_layout(
        height=1500,  # Adjust height for the grid layout
        width=1500,  # Adjust width for the grid layout
        showlegend=False,
        title_text="Ping Time vs Range for Different Delays"
    )

    fig.show()



def visualize_cluster(df,cluster = 0, simple = True):
    # Load the dataset
    file_path = '../processed_data/all_data_v4-1-1_cleaned_sensor211.csv'
    all_cleaned_df = pd.read_csv(file_path)
    all_cleaned_df = all_cleaned_df.drop("Unnamed: 0",axis=1)
    
    cluster_sensors = df[df["cluster"]==cluster]["Sensor ID"].unique()
    if simple:
        visualize_lineplot_ping_time_with_variability_simple(all_cleaned_df,cluster_sensors)
    else:
        visualize_lineplot_ping_time_with_variability(all_cleaned_df,cluster_sensors)

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def visualize_lineplot_ping_time_with_variability_by_cluster(df, cluster_sensors, delay=None):
    """
    Visualize the effect of range on ping time for each cluster with variability, optionally filtering by delay.

    Parameters:
    df (DataFrame): The DataFrame containing the data.
    cluster_sensors (dict): Dictionary where keys are cluster labels and values are lists of sensor IDs in each cluster.
    delay (int, optional): If specified, only data for this delay will be plotted. Otherwise, all delays are plotted.
    """
    # Group by sensor ID, range, and delay, then calculate the mean and standard deviation of ping time
    grouped_df = df.groupby(['Sensor ID', 'Range (cm)', 'Delay (us)']).agg(
        mean_ping_time=('Ping Time (us)', 'mean'),
        std_ping_time=('Ping Time (us)', 'std')
    ).reset_index()

    # Filter by the specified delay if provided
    if delay is not None:
        grouped_df = grouped_df[grouped_df['Delay (us)'] == delay]

    # Define the number of columns for subplots
    num_clusters = len(cluster_sensors)
    num_columns = 2  # Number of columns for the grid
    num_rows = (num_clusters + num_columns - 1) // num_columns  # Calculate rows based on the number of clusters

    # Create subplots
    fig = make_subplots(rows=num_rows, cols=num_columns, subplot_titles=[f'Cluster {cluster}' for cluster in cluster_sensors.keys()])

    for i, (cluster, sensors) in enumerate(cluster_sensors.items()):
        cluster_df = grouped_df[grouped_df['Sensor ID'].isin(sensors)]

        # Get the row and column position for the subplot
        row = (i // num_columns) + 1
        col = (i % num_columns) + 1

        # Adding error bars
        for sensor_id in sensors:
            sensor_data = cluster_df[cluster_df['Sensor ID'] == sensor_id]
            fig.add_trace(
                go.Scatter(
                    x=sensor_data['Range (cm)'],
                    y=sensor_data['mean_ping_time'],
                    mode='lines+markers',
                    name=f'Sensor {sensor_id}',
                    error_y=dict(
                        type='data',
                        array=sensor_data['std_ping_time'],
                        visible=True
                    )
                ),
                row=row, col=col
            )

        # Plot reference line
        ranges = np.linspace(cluster_df['Range (cm)'].min(), cluster_df['Range (cm)'].max(), 100)
        reference_ping_times = 57 * ranges
        fig.add_trace(
            go.Scatter(
                x=ranges,
                y=reference_ping_times,
                mode='lines',
                line=dict(color='red', dash='dash'),
                name='Reference Line'
            ),
            row=row, col=col
        )

    fig.update_layout(
        height=3000,  # Adjust height for the grid layout
        width=1500,  # Adjust width for the grid layout
        showlegend=False,
        title_text=f"Ping Time vs Range for Different Clusters {delay}us"
    )

    fig.show()

def visualize_cluster_delay(df, delay_pos=4):
    # Load the dataset
    file_path = '../processed_data/all_data_v4-1-1_cleaned_sensor211.csv'
    all_cleaned_df = pd.read_csv(file_path)
    all_cleaned_df = all_cleaned_df.drop("Unnamed: 0", axis=1)
    
    # Dictionary to store sensors grouped by cluster
    cluster_sensors = df.groupby("cluster")["Sensor ID"].apply(list).to_dict()

    delays = [3000,6000,8000,10000,16800]

    visualize_lineplot_ping_time_with_variability_by_cluster(all_cleaned_df, cluster_sensors, delays[delay_pos])



import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def visualize_lineplot_ping_time_with_variability_side_by_side(df, cluster_sensors, delays):
    """
    Visualize the effect of range on ping time for selected clusters and delays side-by-side with variability.

    Parameters:
    df (DataFrame): The DataFrame containing the data.
    cluster_sensors (dict): Dictionary where keys are cluster labels and values are lists of sensor IDs in each cluster.
    delays (list): List of delays to compare across clusters.
    """
    # Group by sensor ID, range, and delay, then calculate the mean and standard deviation of ping time
    grouped_df = df.groupby(['Sensor ID', 'Range (cm)', 'Delay (us)']).agg(
        mean_ping_time=('Ping Time (us)', 'mean'),
        std_ping_time=('Ping Time (us)', 'std')
    ).reset_index()

    # Determine number of rows and columns for subplots
    num_clusters = len(cluster_sensors)
    num_delays = len(delays)
    
    num_columns = num_clusters
    num_rows = num_delays
    
    # Create subplots
    fig = make_subplots(
        rows=num_rows, 
        cols=num_columns, 
        subplot_titles=[f'Cluster {cluster} - Delay {delay} us' for delay in delays for cluster in cluster_sensors.keys()]
    )

    for i, cluster in enumerate(cluster_sensors.keys()):
        sensors = cluster_sensors[cluster]
        cluster_df = grouped_df[grouped_df['Sensor ID'].isin(sensors)]
        
        for j, delay in enumerate(delays):
            delay_df = cluster_df[cluster_df['Delay (us)'] == delay]

            # Get the row and column position for the subplot
            row = j + 1
            col = i + 1

            # Adding error bars
            for sensor_id in sensors:
                sensor_data = delay_df[delay_df['Sensor ID'] == sensor_id]
                fig.add_trace(
                    go.Scatter(
                        x=sensor_data['Range (cm)'],
                        y=sensor_data['mean_ping_time'],
                        mode='lines+markers',
                        name=f'Sensor {sensor_id} (Delay {delay} us)',
                        error_y=dict(
                            type='data',
                            array=sensor_data['std_ping_time'],
                            visible=True
                        )
                    ),
                    row=row, col=col
                )

            # Plot reference line
            ranges = np.linspace(delay_df['Range (cm)'].min(), delay_df['Range (cm)'].max(), 100)
            reference_ping_times = 57 * ranges
            fig.add_trace(
                go.Scatter(
                    x=ranges,
                    y=reference_ping_times,
                    mode='lines',
                    line=dict(color='red', dash='dash'),
                    name='Reference Line'
                ),
                row=row, col=col
            )

    fig.update_layout(
        height=300 * num_rows,  # Adjust height based on the number of delays
        width=400 * num_columns,  # Adjust width based on the number of clusters
        showlegend=False,
        title_text="Side-by-Side Comparison of Clusters Across All Delays"
    )

    fig.show()

def visualize_cluster_delay_side_by_side(df, clusters_to_compare, delays=[3000, 6000, 8000, 10000, 16800]):
    """
    Compare multiple clusters across all specified delays side by side.

    Parameters:
    df (DataFrame): The DataFrame containing the data, including clustering information.
    clusters_to_compare (list): List of cluster labels to compare side-by-side.
    delays (list): List of delays to compare.
    """
    # Load the dataset
    file_path = '../processed_data/all_data_v4-1-1_cleaned_sensor211.csv'
    all_cleaned_df = pd.read_csv(file_path)
    all_cleaned_df = all_cleaned_df.drop("Unnamed: 0",axis=1)

    # Dictionary to store sensors grouped by cluster
    cluster_sensors = {cluster: df[df["cluster"] == cluster]["Sensor ID"].unique() for cluster in clusters_to_compare}

    # Visualize side-by-side comparisons for the selected clusters and delays
    visualize_lineplot_ping_time_with_variability_side_by_side(all_cleaned_df, cluster_sensors, delays)


import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def visualize_sensors_delay_side_by_side(sensors_to_compare, delays=[3000, 6000, 8000, 10000, 16800]):
    """
    Compare multiple sensors across all specified delays side by side.

    Parameters:
    sensors_to_compare (list): List of sensor IDs to compare side-by-side.
    delays (list): List of delays to compare.
    """
    # Load the dataset
    file_path = '../processed_data/all_data_v4-1-1_cleaned_sensor211.csv'
    all_cleaned_df = pd.read_csv(file_path)
    all_cleaned_df = all_cleaned_df.drop("Unnamed: 0", axis=1)

    # Group by sensor ID, range, and delay, then calculate the mean and standard deviation of ping time
    grouped_df = all_cleaned_df.groupby(['Sensor ID', 'Range (cm)', 'Delay (us)']).agg(
        mean_ping_time=('Ping Time (us)', 'mean'),
        std_ping_time=('Ping Time (us)', 'std')
    ).reset_index()

    # Filter the data to include only the sensors of interest
    grouped_df = grouped_df[grouped_df['Sensor ID'].isin(sensors_to_compare)]

    # Determine number of rows and columns for subplots
    num_sensors = len(sensors_to_compare)
    num_delays = len(delays)
    
    num_columns = num_sensors
    num_rows = num_delays
    
    # Create subplots
    subplot_titles = []
    for delay in delays:
        for sensor in sensors_to_compare:
            subplot_titles.append(f'Sensor {sensor} - Delay {delay} us')
    fig = make_subplots(
        rows=num_rows, 
        cols=num_columns, 
        subplot_titles=subplot_titles
    )

    for i, sensor_id in enumerate(sensors_to_compare):
        sensor_df = grouped_df[grouped_df['Sensor ID'] == sensor_id]
        
        for j, delay in enumerate(delays):
            delay_df = sensor_df[sensor_df['Delay (us)'] == delay]

            # Get the row and column position for the subplot
            row = j + 1
            col = i + 1

            # Adding error bars
            sensor_data = delay_df
            fig.add_trace(
                go.Scatter(
                    x=sensor_data['Range (cm)'],
                    y=sensor_data['mean_ping_time'],
                    mode='lines+markers',
                    name=f'Sensor {sensor_id} (Delay {delay} us)',
                    error_y=dict(
                        type='data',
                        array=sensor_data['std_ping_time'],
                        visible=True
                    )
                ),
                row=row, col=col
            )

            # Plot reference line
            if not delay_df.empty:
                ranges = np.linspace(delay_df['Range (cm)'].min(), delay_df['Range (cm)'].max(), 100)
                reference_ping_times = 57 * ranges
                fig.add_trace(
                    go.Scatter(
                        x=ranges,
                        y=reference_ping_times,
                        mode='lines',
                        line=dict(color='red', dash='dash'),
                        name='Reference Line'
                    ),
                    row=row, col=col
                )

    fig.update_layout(
        height=300 * num_rows,  # Adjust height based on the number of delays
        width=400 * num_columns,  # Adjust width based on the number of sensors
        showlegend=False,
        title_text="Side-by-Side Comparison of Sensors Across Delays"
    )

    fig.show()



from scipy.spatial.distance import cdist


def find_and_visualize_closest_sensors(target_sensor_id, n=5, metric='euclidean', delays=[3000, 6000, 8000, 10000, 16800]):
    """
    Find the n closest sensors to a target sensor based on the specified distance metric and visualize them.
    
    Parameters:
    - target_sensor_id (int): The ID of the target sensor.
    - n (int): Number of closest sensors to find.
    - metric (str): Distance metric to use ('euclidean' or 'cosine').
    - delays (list): List of delays to compare.
    """
    # Load the dataset
    file_path = '../processed_data/all_data_v4-1-1_cleaned_sensor211.csv'
    all_cleaned_df = pd.read_csv(file_path)
    all_cleaned_df = all_cleaned_df.drop("Unnamed: 0", axis=1)
    
    # Group by sensor ID, range, and delay, then calculate the mean and standard deviation of ping time
    grouped_df = all_cleaned_df.groupby(['Sensor ID', 'Range (cm)', 'Delay (us)']).agg(
        mean_ping_time=('Ping Time (us)', 'mean'),
        std_ping_time=('Ping Time (us)', 'std')
    ).reset_index()
    
    # Pivot the data to create feature vectors for each sensor
    pivot_df = grouped_df.pivot_table(
        index='Sensor ID', 
        columns=['Delay (us)', 'Range (cm)'], 
        values='mean_ping_time'
    ).fillna(0)
    
    # Ensure the target sensor exists in the data
    if target_sensor_id not in pivot_df.index:
        print(f"Sensor ID {target_sensor_id} not found in the data.")
        return
    
    # Extract feature vectors
    sensor_ids = pivot_df.index.values
    feature_vectors = pivot_df.values
    
    # Get the feature vector for the target sensor
    target_vector = pivot_df.loc[target_sensor_id].values.reshape(1, -1)
    
    # Compute distances
    distances = cdist(target_vector, feature_vectors, metric=metric).flatten()
    
    # Create a DataFrame of distances
    distance_df = pd.DataFrame({
        'Sensor ID': sensor_ids,
        'Distance': distances
    })
    
    # Remove the target sensor from the list
    distance_df = distance_df[distance_df['Sensor ID'] != target_sensor_id]
    
    # Sort by distance and get the n closest sensors
    closest_sensors_df = distance_df.sort_values('Distance').head(n)
    closest_sensor_ids = closest_sensors_df['Sensor ID'].values.tolist()
    
    # Print the IDs of the n closest sensors
    print(f"The {n} closest sensors to Sensor {target_sensor_id} based on {metric} distance are:")
    for idx, row in closest_sensors_df.iterrows():
        print(f"Sensor ID: {row['Sensor ID']}, Distance: {row['Distance']}")
    
    # Include the target sensor in the visualization
    sensors_to_visualize = [target_sensor_id] + closest_sensor_ids
    
    # Use the existing visualization function
    visualize_sensors_delay_side_by_side(sensors_to_visualize, delays)


from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

def visulaize_clustering_all(df,random_state=42, visualization_method='PCA', plot_3d=False):

    # Standardize the features
    df = df.copy()
    sensor_ids = df.index if 'Sensor ID' not in df.columns else df['Sensor ID']
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(df.drop(columns=['Sensor ID']))

    # Visualize the clustering results using PCA or t-SNE
    if visualization_method.upper() == 'PCA':
        n_components = 3 if plot_3d else 2
        pca = PCA(n_components=n_components)
        components = pca.fit_transform(features_scaled)
        explained_variance = pca.explained_variance_ratio_  # Get explained variance ratio
        title = '3D Visualization using PCA' if plot_3d else '2D Visualization using PCA'
        
        # Define axis labels with explained variance for each component
        axis_labels = [f'Component {i+1} ({explained_variance[i]:.2%} Variance)' for i in range(n_components)]

    elif visualization_method.upper() == 'TSNE':
        n_components = 3 if plot_3d else 2
        tsne = TSNE(n_components=n_components, random_state=random_state)
        components = tsne.fit_transform(features_scaled)
        title = '3D Visualization using t-SNE' if plot_3d else '2D Visualization using t-SNE'
        axis_labels = [f'Component {i+1}' for i in range(n_components)]  # t-SNE does not have explained variance

    else:
        raise ValueError("visualization_method should be either 'PCA' or 'TSNE'.")

    # Create a DataFrame for the components
    components_df = pd.DataFrame(components, columns=[f'Component {i+1}' for i in range(n_components)])
    components_df['cluster'] = df['cluster'] 
    components_df['Sensor ID'] = sensor_ids

    # Plot the results
    if plot_3d:
        fig = px.scatter_3d(
            components_df, 
            x='Component 1', 
            y='Component 2', 
            z='Component 3', 
            color='cluster', 
            title=title,
            hover_name='Sensor ID'  # Display Sensor ID on hover
        )
        fig.update_layout(scene=dict(
            xaxis_title=axis_labels[0],
            yaxis_title=axis_labels[1],
            zaxis_title=axis_labels[2]
        ))

    else:
        fig = px.scatter(
            components_df, 
            x='Component 1', 
            y='Component 2', 
            color='cluster', 
            title=title,
            hover_name='Sensor ID'  # Display Sensor ID on hover
        )
        fig.update_layout(
            xaxis_title=axis_labels[0],
            yaxis_title=axis_labels[1]
        )

    fig.show()


def visualize_aggregated_ping_time_with_variability(df, cluster=0, file_path='../processed_data/all_data_v4-1-1_cleaned_sensor211.csv'):
    """
    Visualize the effect of range on ping time aggregated across sensors for each delay, with variability shown as error bars.

    Parameters:
    df (DataFrame): The DataFrame containing clustered sensor data.
    cluster (int): The cluster number to visualize.
    file_path (str): The path to the full dataset for aggregation.
    """
    # Load and prepare data
    all_cleaned_df = pd.read_csv(file_path).drop("Unnamed: 0", axis=1)
    cluster_sensors = df[df["cluster"] == cluster]["Sensor ID"].unique()
    cluster_df = all_cleaned_df[all_cleaned_df['Sensor ID'].isin(cluster_sensors)]
    
    # Group by Delay and Range, then calculate the mean and standard deviation across sensors for Ping Time
    aggregated_df = cluster_df.groupby(['Delay (us)', 'Range (cm)']).agg(
        mean_ping_time=('Ping Time (us)', 'mean'),
        std_ping_time=('Ping Time (us)', 'std')
    ).reset_index()

    # Get unique delays for plotting each delay as a separate subplot
    unique_delays = aggregated_df['Delay (us)'].unique()

    # Create subplots layout based on the number of unique delays
    num_columns = 2  # Customize as needed
    num_rows = -(-len(unique_delays) // num_columns)  # Calculate rows based on number of delays

    fig = make_subplots(rows=num_rows, cols=num_columns, subplot_titles=[f'Delay: {delay} us' for delay in unique_delays])

    for i, delay in enumerate(unique_delays):
        subset_df = aggregated_df[aggregated_df['Delay (us)'] == delay]
        
        # Determine row and column for current subplot
        row = (i // num_columns) + 1
        col = (i % num_columns) + 1

        # Plot the mean line with standard deviation as error bars
        fig.add_trace(
            go.Scatter(
                x=subset_df['Range (cm)'],
                y=subset_df['mean_ping_time'],
                mode='lines+markers',
                name=f'Delay {delay} us',
                error_y=dict(
                    type='data',
                    array=subset_df['std_ping_time'],
                    visible=True
                )
            ),
            row=row, col=col
        )

        # Plot reference line (assuming 57 * range as the reference relationship)
        ranges = np.linspace(subset_df['Range (cm)'].min(), subset_df['Range (cm)'].max(), 100)
        reference_ping_times = 57 * ranges
        fig.add_trace(
            go.Scatter(
                x=ranges,
                y=reference_ping_times,
                mode='lines',
                line=dict(color='red', dash='dash'),
                name='Reference Line'
            ),
            row=row, col=col
        )

    # Update layout for better presentation
    fig.update_layout(
        height=800,  # Adjust height for the grid layout
        width=1200,  # Adjust width for the grid layout
        showlegend=False,  # Set to True if you want a global legend
        title_text=f"Aggregated Ping Time vs Range for Cluster {cluster} Across Delays",
        template="plotly_white"
    )

    fig.show()