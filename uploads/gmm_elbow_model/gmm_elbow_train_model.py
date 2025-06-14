# ==============================
# IMPORTS
# ==============================

# Standard Library Imports (for file handling and script management)
import os
import sys
import time

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
from sklearn.mixture import GaussianMixture

gmm_html_content = ""

def link_to_datatable_html(link, title, filename):
    download_link = f'<a id="gmm_elbow-download-link" download>📥 Download {filename}</a>'
    return f"<h2>{title}</h2>\n" + download_link +  "\n<br/>\n <button id='load-gmm_elbow-table' class='btn btn-primary'>Load GMM Elbow Table</button> <div id='gmm_elbow_output_container'></div> \n\n"

def df_to_datatable_html(df, title, table_id, index):
    df_html = df.to_html(index=index, border=0)
    df_html = df_html.replace('<table class="dataframe">', f'<table id="{table_id}" class="display output_result_tab5" style="width:100%">')
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

df_gmm = df.copy()
df_gmm.loc[:, 'Completeness_Percentage'] = (df_gmm[doc_columns].sum(axis=1) / len(doc_columns)) * 100
weight_factor = 5
df_gmm['Weighted_Completeness'] = df_gmm['Completeness_Percentage'] * weight_factor
df_gmm_for_clustering = df_gmm[doc_columns + ['Weighted_Completeness']]

# ==============================
# DATA SCALING
# ==============================

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_gmm_for_clustering)

# ==============================
# ELBOW METHOD TO FIND BEST K (BIC/AIC)
# ==============================

bics = []
aics = []
fit_times = []
K = range(1, 11)
for k in K:
    start = time.time()
    gmm = GaussianMixture(n_components=k, random_state=42, covariance_type="tied")
    gmm.fit(X_scaled)
    bics.append(gmm.bic(X_scaled))
    aics.append(gmm.aic(X_scaled))
    fit_times.append(time.time() - start)

# Use KneeLocator to find the elbow for BIC
K_range = list(range(2, 11))
kneedle = KneeLocator(K_range, bics[1:], curve='convex', direction='decreasing')
best_k = kneedle.elbow if kneedle.elbow is not None else 3
print(f"Best K found by elbow method (BIC): {best_k}")

# Plot BIC and fit time for each K (manual elbow plot)
fig, ax1 = plt.subplots(figsize=(8, 6))

color_bic = 'tab:blue'
color_time = 'tab:green'

# Plot BIC
ax1.plot(K, bics, marker='o', color=color_bic, label='BIC')
ax1.set_xlabel('Number of Clusters (K)', fontsize=12)
ax1.set_ylabel('BIC', color=color_bic, fontsize=12)
ax1.tick_params(axis='y', labelcolor=color_bic)
ax1.set_xticks(list(K))
ax1.grid(alpha=0.5)

# Mark the best_k found by KneeLocator
ax1.axvline(best_k, color='black', linestyle='--', label=f'Elbow at k={best_k}')

# Plot fit time on secondary y-axis
ax2 = ax1.twinx()
ax2.plot(K, fit_times, marker='s', color=color_time, linestyle='--', label='Fit Time (s)')
ax2.set_ylabel('Fit Time (seconds)', color=color_time, fontsize=12)
ax2.tick_params(axis='y', labelcolor=color_time)

# Combine legends from both axes
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right', fontsize=11)

ax1.set_title('GMM Elbow: BIC & Fit Time vs K', fontsize=14)
plt.tight_layout()
bic_aic_plot_path = os.path.join(script_dir, "gmm_elbow_fit_time.png")
plt.savefig(bic_aic_plot_path, dpi=300, bbox_inches="tight")
plt.close(fig)

# ==============================
# GMM WITH BEST K
# ==============================

gmm = GaussianMixture(n_components=best_k, random_state=42, covariance_type="tied")
df_gmm.loc[:, 'Cluster'] = gmm.fit_predict(X_scaled)
model_output = os.path.join(script_dir, "gmm_model_elbow.pkl")
joblib.dump(gmm, model_output)

# ==============================
# ASSIGN CLUSTER LABELS AS "CLUSTER 1", "CLUSTER 2", ...
# ==============================

df_gmm['Cluster_Label'] = df_gmm['Cluster'].apply(lambda x: f"Cluster {x+1}")
cluster_labels = [f"Cluster {i+1}" for i in range(best_k)]

# ==============================
# EXPORT CLUSTERED DATA
# ==============================

output_file = os.path.join(script_dir, "gmm_elbow_output.csv")
df_gmm.to_csv(output_file)
gmm_html_content += link_to_datatable_html("http://${serverIP}:3000/uploads/gmm_elbow_model/gmm_elbow_output.csv", "GMM Elbow Output", "gmm_elbow_output.csv")

# ==============================
# VISUALIZE CLUSTERING RESULTS
# ==============================

plt.figure(figsize=(10, 6))
for label in cluster_labels:
    subset = df_gmm[df_gmm['Cluster_Label'] == label]
    plt.scatter(subset.index, subset['Completeness_Percentage'], label=label, s=50)
plt.title('GMM Elbow Clustering of Document Completeness (No Grouping)', fontsize=16)
plt.xlabel('Index', fontsize=14)
plt.ylabel('Completeness Percentage', fontsize=14)
plt.xticks([], [])
plt.legend(title='Cluster Label', fontsize=12)
plt.grid(alpha=0.5)
plt.tight_layout()
cluster_output = os.path.join(script_dir, "gmm_elbow_clusters.png")
plt.savefig(cluster_output, dpi=300, bbox_inches="tight")
plt.close()

# ==============================
# CLUSTERING METRICS
# ==============================

silhouette = silhouette_score(X_scaled, df_gmm['Cluster'])
calinski_harabasz = calinski_harabasz_score(X_scaled, df_gmm['Cluster'])
davies_bouldin = davies_bouldin_score(X_scaled, df_gmm['Cluster'])

metrics_dict = {
    "Metric": ["Silhouette Score", "Calinski-Harabasz Index", "Davies-Bouldin Index"],
    "Value": [silhouette, calinski_harabasz, davies_bouldin]
}
metrics_df = pd.DataFrame(metrics_dict)
metrics_file = os.path.join(script_dir, "gmm_elbow_metrics.csv")
metrics_df.to_csv(metrics_file, index=False)
gmm_html_content += df_to_datatable_html(metrics_df, "GMM Elbow Metrics", "gmm_elbow_metrics", False)

# ==============================
# PCA VISUALIZATION
# ==============================

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
custom_cmap = ListedColormap(matplotlib.colormaps['tab10'].colors[:best_k])
plt.figure(figsize=(10, 8))
scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=df_gmm['Cluster'], cmap=custom_cmap, edgecolors='k', s=50)
gmm_centroids = gmm.means_ if hasattr(gmm, "means_") else np.zeros((best_k, X_scaled.shape[1]))
gmm_centroids_pca = pca.transform(gmm_centroids)
plt.scatter(gmm_centroids_pca[:, 0], gmm_centroids_pca[:, 1], marker='X', s=300, c='black', edgecolors='white', label='Centroids')
for i, label in enumerate(cluster_labels):
    plt.text(gmm_centroids_pca[i, 0], gmm_centroids_pca[i, 1], label, fontsize=12, weight='bold')
plt.title('GMM Elbow Clustering with Cluster Areas (2D PCA)', fontsize=16)
plt.xlabel('PCA Component 1', fontsize=14)
plt.ylabel('PCA Component 2', fontsize=14)
plt.colorbar(scatter, label='Cluster')
plt.legend()
plt.tight_layout()
pca_output = os.path.join(script_dir, "gmm_elbow_pca.png")
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
    return df_to_datatable_html(cluster_count_sorted, f"GMM Elbow Group By {group_col}", report_name.replace('.csv', ''), True)

gmm_html_content += group_and_report(df_gmm, 'UNIT KERJA', "gmm_elbow_best_unit_kerja_report.csv")
gmm_html_content += group_and_report(df_gmm, 'TINGKAT', "gmm_elbow_best_tingkat_report.csv")
gmm_html_content += group_and_report(df_gmm, 'LOKASI', "gmm_elbow_best_lokasi_report.csv")
gmm_html_content += group_and_report(df_gmm, 'PROVINSI', "gmm_elbow_best_provinsi_report.csv")
gmm_html_content += group_and_report(df_gmm, 'STATUS', "gmm_elbow_best_status_report.csv")
gmm_html_content += group_and_report(df_gmm, 'JENIS KELAMIN', "gmm_elbow_best_jenis_kelamin_report.csv")

# ==============================
# CLOSE HTML AND SAVE
# ==============================

html_log_file = os.path.join(script_dir, "gmm_elbow_html_results.txt")
with open(html_log_file, "w", encoding="utf-8") as f:
    f.write(gmm_html_content)

print(f"All DataFrames saved as HTML in: {html_log_file}")
