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

# Remove rows where 'LOKASI' is 'Jakarta Pusat'
df = df[df['LOKASI'] != 'Jakarta Pusat']

df = df.drop(columns=['NAMA', 'NIP'], errors='ignore')



# ================================================================

# Calculate counts for each UNIT KERJA
unit_kerja_counts = df['UNIT KERJA'].value_counts()

# Determine the threshold using the formula (mean - standard deviation)
threshold = unit_kerja_counts.mean() - unit_kerja_counts.std()

proportion = 0.005  # For example, 0.5% of the total rows
total_rows = df.shape[0]
threshold = total_rows * proportion

# Step 2: Filter out UNIT KERJA with counts below the threshold
unit_kerja_counts = df['UNIT KERJA'].value_counts()
filtered_units = unit_kerja_counts[unit_kerja_counts >= threshold].index

# Step 3: Keep only rows with UNIT KERJA above the threshold
df_filtered = df[df['UNIT KERJA'].isin(filtered_units)]

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

# Make sure document columns are numeric
df_filtered.loc[:, doc_columns] = df_filtered[doc_columns].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)

# Group by all relevant columns
grouped_df = df_filtered.groupby(group_cols)[doc_columns].sum().reset_index()

# Optional: Add total document count
grouped_df['TOTAL DOKUMEN'] = grouped_df[doc_columns].sum(axis=1)

# Save to Excel
output_file_path = os.path.join(script_dir, "data_view.xlsx")
grouped_df.to_excel(output_file_path, index=True)