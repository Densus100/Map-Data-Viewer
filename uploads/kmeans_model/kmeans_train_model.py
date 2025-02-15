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

# Machine Learning & Preprocessing Imports
from sklearn.decomposition import PCA
import numpy as np
from sklearn.preprocessing import StandardScaler
from matplotlib.colors import ListedColormap
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.cluster import KMeans  # K-Means clustering algorithm
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay
)



# kmeans_html_content = """
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>K-Means Clustering Results</title>
#     <link rel="stylesheet" href="https://cdn.datatables.net/1.13.4/css/jquery.dataTables.min.css">
#     <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
#     <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
#     <script>
#         $(document).ready(function() {
#             $('table').DataTable();
#         });
#     </script>
# </head>
# <body>
# <h1>K-Means Clustering Results</h1>
# """
kmeans_html_content = ""


# Function to convert a DataFrame to a properly formatted DataTable HTML
def df_to_datatable_html(df, title, table_id, index):
    df_html = df.to_html(index=index, border=0)  # Convert DataFrame to HTML, remove border
    df_html = df_html.replace('<table class="dataframe">', f'<table id="{table_id}" class="display output_result" style="width:100%">')  # Fix table formatting
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
    "KARTU ASN VIRTUAL", "NO NPWP", "NO BPJS"
]

# Create a copy of the dataframe to avoid modifying original data
df_kmeans = df.copy()

# Compute the completeness percentage for each row (how many required documents are present)
df_kmeans.loc[:, 'Completeness_Percentage'] = (df_kmeans[doc_columns].sum(axis=1) / len(doc_columns)) * 100

# Apply a weighting factor to emphasize document completeness in clustering
weight_factor = 5  
df_kmeans['Weighted_Completeness'] = df_kmeans['Completeness_Percentage'] * weight_factor

# Select relevant features for clustering
df_kmeans_for_clustering = df_kmeans[doc_columns + ['Weighted_Completeness']]

# ==============================
# DATA SCALING & K-MEANS CLUSTERING
# ==============================

# Normalize feature values to improve clustering performance
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_kmeans_for_clustering)

# Perform K-Means clustering with 3 clusters
kmeans = KMeans(n_clusters=3, random_state=42)
df_kmeans.loc[:, 'Cluster'] = kmeans.fit_predict(X_scaled)  

# Save the trained K-Means model
model_output = os.path.join(script_dir, "kmeans_model.pkl")
joblib.dump(kmeans, model_output)

# ==============================
# ASSIGN CLUSTER LABELS
# ==============================

# Compute median completeness for each cluster to determine cluster meaning
cluster_medians = df_kmeans.groupby('Cluster')['Completeness_Percentage'].median()

# Sort clusters based on completeness levels
sorted_clusters = cluster_medians.sort_values()

# Map cluster indexes to labels ('Low', 'Medium', 'High') based on completeness level
cluster_mapping = {sorted_clusters.index[0]: 'Low', sorted_clusters.index[1]: 'Medium', sorted_clusters.index[2]: 'High'}
df_kmeans['Cluster_Label'] = df_kmeans['Cluster'].map(cluster_mapping)

# ==============================
# EXPORT CLUSTERED DATA
# ==============================

# Save the clustered dataset as a CSV file
# output_file = os.path.join(script_dir, "kmeans_output.csv")
# df_kmeans.to_csv(output_file, index=False)
# kmeans_html_content += f"<h2>K-Means Output</h2>\n{df_kmeans.to_html(index=True)}<br/><br/>\n"
kmeans_html_content += df_to_datatable_html(df_kmeans, "K-Means Output", "kmeans_output", True)


# ==============================
# VISUALIZE CLUSTERING RESULTS
# ==============================

plt.figure(figsize=(10, 6))  # Set figure size

# Loop through each cluster label and plot data points
for label in ['Low', 'Medium', 'High']:
    subset = df_kmeans[df_kmeans['Cluster_Label'] == label]
    plt.scatter(subset.index, subset['Completeness_Percentage'], label=label, s=50)

# Set chart title and labels
plt.title('K-means Clustering of Document Completeness (No Grouping)', fontsize=16)
plt.xlabel('Index', fontsize=14)
plt.ylabel('Completeness Percentage', fontsize=14)

# Remove x-axis labels for better readability
plt.xticks([], [])

plt.legend(title='Cluster Label', fontsize=12)
plt.grid(alpha=0.5)
plt.tight_layout()

# Save the plot as an image
cluster_output = os.path.join(script_dir, "kmeans_clusters.png")
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
df_kmeans['Actual_Label'] = df_kmeans['Completeness_Percentage'].apply(classify_completeness)

# Compute accuracy by comparing predicted clusters with actual labels
correct_predictions = (df_kmeans['Actual_Label'] == df_kmeans['Cluster_Label']).sum()
df_kmeans['Cluster_Label'] = df_kmeans['Cluster'].map(cluster_mapping)


# Compute metrics
accuracy = correct_predictions / len(df_kmeans)
silhouette = silhouette_score(X_scaled, df_kmeans['Cluster'])
calinski_harabasz = calinski_harabasz_score(X_scaled, df_kmeans['Cluster'])
davies_bouldin = davies_bouldin_score(X_scaled, df_kmeans['Cluster'])

# Store results in a dictionary
metrics_dict = {
    "Metric": ["Accuracy", "Silhouette Score", "Calinski-Harabasz Index", "Davies-Bouldin Index"],
    "Value": [accuracy, silhouette, calinski_harabasz, davies_bouldin]
}

# Convert dictionary to DataFrame
metrics_df = pd.DataFrame(metrics_dict)

# Define output file path
# metrics_file = os.path.join(script_dir, "kmeans_metrics.csv")
# metrics_df.to_csv(metrics_file, index=False)
# kmeans_html_content += f"<h2>K-Means Metrics</h2>\n{metrics_df.to_html(index=False)}<br/><br/>\n"
kmeans_html_content += df_to_datatable_html(metrics_df, "K-Means Metrics", "kmeans_metrics", False)


# print("K-Means Metrics:")
# print("Accuracy: ", accuracy)
# print("Silhouette Score:", silhouette)
# print("Calinski-Harabasz Index:", calinski_harabasz)
# print("Davies-Bouldin Index:", davies_bouldin)


# ==============================
# CONFUSION MATRIX & CLASSIFICATION REPORT
# ==============================

# Compute confusion matrix to evaluate clustering performance
conf_matrix = confusion_matrix(
    df_kmeans['Actual_Label'], 
    df_kmeans['Cluster_Label'], 
    labels=['Low', 'Medium', 'High']
)

# Convert confusion matrix to a DataFrame for easier readability
conf_matrix_df = pd.DataFrame(
    conf_matrix, 
    index=['Actual_Low', 'Actual_Medium', 'Actual_High'], 
    columns=['Pred_Low', 'Pred_Medium', 'Pred_High']
)

# Save confusion matrix as a CSV file
# conf_matrix_report = os.path.join(script_dir, "kmeans_confusion_matrix.csv")
# conf_matrix_df.to_csv(conf_matrix_report, index=True)

# Generate and save confusion matrix plot
disp = ConfusionMatrixDisplay(
    confusion_matrix=conf_matrix, 
    display_labels=['Low', 'Medium', 'High']
)
disp.plot(cmap="Blues", values_format='d')
plt.title("Confusion Matrix")

matrix_output = os.path.join(script_dir, "kmeans_confusion_matrix.png")
plt.savefig(matrix_output, dpi=300, bbox_inches='tight')
plt.close()

# Compute classification report (Precision, Recall, F1-Score)
report = classification_report(
    df_kmeans['Actual_Label'], 
    df_kmeans['Cluster_Label'], 
    labels=['Low', 'Medium', 'High'], 
    target_names=['Low', 'Medium', 'High'], 
    output_dict=True
)

# Convert classification report to DataFrame and save as CSV
report_df = pd.DataFrame(report).transpose()
# output_report = os.path.join(script_dir, "kmeans_classification_report.csv")
# report_df.to_csv(output_report, index=True)
# kmeans_html_content += f"<h2>K-Means Classification Report</h2>\n{report_df.to_html(index=True)}<br/><br/>\n"
kmeans_html_content += df_to_datatable_html(report_df, "K-Means Classification Report", "kmeans_classification_report", True)




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

# Transform the centroids into the PCA-reduced 2D space
kmeans_centroids_pca = pca.transform(kmeans.cluster_centers_)

# Compute the decision boundary
# Z = np.array([np.argmin([np.linalg.norm(point - centroid) for centroid in kmeans_centroids_pca])
#               for point in grid_points])
# Z = Z.reshape(xx.shape)

# Get predictions for the mesh grid

# Plot the decision boundary and the background color
# plt.contourf(xx, yy, Z, alpha=0.3, cmap=custom_cmap)  # Background colored by clusters

# Scatter the data points in the reduced 2D PCA space using the existing cluster labels
scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=df_kmeans['Cluster'], cmap=custom_cmap, edgecolors='k', s=50)

# Plot the transformed centroids
plt.scatter(kmeans_centroids_pca[:, 0], kmeans_centroids_pca[:, 1], marker='X', s=300, c='black', edgecolors='white', label='Centroids')

# Add cluster labels (Low, Medium, High) to the boundaries
plt.text(x_min + 0.5, y_max - 3, 'Low', fontsize=12, color='blue', weight='bold')
plt.text(x_min + 0.5, y_max - 2, 'Medium', fontsize=12, color='orange', weight='bold')
plt.text(x_min + 0.5, y_max - 1, 'High', fontsize=12, color='green', weight='bold')

plt.title('K-means Clustering with Decision Boundary and Cluster Areas (2D PCA)', fontsize=16)
plt.xlabel('PCA Component 1', fontsize=14)
plt.ylabel('PCA Component 2', fontsize=14)
plt.colorbar(scatter, label='Cluster')

# Add legend for centroids
plt.legend()
plt.tight_layout()

pca_output = os.path.join(script_dir, "kmeans_pca.png")
plt.savefig(pca_output, dpi=300, bbox_inches='tight')
plt.close()


# =============================================

# Group by 'UNIT KERJA' and get the counts of each cluster label
cluster_count_per_unit = df_kmeans.groupby('UNIT KERJA')['Cluster_Label'].value_counts().unstack(fill_value=0)

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

# cluster_count_per_unit_sorted_report = os.path.join(script_dir, "kmeans_best_unit_kerja_report.csv")
# cluster_count_per_unit_sorted.to_csv(cluster_count_per_unit_sorted_report, index=True)
# kmeans_html_content += f"<h2>K-Means Group By UNIT KERJA</h2>\n{cluster_count_per_unit_sorted.to_html(index=True)}<br/><br/>\n"
kmeans_html_content += df_to_datatable_html(cluster_count_per_unit_sorted, "K-Means Group By UNIT KERJA", "kmeans_best_unit_kerja_report", True)




# ===================================================


# Group by 'LOKASI' and get the counts of each cluster label
cluster_count_per_lokasi = df_kmeans.groupby('LOKASI')['Cluster_Label'].value_counts().unstack(fill_value=0)

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

# cluster_count_per_lokasi_sorted_report = os.path.join(script_dir, "kmeans_best_lokasi_report.csv")
# cluster_count_per_lokasi_sorted.to_csv(cluster_count_per_lokasi_sorted_report, index=True)
# kmeans_html_content += f"<h2>K-Means Group By LOKASI</h2>\n{cluster_count_per_lokasi_sorted.to_html(index=True)}<br/><br/>\n"
kmeans_html_content += df_to_datatable_html(cluster_count_per_lokasi_sorted, "K-Means Group By LOKASI", "kmeans_best_lokasi_report", True)



# ===================================================


# Group by 'STATUS' and get the counts of each cluster label
cluster_count_per_status = df_kmeans.groupby('STATUS')['Cluster_Label'].value_counts().unstack(fill_value=0)

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

# cluster_count_per_status_sorted_report = os.path.join(script_dir, "kmeans_best_status_report.csv")
# cluster_count_per_status_sorted.to_csv(cluster_count_per_status_sorted_report, index=True)
# kmeans_html_content += f"<h2>K-Means Group By STATUS</h2>\n{cluster_count_per_status_sorted.to_html(index=True)}<br/><br/>\n"
kmeans_html_content += df_to_datatable_html(cluster_count_per_status_sorted, "K-Means Group By STATUS", "kmeans_best_status_report", True)





# ===================================================

# Group by 'JENIS KELAMIN' and get the counts of each cluster label
cluster_count_per_jk = df_kmeans.groupby('JENIS KELAMIN')['Cluster_Label'].value_counts().unstack(fill_value=0)

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

# cluster_count_per_jk_sorted_report = os.path.join(script_dir, "kmeans_best_jenis_kelamin_report.csv")
# cluster_count_per_jk_sorted.to_csv(cluster_count_per_jk_sorted_report, index=True)
# kmeans_html_content += f"<h2>K-Means Group By JENIS KELAMIN</h2>\n{cluster_count_per_jk_sorted.to_html(index=True)}<br/><br/>\n"
kmeans_html_content += df_to_datatable_html(cluster_count_per_jk_sorted, "K-Means Group By JENIS KELAMIN", "kmeans_best_jenis_kelamin_report", True)

# Close HTML body and file
# kmeans_html_content += """
# </body>
# </html>
# """


# Define the output file path
html_log_file = os.path.join(script_dir, "kmeans_html_results.txt")
with open(html_log_file, "w", encoding="utf-8") as f:
    f.write(kmeans_html_content)

print(f"All DataFrames saved as HTML in: {html_log_file}")
