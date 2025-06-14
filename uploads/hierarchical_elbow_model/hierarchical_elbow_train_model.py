# ==============================
# IMPORTS
# ==============================

import os
import sys
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from kneed import KneeLocator
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from matplotlib.colors import ListedColormap
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.cluster import AgglomerativeClustering
import scipy.cluster.hierarchy as sch
import time

hierarchical_html_content = ""

def link_to_datatable_html(link, title, filename):
    download_link = f'<a id="hierarchical_elbow-download-link" download>📥 Download {filename}</a>'
    return f"<h2>{title}</h2>\n" + download_link +  "\n<br/>\n <button id='load-hierarchical_elbow-table' class='btn btn-primary'>Load Hierarchical Elbow Table</button> <div id='hierarchical_elbow_output_container'></div> \n\n"

def df_to_datatable_html(df, title, table_id, index):
    df_html = df.to_html(index=index, border=0)
    df_html = df_html.replace('<table class="dataframe">', f'<table id="{table_id}" class="display output_result_tab6" style="width:100%">')
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

df_hier = df.copy()
df_hier.loc[:, 'Completeness_Percentage'] = (df_hier[doc_columns].sum(axis=1) / len(doc_columns)) * 100
weight_factor = 5
df_hier['Weighted_Completeness'] = df_hier['Completeness_Percentage'] * weight_factor
df_hier_for_clustering = df_hier[doc_columns + ['Weighted_Completeness']]

# ==============================
# DATA SCALING
# ==============================

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_hier_for_clustering)

# ==============================
# ELBOW METHOD FOR HIERARCHICAL (DENDROGRAM & LINKAGE DISTANCES)
# ==============================

# Compute linkage matrix for dendrogram and elbow
linkage_matrix = sch.linkage(X_scaled, method='ward')

# Plot dendrogram (truncated)
plt.figure(figsize=(12, 6))
dendrogram = sch.dendrogram(
    linkage_matrix,
    truncate_mode='level',
    p=5
)
plt.title('Dendrogram (Truncated)', fontsize=16)
plt.xlabel('Samples', fontsize=14)
plt.ylabel('Euclidean Distances', fontsize=14)
plt.tight_layout()
dendrogram_output = os.path.join(script_dir, "hierarchical_elbow_dendrogram.png")
plt.savefig(dendrogram_output, dpi=300, bbox_inches="tight")
plt.close()

# Plot linkage distances and fit times (manual elbow plot)
last = linkage_matrix[-10:, 2]
num_clusters = range(1, 11)
reversed_last = last[::-1]

# Find the elbow using KneeLocator
K_range = list(num_clusters)
kneedle = KneeLocator(K_range, reversed_last, curve='convex', direction='decreasing')
best_k = kneedle.elbow if kneedle.elbow is not None else 3

# Calculate fit times for each K
fit_times = []
for k in num_clusters:
    start = time.time()
    AgglomerativeClustering(n_clusters=k, metric='euclidean', linkage='ward').fit(X_scaled)
    fit_times.append(time.time() - start)

fig, ax1 = plt.subplots(figsize=(8, 6))

color_linkage = 'tab:blue'
color_time = 'tab:green'

# Plot linkage distances
ax1.plot(num_clusters, reversed_last, marker='o', color=color_linkage, label='Linkage Distance')
ax1.set_xlabel('Number of Clusters (K)', fontsize=12)
ax1.set_ylabel('Linkage Distance', color=color_linkage, fontsize=12)
ax1.tick_params(axis='y', labelcolor=color_linkage)
ax1.set_xticks(list(num_clusters))
ax1.grid(alpha=0.5)

# Mark the best_k found by KneeLocator
ax1.axvline(best_k, color='black', linestyle='--', label=f'Elbow at k={best_k}')

# Plot fit time on secondary y-axis
ax2 = ax1.twinx()
ax2.plot(num_clusters, fit_times, marker='s', color=color_time, linestyle='--', label='Fit Time (s)')
ax2.set_ylabel('Fit Time (seconds)', color=color_time, fontsize=12)
ax2.tick_params(axis='y', labelcolor=color_time)

# Combine legends from both axes, place at top right
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right', fontsize=11)

ax1.set_title('Hierarchical Elbow: Linkage Distance & Fit Time vs K', fontsize=14)
plt.tight_layout()
elbow_plot_path = os.path.join(script_dir, "hierarchical_elbow_fit_time.png")
plt.savefig(elbow_plot_path, dpi=300, bbox_inches="tight")
plt.close(fig)

print(f"Best K found by elbow method (linkage): {best_k}")

# ==============================
# HIERARCHICAL CLUSTERING WITH BEST K
# ==============================

hierarchical = AgglomerativeClustering(n_clusters=best_k, metric='euclidean', linkage='ward')
df_hier.loc[:, 'Cluster'] = hierarchical.fit_predict(X_scaled)

# ==============================
# ASSIGN CLUSTER LABELS AS "CLUSTER 1", "CLUSTER 2", ...
# ==============================

df_hier['Cluster_Label'] = df_hier['Cluster'].apply(lambda x: f"Cluster {x+1}")
cluster_labels = [f"Cluster {i+1}" for i in range(best_k)]

# ==============================
# EXPORT CLUSTERED DATA
# ==============================

output_file = os.path.join(script_dir, "hierarchical_elbow_output.csv")
df_hier.to_csv(output_file)
hierarchical_html_content += link_to_datatable_html("http://${serverIP}:3000/uploads/hierarchical_elbow_model/hierarchical_elbow_output.csv", "Hierarchical Elbow Output", "hierarchical_elbow_output.csv")

# ==============================
# VISUALIZE CLUSTERING RESULTS
# ==============================

plt.figure(figsize=(10, 6))
for label in cluster_labels:
    subset = df_hier[df_hier['Cluster_Label'] == label]
    plt.scatter(subset.index, subset['Completeness_Percentage'], label=label, s=50)
plt.title('Hierarchical Elbow Clustering of Document Completeness (No Grouping)', fontsize=16)
plt.xlabel('Index', fontsize=14)
plt.ylabel('Completeness Percentage', fontsize=14)
plt.xticks([], [])
plt.legend(title='Cluster Label', fontsize=12)
plt.grid(alpha=0.5)
plt.tight_layout()
cluster_output = os.path.join(script_dir, "hierarchical_elbow_clusters.png")
plt.savefig(cluster_output, dpi=300, bbox_inches="tight")
plt.close()

# ==============================
# CLUSTERING METRICS
# ==============================

silhouette = silhouette_score(X_scaled, df_hier['Cluster'])
calinski_harabasz = calinski_harabasz_score(X_scaled, df_hier['Cluster'])
davies_bouldin = davies_bouldin_score(X_scaled, df_hier['Cluster'])

metrics_dict = {
    "Metric": ["Silhouette Score", "Calinski-Harabasz Index", "Davies-Bouldin Index"],
    "Value": [silhouette, calinski_harabasz, davies_bouldin]
}
metrics_df = pd.DataFrame(metrics_dict)
metrics_file = os.path.join(script_dir, "hierarchical_elbow_metrics.csv")
metrics_df.to_csv(metrics_file, index=False)
hierarchical_html_content += df_to_datatable_html(metrics_df, "Hierarchical Elbow Metrics", "hierarchical_elbow_metrics", False)

# ==============================
# PCA VISUALIZATION
# ==============================

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
custom_cmap = ListedColormap(matplotlib.colormaps['tab10'].colors[:best_k])
plt.figure(figsize=(10, 8))
scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=df_hier['Cluster'], cmap=custom_cmap, edgecolors='k', s=50)
# Compute centroids in original space, then project to PCA
cluster_labels_idx = df_hier['Cluster'].values
unique_labels = np.unique(cluster_labels_idx)
centroids = np.array([X_scaled[cluster_labels_idx == label].mean(axis=0) for label in unique_labels])
centroids_pca = pca.transform(centroids)
plt.scatter(centroids_pca[:, 0], centroids_pca[:, 1], marker='X', s=300, c='black', edgecolors='white', label='Centroids')
for i, label in enumerate(cluster_labels):
    plt.text(centroids_pca[i, 0], centroids_pca[i, 1], label, fontsize=12, weight='bold')
plt.title('Hierarchical Elbow Clustering with Cluster Areas (2D PCA)', fontsize=16)
plt.xlabel('PCA Component 1', fontsize=14)
plt.ylabel('PCA Component 2', fontsize=14)
plt.colorbar(scatter, label='Cluster')
plt.legend()
plt.tight_layout()
pca_output = os.path.join(script_dir, "hierarchical_elbow_pca.png")
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
    return df_to_datatable_html(cluster_count_sorted, f"Hierarchical Elbow Group By {group_col}", report_name.replace('.csv', ''), True)

hierarchical_html_content += group_and_report(df_hier, 'UNIT KERJA', "hierarchical_elbow_best_unit_kerja_report.csv")
hierarchical_html_content += group_and_report(df_hier, 'TINGKAT', "hierarchical_elbow_best_tingkat_report.csv")
hierarchical_html_content += group_and_report(df_hier, 'LOKASI', "hierarchical_elbow_best_lokasi_report.csv")
hierarchical_html_content += group_and_report(df_hier, 'PROVINSI', "hierarchical_elbow_best_provinsi_report.csv")
hierarchical_html_content += group_and_report(df_hier, 'STATUS', "hierarchical_elbow_best_status_report.csv")
hierarchical_html_content += group_and_report(df_hier, 'JENIS KELAMIN', "hierarchical_elbow_best_jenis_kelamin_report.csv")

# ==============================
# CLOSE HTML AND SAVE
# ==============================

html_log_file = os.path.join(script_dir, "hierarchical_elbow_html_results.txt")
with open(html_log_file, "w", encoding="utf-8") as f:
    f.write(hierarchical_html_content)

print(f"All DataFrames saved as HTML in: {html_log_file}")
