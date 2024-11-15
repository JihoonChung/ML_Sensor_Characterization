import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from clustering_helper import average_variability_metrics

def tune_and_visualize_kmeans(data, n_clusters_range=range(1, 11), plot_3d=False):
    """
    Perform hyperparameter tuning for KMeans clustering,
    store the results in a DataFrame, visualize the results, and return the best model.
    Optionally, create an interactive 3D plot of the clustering results.

    Parameters:
    - data: pd.DataFrame - The input data for KMeans clustering.
    - n_clusters_range: range - The range of number of clusters to try.
    - plot_3d: bool - Whether to create an interactive 3D plot of the clustering results.

    Returns:
    - best_model: KMeans - The best KMeans model based on the inertia criterion.
    - results_df: pd.DataFrame - The DataFrame containing inertia values for each model.
    """
    
    # Drop the target column if it's present
    if 'target' in data.columns:
        data = data.drop('target', axis=1)

    # Standardize the features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(data)

    # Create lists to store the results
    inertia_values = []
    n_clusters_list = []

    # Loop over the range of clusters
    for n_clusters in n_clusters_range:
        kmeans = KMeans(n_clusters=n_clusters, n_init='auto',random_state=42)
        kmeans.fit(features_scaled)
        
        inertia = kmeans.inertia_
        
        inertia_values.append(inertia)
        n_clusters_list.append(n_clusters)

    # Create a DataFrame to store the results
    results_df = pd.DataFrame({
        'n_clusters': n_clusters_list,
        'Inertia': inertia_values
    })

    # Plot the inertia values
    fig = px.line(results_df, x='n_clusters', y='Inertia', 
                  title='Inertia values for different number of clusters',
                  labels={'Inertia': 'Inertia', 'n_clusters': 'Number of Clusters'},
                  markers=True)
    fig.show()

    # Find the best model based on the inertia (elbow method)
    best_index = results_df['Inertia'].idxmin()
    best_n_clusters = results_df.loc[best_index, 'n_clusters']
    best_model = KMeans(n_clusters=best_n_clusters, random_state=42)
    best_model.fit(features_scaled)

    # Optionally, create an interactive 3D plot of the clustering results
    if plot_3d:
        if features_scaled.shape[1] < 3:
            raise ValueError("The dataset must have at least 3 features for a 3D plot.")
        
        # Predict cluster labels
        cluster_labels = best_model.predict(features_scaled)
        data['cluster'] = cluster_labels
        
        # Create 3D scatter plot
        fig_3d = px.scatter_3d(
            data, 
            x=features_scaled[:, 0], 
            y=features_scaled[:, 1], 
            z=features_scaled[:, 2], 
            color='cluster',
            title='KMeans Clustering Results in 3D',
            labels={'x': 'Feature 1', 'y': 'Feature 2', 'z': 'Feature 3'}
        )
        fig_3d.show()

    return best_model, results_df
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score
import plotly.express as px
from joblib import dump, load

def train_KMeans(df, n_clusters=5, random_state=42, visualization_method='PCA', plot_3d=False):
    """
    Train a KMeans model on the given dataframe, predict clusters, and visualize the results.

    Parameters:
    df (DataFrame): The DataFrame containing the features to cluster.
    n_clusters (int): The number of clusters for KMeans.
    random_state (int): Random state for reproducibility.
    visualization_method (str): The method for visualization ('PCA' or 'TSNE').
    plot_3d (bool): Whether to generate a 3D plot. If False, a 2D plot will be generated.

    Returns:
    DataFrame: The original DataFrame with an additional column for cluster labels.
    KMeans: The fitted KMeans model.
    """

    # Standardize the features
    df = df.copy()
    sensor_ids = df.index if 'Sensor ID' not in df.columns else df['Sensor ID']
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(df.drop(columns=['Sensor ID']))
    #dump(scaler, "best_models/final/scaler_final.joblib")

    # Fit a KMeans model
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
    kmeans.fit(features_scaled)

    # Predict cluster labels
    cluster_labels = kmeans.predict(features_scaled)
    df['cluster'] = cluster_labels

    # Calculate Silhouette Score
    silhouette_avg = silhouette_score(features_scaled, cluster_labels)
    

    print("============ Distribution of Sensors in each Cluster ============")
    print(df.groupby(["cluster"])["Sensor ID"].count())

    # Evaluate the model using inertia
    inertia = kmeans.inertia_
    print(f"Inertia: {inertia}")
    print(f"Silhouette Score: {silhouette_avg:.4f}")

    # Assuming 'all_cleaned_df' is your cleaned DataFrame with all necessary data
    file_path = '../processed_data/all_data_v4-1-1_cleaned_sensor211.csv'
    all_cleaned_df = pd.read_csv(file_path)
    all_cleaned_df = all_cleaned_df.drop("Unnamed: 0",axis=1)
    results_df, weighted_avg_count_outliers_score, weighted_avg_std_ping_time_score = average_variability_metrics(df, all_cleaned_df)
    print("Custom Scores:")
    print(f"Weighted Average Count of Outliers Score: {weighted_avg_count_outliers_score}")
    print(f"Weighted Average Standard Deviation of Ping Time Score: {weighted_avg_std_ping_time_score}")

    

    # Visualize the clustering results using PCA or t-SNE
    if visualization_method.upper() == 'PCA':
        n_components = 3 if plot_3d else 2
        pca = PCA(n_components=n_components)
        components = pca.fit_transform(features_scaled)
        title = '3D Visualization using PCA' if plot_3d else '2D Visualization using PCA'
    elif visualization_method.upper() == 'TSNE':
        n_components = 3 if plot_3d else 2
        tsne = TSNE(n_components=n_components, random_state=random_state)
        components = tsne.fit_transform(features_scaled)
        title = '3D Visualization using t-SNE' if plot_3d else '2D Visualization using t-SNE'
    else:
        raise ValueError("visualization_method should be either 'PCA' or 'TSNE'.")

    # Create a DataFrame for the components
    components_df = pd.DataFrame(components, columns=[f'Component {i+1}' for i in range(n_components)])
    components_df['cluster'] = cluster_labels
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
    else:
        fig = px.scatter(
            components_df, 
            x='Component 1', 
            y='Component 2', 
            color='cluster', 
            title=title,
            hover_name='Sensor ID'  # Display Sensor ID on hover
        )
    
    fig.show()

    return df, kmeans, scaler

# Example usage:
# df, kmeans = train_KMeans(df, n_clusters=5, random_state=42, visualization_method='PCA', plot_3d=True)
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def search_kmeans_weighted_avg(df, data, n_components_range=range(2, 20)):
    """
    Perform KMeans clustering with a range of components (clusters), 
    calculate weighted average outlier and standard deviation scores, 
    and the silhouette score for each configuration.

    Parameters:
    df (DataFrame): DataFrame containing the features for clustering.
    data (DataFrame): Additional data to calculate the variability and outlier metrics.
    n_components_range (range): Range of cluster numbers to try for KMeans.

    Returns:
    None: Prints the weighted average scores and silhouette score for each number of clusters.
    """

    for i in n_components_range:
        # Standardize the features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(df)

        # Fit a KMeans model
        kmeans = KMeans(n_clusters=i, n_init='auto', random_state=42)
        kmeans.fit(features_scaled)

        # Predict cluster labels
        cluster_labels = kmeans.predict(features_scaled)
        df['cluster'] = cluster_labels

        # Calculate silhouette score
        sil_score = silhouette_score(features_scaled, cluster_labels)

        # Calculate custom metrics
        results_df, weighted_avg_outliers_score, weighted_avg_std_ping_time_score = average_variability_metrics(df, data)
        
        # Print weighted average variability and outlier scores
        print(f"{i}-Weighted average of variability score: {weighted_avg_std_ping_time_score} Outlier score: {weighted_avg_outliers_score} Silhouette Score: {sil_score:.4f}")
