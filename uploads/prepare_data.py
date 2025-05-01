import pandas as pd
import os

pd.set_option('future.no_silent_downcasting', True)
# Assuming your xlsx file is in your Google Drive, replace with actual path
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir,"uploaded_file.xlsx")

try:
  df = pd.read_excel(file_path, index_col=1)
#   print(df.head()) # Print the first few rows to verify
except FileNotFoundError:
  print(f"Error: File not found at {file_path}")
except Exception as e:
  print(f"An error occurred: {e}")


# Replace '√' with 1 and empty/NaN values with 0
df = df.replace('√', 1).infer_objects(copy=False)
df = df.fillna(0)

# Strip leading and trailing spaces from all column names
df.columns = df.columns.str.strip()
df.columns = df.columns.str.upper()

# Verify the column names after stripping spaces
# print(df.columns)

# # Remove rows where 'LOKASI' is 'Jakarta Pusat'
# df = df[df['LOKASI'] != 'Jakarta Pusat']

df = df.drop(columns=['NAMA', 'NIP'], errors='ignore')



# ================================================================

# # Calculate counts for each UNIT KERJA
# unit_kerja_counts = df['UNIT KERJA'].value_counts()

# # Determine the threshold using the formula (mean - standard deviation)
# threshold = unit_kerja_counts.mean() - unit_kerja_counts.std()

# proportion = 0.005  # For example, 0.5% of the total rows
# total_rows = df.shape[0]
# threshold = total_rows * proportion

# # Step 2: Filter out UNIT KERJA with counts below the threshold
# unit_kerja_counts = df['UNIT KERJA'].value_counts()
# filtered_units = unit_kerja_counts[unit_kerja_counts >= threshold].index

# # Step 3: Keep only rows with UNIT KERJA above the threshold
# df_filtered = df[df['UNIT KERJA'].isin(filtered_units)]

df_filtered = df.copy()
# Step 4: Save the filtered DataFrame to a new Excel file
output_file_path = os.path.join(script_dir,"data_ready.xlsx")
df_filtered.to_excel(output_file_path, index=False)

# ================================================================


doc_columns = [
    "FOTO 1/2 BADAN (*)", "FOTO FULL BODY (*)", "AKTA LAHIR (*)", 
    "KTP (*)", "NPWP(*)", "SUMPAH PNS", "NOTA BKN", "SPMT CPNS", 
    "KARTU ASN VIRTUAL", "NO NPWP", "NO BPJS", "NO KK"
]

# Full list of columns to group by (first priority is UNIT KERJA)
group_cols = ['UNIT KERJA', 'TINGKAT', 'LOKASI', 'PROVINSI', 'STATUS', 'JENIS KELAMIN', 'BULAN', 'TAHUN']

df_unitkerja = df_filtered.copy()

# Make sure document columns are numeric
df_unitkerja.loc[:, doc_columns] = df_unitkerja[doc_columns].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)

# Group by all relevant columns
grouped_df_unitkerja = df_unitkerja.groupby(group_cols)[doc_columns].sum().reset_index()

# Optional: Add total document count
grouped_df_unitkerja['TOTAL DOKUMEN'] = grouped_df_unitkerja[doc_columns].sum(axis=1)

# add a new column 'NO' with sequential numbers starting from 1
grouped_df_unitkerja.insert(0, 'NO', range(1, len(grouped_df_unitkerja) + 1))

# Save to Excel
output_file_path = os.path.join(script_dir, "data_view.xlsx")
grouped_df_unitkerja.to_excel(output_file_path, index=False)


# ============================================================

# Groupby Tingkat
group_cols = ['TINGKAT']

df_tingkat = df_filtered.copy()

# Make sure document columns are numeric
df_tingkat.loc[:, doc_columns] = df_tingkat[doc_columns].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)

# Group by all relevant columns
grouped_df_tingkat = df_tingkat.groupby(group_cols)[doc_columns].sum().reset_index()

# Optional: Add total document count
grouped_df_tingkat['TOTAL DOKUMEN'] = grouped_df_tingkat[doc_columns].sum(axis=1)

# add a new column 'NO' with sequential numbers starting from 1
grouped_df_tingkat.insert(0, 'NO', range(1, len(grouped_df_tingkat) + 1))

# Save to Excel
output_file_path = os.path.join(script_dir, "data_view_tingkat.xlsx")
grouped_df_tingkat.to_excel(output_file_path, index=False)


# ============================================================

# Groupby Lokasi
group_cols = ['LOKASI']

df_lokasi = df_filtered.copy()

# Make sure document columns are numeric
df_lokasi.loc[:, doc_columns] = df_lokasi[doc_columns].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)

# Group by all relevant columns
grouped_df_lokasi = df_lokasi.groupby(group_cols)[doc_columns].sum().reset_index()

# Optional: Add total document count
grouped_df_lokasi['TOTAL DOKUMEN'] = grouped_df_lokasi[doc_columns].sum(axis=1)

# add a new column 'NO' with sequential numbers starting from 1
grouped_df_lokasi.insert(0, 'NO', range(1, len(grouped_df_lokasi) + 1))

# Save to Excel
output_file_path = os.path.join(script_dir, "data_view_lokasi.xlsx")
grouped_df_lokasi.to_excel(output_file_path, index=False)


# ============================================================

# Groupby Provinsi
group_cols = ['PROVINSI']

df_provinsi = df_filtered.copy()

# Make sure document columns are numeric
df_provinsi.loc[:, doc_columns] = df_provinsi[doc_columns].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)

# Group by all relevant columns
grouped_df_provinsi = df_provinsi.groupby(group_cols)[doc_columns].sum().reset_index()

# Optional: Add total document count
grouped_df_provinsi['TOTAL DOKUMEN'] = grouped_df_provinsi[doc_columns].sum(axis=1)

# add a new column 'NO' with sequential numbers starting from 1
grouped_df_provinsi.insert(0, 'NO', range(1, len(grouped_df_provinsi) + 1))

# Save to Excel
output_file_path = os.path.join(script_dir, "data_view_provinsi.xlsx")
grouped_df_provinsi.to_excel(output_file_path, index=False)


# ============================================================

# Groupby STATUS
group_cols = ['STATUS']

df_status = df_filtered.copy()

# Make sure document columns are numeric
df_status.loc[:, doc_columns] = df_status[doc_columns].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)

# Group by all relevant columns
grouped_df_status = df_status.groupby(group_cols)[doc_columns].sum().reset_index()

# Optional: Add total document count
grouped_df_status['TOTAL DOKUMEN'] = grouped_df_status[doc_columns].sum(axis=1)

# add a new column 'NO' with sequential numbers starting from 1
grouped_df_status.insert(0, 'NO', range(1, len(grouped_df_status) + 1))

# Save to Excel
output_file_path = os.path.join(script_dir, "data_view_status.xlsx")
grouped_df_status.to_excel(output_file_path, index=False)


# ============================================================

# Groupby JENIS KELAMIN
group_cols = ['JENIS KELAMIN']

df_jeniskelamin = df_filtered.copy()

# Make sure document columns are numeric
df_jeniskelamin.loc[:, doc_columns] = df_jeniskelamin[doc_columns].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)

# Group by all relevant columns
grouped_df_jeniskelamin = df_jeniskelamin.groupby(group_cols)[doc_columns].sum().reset_index()

# Optional: Add total document count
grouped_df_jeniskelamin['TOTAL DOKUMEN'] = grouped_df_jeniskelamin[doc_columns].sum(axis=1)

# add a new column 'NO' with sequential numbers starting from 1
grouped_df_jeniskelamin.insert(0, 'NO', range(1, len(grouped_df_jeniskelamin) + 1))

# Save to Excel
output_file_path = os.path.join(script_dir, "data_view_jeniskelamin.xlsx")
grouped_df_jeniskelamin.to_excel(output_file_path, index=False)
