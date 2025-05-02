# ==============================
# IMPORTS
# ==============================

# Standard Library Imports (for file handling and script management)
import os
import sys

# Third-Party Library Imports (external dependencies)
import joblib  # For saving and loading models
import pandas as pd  # Data manipulation library
import matplotlib.pyplot as plt  # Data visualization


from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import StandardScaler
from matplotlib.colors import ListedColormap


from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score


# Scikit-Learn Imports (machine learning & preprocessing)
from sklearn.cluster import AgglomerativeClustering  # Hierarchical Clustering algorithm
import scipy.cluster.hierarchy as sch  # Dendrogram plotting
from sklearn.preprocessing import StandardScaler  # Data normalization
from sklearn.metrics import (  # Model evaluation metrics
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay
)


hierarchical_html_content = ""


def link_to_datatable_html(link, title, filename):
    download_link = f'<a id="hierarchical-download-link" download>📥 Download {filename}</a>'
    return f"<h2>{title}</h2>\n" + download_link +  "\n<br/>\n <button id='load-hierarchical-table' class='btn btn-primary'>Load Hierarchical Table</button> <div id='hierarchical_output_container'></div> \n\n"

# Function to convert a DataFrame to a properly formatted DataTable HTML
def df_to_datatable_html(df, title, table_id, index):
    """Convert DataFrame to an HTML DataTable, adding sorting for 'Total_Score' if present."""
    df_html = df.to_html(index=index, border=0)  # Convert DataFrame to HTML, remove border
    df_html = df_html.replace('<table class="dataframe">', f'<table id="{table_id}" class="display output_result_tab3" style="width:100%">')  # Fix table formatting
    return f"<h2>{title}</h2>\n" + df_html +  "\n<br/><br/>\n"


# ==============================
# LOAD DATA
# ==============================

# Get the script's directory and define the data file path (one level up)
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "..", "data_ready.xlsx")

# Try to load the Excel file; exit script if an error occurs
try:
    df = pd.read_excel(file_path, index_col=0)
except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
    sys.exit(1)  # Exit script if file is missing
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)  # Exit script on any other error


# ==============================
# FEATURE ENGINEERING
# ==============================

# Define the list of document columns (features used for clustering)
doc_columns = [
    "FOTO 1/2 BADAN (*)", "FOTO FULL BODY (*)", "AKTA LAHIR (*)", 
    "KTP (*)", "NPWP(*)", "SUMPAH PNS", "NOTA BKN", "SPMT CPNS", 
    "KARTU ASN VIRTUAL", "NO NPWP", "NO BPJS", "NO KK"
]

# Create a copy of the dataframe to avoid modifying original data
df_hierarchical = df.copy()

# Compute the completeness percentage for each row (how many required documents are present)
df_hierarchical.loc[:, 'Completeness_Percentage'] = (df_hierarchical[doc_columns].sum(axis=1) / len(doc_columns)) * 100

# Apply a weighting factor to emphasize document completeness in clustering
weight_factor = 5  
df_hierarchical['Weighted_Completeness'] = df_hierarchical['Completeness_Percentage'] * weight_factor

# Select relevant features for clustering
df_hierarchical_for_clustering = df_hierarchical[doc_columns + ['Weighted_Completeness']]

# ==============================
# DATA SCALING & Hierarchical CLUSTERING
# ==============================

# Normalize feature values to improve clustering performance
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_hierarchical_for_clustering)

plt.figure(figsize=(12, 6))
dendrogram = sch.dendrogram(
    sch.linkage(X_scaled, method='ward'),
    truncate_mode='level',  # Show only the top levels of the hierarchy
    p=5  # Show the last 5 levels of the dendrogram
)

plt.title('Dendrogram (Truncated)', fontsize=16)
plt.xlabel('Samples', fontsize=14)
plt.ylabel('Euclidean Distances', fontsize=14)
plt.tight_layout()
dendrogram_output = os.path.join(script_dir, "hierarchical_dendrogram.png")
plt.savefig(dendrogram_output, dpi=300, bbox_inches="tight")  
# plt.show()

# Perform Hierarchical clustering with 3 clusters
hierarchical = AgglomerativeClustering(n_clusters=3, metric='euclidean', linkage='ward')
df_hierarchical.loc[:, 'Cluster'] = hierarchical.fit_predict(X_scaled)  

# Save the trained Hierarchical model
# model_output = os.path.join(script_dir, "hierarchical_model.pkl")
# joblib.dump(hierarchical, model_output)

# ==============================
# ASSIGN CLUSTER LABELS
# ==============================

# Compute median completeness for each cluster to determine cluster meaning
cluster_medians = df_hierarchical.groupby('Cluster')['Completeness_Percentage'].median()

# Sort clusters based on completeness levels
sorted_clusters = cluster_medians.sort_values()

# Map cluster indexes to labels ('Low', 'Medium', 'High') based on completeness level
cluster_mapping = {sorted_clusters.index[0]: 'Low', sorted_clusters.index[1]: 'Medium', sorted_clusters.index[2]: 'High'}
df_hierarchical['Cluster_Label'] = df_hierarchical['Cluster'].map(cluster_mapping)

# ==============================
# EXPORT CLUSTERED DATA
# ==============================

# Save the clustered dataset as a CSV file
output_file = os.path.join(script_dir, "hierarchical_output.csv")
df_hierarchical.to_csv(output_file)
# hierarchical_html_content += f"<h2>Hierarchical Output</h2>\n{df_hierarchical.to_html(index=True)}<br/><br/>\n"
# hierarchical_html_content += df_to_datatable_html(df_hierarchical, "Hierarchical Output", "hierarchical_output", True)
hierarchical_html_content += link_to_datatable_html("http://${serverIP}:3000/uploads/hierarchical_model/hierarchical_output.csv", "Hierarchical Output", "hierarchical_output.csv")



# ==============================
# VISUALIZE CLUSTERING RESULTS
# ==============================

plt.figure(figsize=(10, 6))  # Set figure size

# Loop through each cluster label and plot data points
for label in ['Low', 'Medium', 'High']:
    subset = df_hierarchical[df_hierarchical['Cluster_Label'] == label]
    plt.scatter(subset.index, subset['Completeness_Percentage'], label=label, s=50)

# Set chart title and labels
plt.title('Hierarchical Clustering of Document Completeness (No Grouping)', fontsize=16)
plt.xlabel('Index', fontsize=14)
plt.ylabel('Completeness Percentage', fontsize=14)

# Remove x-axis labels for better readability
plt.xticks([], [])

plt.legend(title='Cluster Label', fontsize=12)
plt.grid(alpha=0.5)
plt.tight_layout()

# Save the plot as an image
cluster_output = os.path.join(script_dir, "hierarchical_clusters.png")
plt.savefig(cluster_output, dpi=300, bbox_inches="tight")  
plt.close()

# ==============================
# CLASSIFY DOCUMENT COMPLETENESS (GROUND TRUTH)
# ==============================

# Define thresholds for classifying document completeness
medium_threshold = 40  # Documents 40% or more but below 80% are 'Medium'
high_threshold = 80  # Documents 80% or more are 'High'

# Function to classify completeness based on thresholds
def classify_completeness(percentage):
    if percentage > high_threshold:
        return 'High'
    elif percentage > medium_threshold:
        return 'Medium'
    else:
        return 'Low'

# Apply classification function to assign ground truth labels
df_hierarchical['Actual_Label'] = df_hierarchical['Completeness_Percentage'].apply(classify_completeness)

# Compute accuracy by comparing predicted clusters with actual labels
correct_predictions = (df_hierarchical['Actual_Label'] == df_hierarchical['Cluster_Label']).sum()
df_hierarchical['Cluster_Label'] = df_hierarchical['Cluster'].map(cluster_mapping)


# Compute metrics
accuracy = correct_predictions / len(df_hierarchical)
silhouette = silhouette_score(X_scaled, df_hierarchical['Cluster'])
calinski_harabasz = calinski_harabasz_score(X_scaled, df_hierarchical['Cluster'])
davies_bouldin = davies_bouldin_score(X_scaled, df_hierarchical['Cluster'])

# Store results in a dictionary
metrics_dict = {
    "Metric": ["Accuracy", "Silhouette Score", "Calinski-Harabasz Index", "Davies-Bouldin Index"],
    "Value": [accuracy, silhouette, calinski_harabasz, davies_bouldin]
}

# Convert dictionary to DataFrame
metrics_df = pd.DataFrame(metrics_dict)

# Define output file path
metrics_file = os.path.join(script_dir, "hierarchical_metrics.csv")
metrics_df.to_csv(metrics_file, index=False)
# hierarchical_html_content += f"<h2>Hierarchical Metrics</h2>\n{metrics_df.to_html(index=False)}<br/><br/>\n"
hierarchical_html_content += df_to_datatable_html(metrics_df, "Hierarchical Metrics", "hierarchical_metrics", False)


# print("Hierarchical Metrics:")
# print("Accuracy: ", accuracy)
# print("Silhouette Score:", silhouette)
# print("Calinski-Harabasz Index:", calinski_harabasz)
# print("Davies-Bouldin Index:", davies_bouldin)

# ==============================
# CONFUSION MATRIX & CLASSIFICATION REPORT
# ==============================

# Compute confusion matrix to evaluate clustering performance
conf_matrix = confusion_matrix(
    df_hierarchical['Actual_Label'], 
    df_hierarchical['Cluster_Label'], 
    labels=['Low', 'Medium', 'High']
)

# Convert confusion matrix to a DataFrame for easier readability
conf_matrix_df = pd.DataFrame(
    conf_matrix, 
    index=['Actual_Low', 'Actual_Medium', 'Actual_High'], 
    columns=['Pred_Low', 'Pred_Medium', 'Pred_High']
)

# Save confusion matrix as a CSV file
# conf_matrix_report = os.path.join(script_dir, "hierarchical_confusion_matrix.csv")
# conf_matrix_df.to_csv(conf_matrix_report, index=True)

# Generate and save confusion matrix plot
disp = ConfusionMatrixDisplay(
    confusion_matrix=conf_matrix, 
    display_labels=['Low', 'Medium', 'High']
)
disp.plot(cmap="Blues", values_format='d')
plt.title("Confusion Matrix")

matrix_output = os.path.join(script_dir, "hierarchical_confusion_matrix.png")
plt.savefig(matrix_output, dpi=300, bbox_inches='tight')
plt.close()

# Compute classification report (Precision, Recall, F1-Score)
report = classification_report(
    df_hierarchical['Actual_Label'], 
    df_hierarchical['Cluster_Label'], 
    labels=['Low', 'Medium', 'High'], 
    target_names=['Low', 'Medium', 'High'], 
    output_dict=True
)

# Convert classification report to DataFrame and save as CSV
report_df = pd.DataFrame(report).transpose()
output_report = os.path.join(script_dir, "hierarchical_classification_report.csv")
report_df.to_csv(output_report, index=True)
# hierarchical_html_content += f"<h2>Hierarchical Classification Report</h2>\n{report_df.to_html(index=True)}<br/><br/>\n"
hierarchical_html_content += df_to_datatable_html(report_df, "Hierarchical Classification Report", "hierarchical_classification_report", True)




# ================================

# Apply PCA for dimensionality reduction (reduce to 2D)
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# Define custom colors for clusters
custom_cmap = ListedColormap(['blue', 'orange', 'green'])

# Plotting the PCA-reduced clusters
plt.figure(figsize=(10, 8))

# Plot decision boundary by creating a grid of points
x_min, x_max = X_pca[:, 0].min() - 1, X_pca[:, 0].max() + 1
y_min, y_max = X_pca[:, 1].min() - 1, X_pca[:, 1].max() + 1
# xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.1),
#                      np.arange(y_min, y_max, 0.1))
# grid_points = np.c_[xx.ravel(), yy.ravel()]


# Compute the centroids manually as the mean of the points in each cluster
cluster_labels = df_hierarchical['Cluster'].values
unique_labels = np.unique(cluster_labels)

# Compute the mean of each cluster in the original high-dimensional space
hierarchical_centroids = np.array([X_scaled[cluster_labels == label].mean(axis=0) for label in unique_labels])

# Transform the centroids into the PCA-reduced 2D space
hierarchical_centroids_pca = pca.transform(hierarchical_centroids)

# Compute the decision boundary
# Z = np.array([np.argmin([np.linalg.norm(point - centroid) for centroid in hierarchical_centroids_pca])
#               for point in grid_points])
# Z = Z.reshape(xx.shape)

# Get predictions for the mesh grid

# Plot the decision boundary and the background color
# plt.contourf(xx, yy, Z, alpha=0.3, cmap=custom_cmap)  # Background colored by clusters

# Scatter the data points in the reduced 2D PCA space using the existing cluster labels
scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=df_hierarchical['Cluster'], cmap=custom_cmap, edgecolors='k', s=50)

# Plot the transformed centroids
plt.scatter(hierarchical_centroids_pca[:, 0], hierarchical_centroids_pca[:, 1], marker='X', s=300, c='black', edgecolors='white', label='Centroids')

# Add cluster labels (Low, Medium, High) to the boundaries
plt.text(x_min + 0.5, y_max - 3, 'Low', fontsize=12, color='blue', weight='bold')
plt.text(x_min + 0.5, y_max - 2, 'Medium', fontsize=12, color='orange', weight='bold')
plt.text(x_min + 0.5, y_max - 1, 'High', fontsize=12, color='green', weight='bold')

plt.title('Hierarchical Clustering with Decision Boundary and Cluster Areas (2D PCA)', fontsize=16)
plt.xlabel('PCA Component 1', fontsize=14)
plt.ylabel('PCA Component 2', fontsize=14)
plt.colorbar(scatter, label='Cluster')

# Add legend for centroids
plt.legend()
plt.tight_layout()

pca_output = os.path.join(script_dir, "hierarchical_pca.png")
plt.savefig(pca_output, dpi=300, bbox_inches='tight')
plt.close()


# =============================================

# Group by 'UNIT KERJA' and get the counts of each cluster label
cluster_count_per_unit = df_hierarchical.groupby('UNIT KERJA')['Cluster_Label'].value_counts().unstack(fill_value=0)

# Reorder the columns to match 'High', 'Medium', 'Low'
cluster_count_per_unit = cluster_count_per_unit[['High', 'Medium', 'Low']]

cluster_count_per_unit['Total'] = cluster_count_per_unit['High'] + cluster_count_per_unit['Medium'] + cluster_count_per_unit['Low']

# Display the result
# print(cluster_count_per_unit)

# Assign weights to each cluster
weights = {'High': 3, 'Medium': 2, 'Low': 1}

# Calculate weighted score for each data
cluster_count_per_unit['Total_Score'] = (
    cluster_count_per_unit['High'] * weights['High'] +
    cluster_count_per_unit['Medium'] * weights['Medium'] +
    cluster_count_per_unit['Low'] * weights['Low']
)

# Sort by Total_Score in descending order to rank the units
cluster_count_per_unit_sorted = cluster_count_per_unit.sort_values(by='Total_Score', ascending=False)

# Display the results
# print("cluster_count_per_unit_sorted")
# print(cluster_count_per_unit_sorted)

cluster_count_per_unit_sorted_report = os.path.join(script_dir, "hierarchical_best_unit_kerja_report.csv")
cluster_count_per_unit_sorted.to_csv(cluster_count_per_unit_sorted_report, index=True)
# hierarchical_html_content += f"<h2>Hierarchical Group By UNIT KERJA</h2>\n{cluster_count_per_unit_sorted.to_html(index=True)}<br/><br/>\n"
hierarchical_html_content += df_to_datatable_html(cluster_count_per_unit_sorted, "Hierarchical Group By UNIT KERJA", "hierarchical_best_unit_kerja_report", True)


# =============================================

# Group by 'TINGKAT' and get the counts of each cluster label
cluster_count_per_tingkat = df_hierarchical.groupby('TINGKAT')['Cluster_Label'].value_counts().unstack(fill_value=0)

# Reorder the columns to match 'High', 'Medium', 'Low'
cluster_count_per_tingkat = cluster_count_per_tingkat[['High', 'Medium', 'Low']]

cluster_count_per_tingkat['Total'] = cluster_count_per_tingkat['High'] + cluster_count_per_tingkat['Medium'] + cluster_count_per_tingkat['Low']

# Display the result
# print(cluster_count_per_tingkat)

# Assign weights to each cluster
weights = {'High': 3, 'Medium': 2, 'Low': 1}

# Calculate weighted score for each data
cluster_count_per_tingkat['Total_Score'] = (
    cluster_count_per_tingkat['High'] * weights['High'] +
    cluster_count_per_tingkat['Medium'] * weights['Medium'] +
    cluster_count_per_tingkat['Low'] * weights['Low']
)

# Sort by Total_Score in descending order to rank the tingkat
cluster_count_per_tingkat_sorted = cluster_count_per_tingkat.sort_values(by='Total_Score', ascending=False)

# Display the results
# print("cluster_count_per_tingkat_sorted")
# print(cluster_count_per_tingkat_sorted)

cluster_count_per_tingkat_sorted_report = os.path.join(script_dir, "hierarchical_best_tingkat_report.csv")
cluster_count_per_tingkat_sorted.to_csv(cluster_count_per_tingkat_sorted_report, index=True)
# hierarchical_html_content += f"<h2>Hierarchical Group By TINGKAT</h2>\n{cluster_count_per_tingkat_sorted.to_html(index=True)}<br/><br/>\n"
hierarchical_html_content += df_to_datatable_html(cluster_count_per_tingkat_sorted, "Hierarchical Group By TINGKAT", "hierarchical_best_tingkat_report", True)




# ===================================================


# Group by 'LOKASI' and get the counts of each cluster label
cluster_count_per_lokasi = df_hierarchical.groupby('LOKASI')['Cluster_Label'].value_counts().unstack(fill_value=0)

# Reorder the columns to match 'High', 'Medium', 'Low'
cluster_count_per_lokasi = cluster_count_per_lokasi[['High', 'Medium', 'Low']]

# Display the result
# print(cluster_count_per_lokasi)

# Assign weights to each cluster
weights = {'High': 3, 'Medium': 2, 'Low': 1}

# Calculate weighted score for each data
cluster_count_per_lokasi['Total_Score'] = (
    cluster_count_per_lokasi['High'] * weights['High'] +
    cluster_count_per_lokasi['Medium'] * weights['Medium'] +
    cluster_count_per_lokasi['Low'] * weights['Low']
)

# Sort by Total_Score in descending order to rank the units
cluster_count_per_lokasi_sorted = cluster_count_per_lokasi.sort_values(by='Total_Score', ascending=False)

# Display the results
# cluster_count_per_lokasi_sorted
# print("cluster_count_per_lokasi_sorted")
# print(cluster_count_per_lokasi_sorted)

cluster_count_per_lokasi_sorted_report = os.path.join(script_dir, "hierarchical_best_lokasi_report.csv")
cluster_count_per_lokasi_sorted.to_csv(cluster_count_per_lokasi_sorted_report, index=True)
# hierarchical_html_content += f"<h2>Hierarchical Group By LOKASI</h2>\n{cluster_count_per_lokasi_sorted.to_html(index=True)}<br/><br/>\n"
hierarchical_html_content += df_to_datatable_html(cluster_count_per_lokasi_sorted, "Hierarchical Group By LOKASI", "hierarchical_best_lokasi_report", True)



# ===================================================


# Group by 'PROVINSI' and get the counts of each cluster label
cluster_count_per_provinsi = df_hierarchical.groupby('PROVINSI')['Cluster_Label'].value_counts().unstack(fill_value=0)

# Reorder the columns to match 'High', 'Medium', 'Low'
cluster_count_per_provinsi = cluster_count_per_provinsi[['High', 'Medium', 'Low']]

# Display the result
# print(cluster_count_per_provinsi)

# Assign weights to each cluster
weights = {'High': 3, 'Medium': 2, 'Low': 1}

# Calculate weighted score for each data
cluster_count_per_provinsi['Total_Score'] = (
    cluster_count_per_provinsi['High'] * weights['High'] +
    cluster_count_per_provinsi['Medium'] * weights['Medium'] +
    cluster_count_per_provinsi['Low'] * weights['Low']
)

# Sort by Total_Score in descending order to rank the units
cluster_count_per_provinsi_sorted = cluster_count_per_provinsi.sort_values(by='Total_Score', ascending=False)

# Display the results
# cluster_count_per_provinsi_sorted
# print("cluster_count_per_provinsi_sorted")
# print(cluster_count_per_provinsi_sorted)

cluster_count_per_provinsi_sorted_report = os.path.join(script_dir, "hierarchical_best_provinsi_report.csv")
cluster_count_per_provinsi_sorted.to_csv(cluster_count_per_provinsi_sorted_report, index=True)
# hierarchical_html_content += f"<h2>Hierarchical Group By PROVINSI</h2>\n{cluster_count_per_provinsi_sorted.to_html(index=True)}<br/><br/>\n"
hierarchical_html_content += df_to_datatable_html(cluster_count_per_provinsi_sorted, "Hierarchical Group By PROVINSI", "hierarchical_best_provinsi_report", True)



# ===================================================


# Group by 'STATUS' and get the counts of each cluster label
cluster_count_per_status = df_hierarchical.groupby('STATUS')['Cluster_Label'].value_counts().unstack(fill_value=0)

# Reorder the columns to match 'High', 'Medium', 'Low'
cluster_count_per_status = cluster_count_per_status[['High', 'Medium', 'Low']]

# Display the result
# print(cluster_count_per_status)


# Assign weights to each cluster
weights = {'High': 3, 'Medium': 2, 'Low': 1}

# Calculate weighted score for each data
cluster_count_per_status['Total_Score'] = (
    cluster_count_per_status['High'] * weights['High'] +
    cluster_count_per_status['Medium'] * weights['Medium'] +
    cluster_count_per_status['Low'] * weights['Low']
)

# Sort by Total_Score in descending order to rank the units
cluster_count_per_status_sorted = cluster_count_per_status.sort_values(by='Total_Score', ascending=False)

# Display the results
# cluster_count_per_status_sorted
# print("cluster_count_per_status_sorted")
# print(cluster_count_per_status_sorted)

cluster_count_per_status_sorted_report = os.path.join(script_dir, "hierarchical_best_status_report.csv")
cluster_count_per_status_sorted.to_csv(cluster_count_per_status_sorted_report, index=True)
# hierarchical_html_content += f"<h2>Hierarchical Group By STATUS</h2>\n{cluster_count_per_status_sorted.to_html(index=True)}<br/><br/>\n"
hierarchical_html_content += df_to_datatable_html(cluster_count_per_status_sorted, "Hierarchical Group By STATUS", "hierarchical_best_status_report", True)





# ===================================================

# Group by 'JENIS KELAMIN' and get the counts of each cluster label
cluster_count_per_jk = df_hierarchical.groupby('JENIS KELAMIN')['Cluster_Label'].value_counts().unstack(fill_value=0)

# Reorder the columns to match 'High', 'Medium', 'Low'
cluster_count_per_jk = cluster_count_per_jk[['High', 'Medium', 'Low']]

# Display the result
# print(cluster_count_per_jk)

# Assign weights to each cluster
weights = {'High': 3, 'Medium': 2, 'Low': 1}

# Calculate weighted score for each data
cluster_count_per_jk['Total_Score'] = (
    cluster_count_per_jk['High'] * weights['High'] +
    cluster_count_per_jk['Medium'] * weights['Medium'] +
    cluster_count_per_jk['Low'] * weights['Low']
)

# Sort by Total_Score in descending order to rank the units
cluster_count_per_jk_sorted = cluster_count_per_jk.sort_values(by='Total_Score', ascending=False)

# Display the results
# cluster_count_per_jk_sorted
# print("cluster_count_per_jk_sorted")
# print(cluster_count_per_jk_sorted)

cluster_count_per_jk_sorted_report = os.path.join(script_dir, "hierarchical_best_jenis_kelamin_report.csv")
cluster_count_per_jk_sorted.to_csv(cluster_count_per_jk_sorted_report, index=True)
# hierarchical_html_content += f"<h2>Hierarchical Group By JENIS KELAMIN</h2>\n{cluster_count_per_jk_sorted.to_html(index=True)}<br/><br/>\n"
hierarchical_html_content += df_to_datatable_html(cluster_count_per_jk_sorted, "Hierarchical Group By JENIS KELAMIN", "hierarchical_best_jenis_kelamin_report", True)



# Define the output file path
html_log_file = os.path.join(script_dir, "hierarchical_html_results.txt")
with open(html_log_file, "w", encoding="utf-8") as f:
    f.write(hierarchical_html_content)

print(f"All DataFrames saved as HTML in: {html_log_file}")
