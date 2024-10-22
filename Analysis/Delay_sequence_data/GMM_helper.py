import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from clustering_helper import average_variability_metrics


def tune_gmm(data, n_components_range=range(1, 15), criterion='AIC'):
    """
    Perform hyperparameter tuning for a Gaussian Mixture Model (GMM),
    store the results in a DataFrame, visualize the results, and return the best model.

    Parameters:
    - data: pd.DataFrame - The input data for GMM clustering.
    - n_components_range: range - The range of number of components to try.
    - criterion: str - The criterion to use for selecting the best model ('AIC' or 'BIC').

    Returns:
    - best_model: GaussianMixture - The best GMM model based on the chosen criterion.
    - results_df: pd.DataFrame - The DataFrame containing AIC and BIC values for each model.
    """
    
    # Standardize the features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(data)

    # Create lists to store the results
    aic_values = []
    bic_values = []
    n_components_list = []

    # Loop over the range of components
    for n_components in n_components_range:
        gmm = GaussianMixture(n_components=n_components, random_state=42)
        gmm.fit(features_scaled)
        
        aic = gmm.aic(features_scaled)
        bic = gmm.bic(features_scaled)
        
        aic_values.append(aic)
        bic_values.append(bic)
        n_components_list.append(n_components)

    # Create a DataFrame to store the results
    results_df = pd.DataFrame({
        'n_components': n_components_list,
        'AIC': aic_values,
        'BIC': bic_values
    })

    # Plot AIC and BIC values
    fig = px.line(results_df, x='n_components', y=['AIC', 'BIC'], 
                  title='AIC and BIC values for different number of components',
                  labels={'value': 'Score', 'n_components': 'Number of Components'},
                  markers=True)
    fig.show()

    # Find the best model based on the chosen criterion
    if criterion == 'AIC':
        best_index = results_df['AIC'].idxmin()
    elif criterion == 'BIC':
        best_index = results_df['BIC'].idxmin()
    else:
        raise ValueError("Criterion must be either 'AIC' or 'BIC'")

    best_model = GaussianMixture(n_components=results_df.loc[best_index, 'n_components'], random_state=42)
    best_model.fit(features_scaled)

    return best_model, results_df



def train_GMM(df, n_components=5, random_state=42, visualization_method='PCA', plot_3d=False):
    """
    Train a Gaussian Mixture Model (GMM) on the given dataframe, predict clusters, and visualize the results.

    Parameters:
    df (DataFrame): The DataFrame containing the features to cluster.
    n_components (int): The number of clusters/components for the GMM.
    random_state (int): Random state for reproducibility.
    visualization_method (str): The method for visualization ('PCA' or 'TSNE').
    plot_3d (bool): Whether to generate a 3D plot. If False, a 2D plot will be generated.

    Returns:
    DataFrame: The original DataFrame with an additional column for cluster labels.
    GaussianMixture: The fitted GMM model.
    """

    # Standardize the features
    df = df.copy()
    sensor_ids = df.index if 'Sensor ID' not in df.columns else df['Sensor ID']
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(df.drop(columns=['Sensor ID']))

    # Fit a Gaussian Mixture Model
    gmm = GaussianMixture(n_components=n_components, random_state=random_state)
    gmm.fit(features_scaled)

    # Predict cluster labels
    cluster_labels = gmm.predict(features_scaled)
    df['cluster'] = cluster_labels

    # Calculate Silhouette Score
    silhouette_avg = silhouette_score(features_scaled, cluster_labels)
    

    print("============ Distribution of Sensors in each Cluster ============")
    print(df.groupby(["cluster"])["Sensor ID"].count())

    # Evaluate the model using BIC and AIC
    bic = gmm.bic(features_scaled)
    aic = gmm.aic(features_scaled)

    print(f"BIC: {bic}")
    print(f"AIC: {aic}")
    print(f"Silhouette Score: {silhouette_avg:.4f}")

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

    return df, gmm



def search_gmm_weighted_avg(df, data, n_components_range=range(2, 20)):
    for i in n_components_range:
        # Standardize the features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(df)

        # Fit a Gaussian Mixture Model
        gmm = GaussianMixture(n_components=i, random_state=42)
        gmm.fit(features_scaled)

        # Predict cluster labels
        cluster_labels = gmm.predict(features_scaled)
        df['cluster'] = cluster_labels

        # Compute silhouette score
        sil_score = silhouette_score(features_scaled, cluster_labels)

        # Compute your custom metrics
        results_df, weighted_avg_outliers_score, weighted_avg_std_ping_time_score = average_variability_metrics(df, data)

        print(f"{i}-Weighted average of variability score: {weighted_avg_std_ping_time_score} Outlier score: {weighted_avg_outliers_score} Silhouette Score: {sil_score:.4f}")
