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
import matplotlib
from kneed import KneeLocator
from scipy.spatial.distance import cdist
from yellowbrick.cluster import KElbowVisualizer

# Machine Learning & Preprocessing Imports
from sklearn.decomposition import PCA
import numpy as np
from sklearn.preprocessing import StandardScaler
from matplotlib.colors import ListedColormap
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.cluster import KMeans  # K-Means clustering algorithm
# from sklearn.metrics import (
#     confusion_matrix,
#     classification_report,
#     ConfusionMatrixDisplay
# )

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


def link_to_datatable_html(link, title, filename):
    download_link = f'<a id="kmeans_elbow-download-link" download>📥 Download {filename}</a>'
    return f"<h2>{title}</h2>\n" + download_link +  "\n<br/>\n <button id='load-kmeans_elbow-table' class='btn btn-primary'>Load K-Means Elbow Table</button> <div id='kmeans_elbow_output_container'></div> \n\n"

def df_to_datatable_html(df, title, table_id, index):
    df_html = df.to_html(index=index, border=0)
    df_html = df_html.replace('<table class="dataframe">', f'<table id="{table_id}" class="display output_result_tab4" style="width:100%">')
    return f"<h2>{title}</h2>\n" + df_html +  "\n<br/><br/>\n"

# ==============================
# LOAD DATA
# ==============================

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "..", "data_ready.xlsx")

try:
    df = pd.read_excel(file_path, index_col=0)
except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)

# ==============================
# FEATURE ENGINEERING
# ==============================

doc_columns = [
    "FOTO 1/2 BADAN (*)", "FOTO FULL BODY (*)", "AKTA LAHIR (*)",
    "KTP (*)", "NPWP(*)", "SUMPAH PNS", "NOTA BKN", "SPMT CPNS",
    "KARTU ASN VIRTUAL", "NO NPWP", "NO BPJS", "NO KK"
]

df_kmeans = df.copy()
df_kmeans.loc[:, 'Completeness_Percentage'] = (df_kmeans[doc_columns].sum(axis=1) / len(doc_columns)) * 100
weight_factor = 5
df_kmeans['Weighted_Completeness'] = df_kmeans['Completeness_Percentage'] * weight_factor
df_kmeans_for_clustering = df_kmeans[doc_columns + ['Weighted_Completeness']]

# ==============================
# DATA SCALING
# ==============================

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_kmeans_for_clustering)

# ==============================
# ELBOW METHOD TO FIND BEST K (Inertia)
# ==============================

inertias = []
mapping1 = {}
mapping2 = {}
K = range(1, 11)

for k in K:
    kmeanModel = KMeans(n_clusters=k, random_state=42).fit(X_scaled)
    inertias.append(kmeanModel.inertia_)
    mapping2[k] = inertias[-1]


# Use inertia for KneeLocator to find best_k (skip k=1)
K_range = list(range(2, 11))
kneedle = KneeLocator(K_range, inertias[1:], curve='convex', direction='decreasing')
best_k = kneedle.elbow if kneedle.elbow is not None else 3
print(f"Best K found by elbow method: {best_k}")

# Yellowbrick KElbowVisualizer (using inertia)
fig, ax = plt.subplots(figsize=(8, 6))
kmeans_yb = KMeans(random_state=42)
visualizer = KElbowVisualizer(kmeans_yb, k=(2, 11), ax=ax)
visualizer.fit(X_scaled)
kelbow_plot_path = os.path.join(script_dir, "kmeans_elbow_fit_time.png")
visualizer.show(outpath=kelbow_plot_path)
plt.close(fig)

# ==============================
# KMEANS WITH BEST K
# ==============================

kmeans = KMeans(n_clusters=best_k, random_state=42)
df_kmeans.loc[:, 'Cluster'] = kmeans.fit_predict(X_scaled)
model_output = os.path.join(script_dir, "kmeans_model_elbow.pkl")
joblib.dump(kmeans, model_output)

# ==============================
# CLUSTER LABELS AS "CLUSTER 1", "CLUSTER 2", ...
# ==============================

df_kmeans['Cluster_Label'] = df_kmeans['Cluster'].apply(lambda x: f"Cluster {x+1}")
cluster_labels = [f"Cluster {i+1}" for i in range(best_k)]

# ==============================
# EXPORT CLUSTERED DATA
# ==============================

output_file = os.path.join(script_dir, "kmeans_elbow_output.csv")
df_kmeans.to_csv(output_file)
kmeans_html_content += link_to_datatable_html("http://${serverIP}:3000/uploads/kmeans_elbow_model/kmeans_elbow_output.csv", "K-Means Elbow Output", "kmeans_elbow_output.csv")

# ==============================
# VISUALIZE CLUSTERING RESULTS
# ==============================

plt.figure(figsize=(10, 6))
for label in cluster_labels:
    subset = df_kmeans[df_kmeans['Cluster_Label'] == label]
    plt.scatter(subset.index, subset['Completeness_Percentage'], label=label, s=50)
plt.title('K-means Elbow Clustering of Document Completeness (No Grouping)', fontsize=16)
plt.xlabel('Index', fontsize=14)
plt.ylabel('Completeness Percentage', fontsize=14)
plt.xticks([], [])
plt.legend(title='Cluster Label', fontsize=12)
plt.grid(alpha=0.5)
plt.tight_layout()
cluster_output = os.path.join(script_dir, "kmeans_elbow_clusters.png")
plt.savefig(cluster_output, dpi=300, bbox_inches="tight")
plt.close()

# ==============================
# CLUSTERING METRICS
# ==============================

silhouette = silhouette_score(X_scaled, df_kmeans['Cluster'])
calinski_harabasz = calinski_harabasz_score(X_scaled, df_kmeans['Cluster'])
davies_bouldin = davies_bouldin_score(X_scaled, df_kmeans['Cluster'])

metrics_dict = {
    "Metric": ["Silhouette Score", "Calinski-Harabasz Index", "Davies-Bouldin Index"],
    "Value": [silhouette, calinski_harabasz, davies_bouldin]
}
metrics_df = pd.DataFrame(metrics_dict)
metrics_file = os.path.join(script_dir, "kmeans_elbow_metrics.csv")
metrics_df.to_csv(metrics_file, index=False)
kmeans_html_content += df_to_datatable_html(metrics_df, "K-Means Elbow Metrics", "kmeans_elbow_metrics", False)

# ==============================
# PCA VISUALIZATION
# ==============================

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
custom_cmap = ListedColormap(matplotlib.colormaps['tab10'].colors[:best_k])
plt.figure(figsize=(10, 8))
scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=df_kmeans['Cluster'], cmap=custom_cmap, edgecolors='k', s=50)
kmeans_centroids_pca = pca.transform(kmeans.cluster_centers_)
plt.scatter(kmeans_centroids_pca[:, 0], kmeans_centroids_pca[:, 1], marker='X', s=300, c='black', edgecolors='white', label='Centroids')
for i, label in enumerate(cluster_labels):
    plt.text(kmeans_centroids_pca[i, 0], kmeans_centroids_pca[i, 1], label, fontsize=12, weight='bold')
plt.title('K-means Clustering with Cluster Areas (2D PCA)', fontsize=16)
plt.xlabel('PCA Component 1', fontsize=14)
plt.ylabel('PCA Component 2', fontsize=14)
plt.colorbar(scatter, label='Cluster')
plt.legend()
plt.tight_layout()
pca_output = os.path.join(script_dir, "kmeans_elbow_pca.png")
plt.savefig(pca_output, dpi=300, bbox_inches='tight')
plt.close()

# ==============================
# GROUP BY REPORTS (DYNAMIC CLUSTER LABELS)
# ==============================

def group_and_report(df, group_col, report_name):
    cluster_count = df.groupby(group_col)['Cluster_Label'].value_counts().unstack(fill_value=0)
    cluster_count = cluster_count.reindex(columns=cluster_labels, fill_value=0)
    cluster_count['Total'] = cluster_count[cluster_labels].sum(axis=1)
    # Assign weights: Cluster 1 = best, Cluster 2 = next, etc.
    weights = {label: best_k - i for i, label in enumerate(cluster_labels)}
    cluster_count['Total_Score'] = sum(cluster_count[label] * weights[label] for label in cluster_labels)
    cluster_count_sorted = cluster_count.sort_values(by='Total_Score', ascending=False)
    report_path = os.path.join(script_dir, report_name)
    cluster_count_sorted.to_csv(report_path, index=True)
    return df_to_datatable_html(cluster_count_sorted, f"K-Means Elbow Group By {group_col}", report_name.replace('.csv', ''), True)

kmeans_html_content += group_and_report(df_kmeans, 'UNIT KERJA', "kmeans_elbow_best_unit_kerja_report.csv")
kmeans_html_content += group_and_report(df_kmeans, 'TINGKAT', "kmeans_elbow_best_tingkat_report.csv")
kmeans_html_content += group_and_report(df_kmeans, 'LOKASI', "kmeans_elbow_best_lokasi_report.csv")
kmeans_html_content += group_and_report(df_kmeans, 'PROVINSI', "kmeans_elbow_best_provinsi_report.csv")
kmeans_html_content += group_and_report(df_kmeans, 'STATUS', "kmeans_elbow_best_status_report.csv")
kmeans_html_content += group_and_report(df_kmeans, 'JENIS KELAMIN', "kmeans_elbow_best_jenis_kelamin_report.csv")

# ==============================
# CLOSE HTML AND SAVE
# ==============================

# kmeans_html_content += """
# </body>
# </html>
# """

html_log_file = os.path.join(script_dir, "kmeans_elbow_html_results.txt")
with open(html_log_file, "w", encoding="utf-8") as f:
    f.write(kmeans_html_content)

print(f"All DataFrames saved as HTML in: {html_log_file}")

# ==============================
# (OPTIONAL) CLASSIFY DOCUMENT COMPLETENESS (GROUND TRUTH) FOR EVALUATION
# ==============================

# # Define thresholds for classifying document completeness
# medium_threshold = 40
# high_threshold = 80

# def classify_completeness(percentage):
#     if percentage > high_threshold:
#         return 'High'
#     elif percentage > medium_threshold:
#         return 'Medium'
#     else:
#         return 'Low'

# df_kmeans['Actual_Label'] = df_kmeans['Completeness_Percentage'].apply(classify_completeness)

# # Map each cluster to the most common Actual_Label in that cluster
# cluster_to_actual = (
#     df_kmeans.groupby('Cluster_Label')['Actual_Label']
#     .agg(lambda x: x.value_counts().index[0])
#     .to_dict()
# )
# df_kmeans['Predicted_Label'] = df_kmeans['Cluster_Label'].map(cluster_to_actual)

# labels = cluster_labels  # ['Cluster 1', 'Cluster 2', ..., 'Cluster N']

# # Compute confusion matrix to evaluate clustering performance
# conf_matrix = confusion_matrix(
#     df_kmeans['Cluster_Label'],
#     df_kmeans['Predicted_Label'],
#     labels=labels
# )

# # Convert confusion matrix to a DataFrame for easier readability
# conf_matrix_df = pd.DataFrame(
#     conf_matrix,
#     index=[f'Actual_{label}' for label in labels],
#     columns=[f'Pred_{label}' for label in labels]
# )

# # Save confusion matrix as a CSV file
# conf_matrix_report = os.path.join(script_dir, "kmeans_elbow_confusion_matrix.csv")
# conf_matrix_df.to_csv(conf_matrix_report, index=True)

# # Generate and save confusion matrix plot
# disp = ConfusionMatrixDisplay(
#     confusion_matrix=conf_matrix,
#     display_labels=labels
# )
# disp.plot(cmap="Blues", values_format='d')
# plt.title("Confusion Matrix")
# matrix_output = os.path.join(script_dir, "kmeans_elbow_confusion_matrix.png")
# plt.savefig(matrix_output, dpi=300, bbox_inches='tight')
# plt.close()

# # Compute classification report (Precision, Recall, F1-Score)
# report = classification_report(
#     df_kmeans['Cluster_Label'],
#     df_kmeans['Predicted_Label'],
#     labels=labels,
#     target_names=labels,
#     output_dict=True,
#     zero_division=0  # <--- add this parameter
# )

# # Convert classification report to DataFrame and save as CSV
# report_df = pd.DataFrame(report).transpose()
# output_report = os.path.join(script_dir, "kmeans_elbow_classification_report.csv")
# report_df.to_csv(output_report, index=True)
# kmeans_html_content += df_to_datatable_html(report_df, "K-Means Elbow Classification Report", "kmeans_elbow_classification_report", True)
