from fpdf import FPDF
import pandas as pd
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

# Initialize PDF
pdf = FPDF(orientation="P", unit="mm", format="A4")
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Title
pdf.set_font("Times", "B", 20)
pdf.multi_cell(0, 10, "Laporan Data Visualisasi di Lingkungan Perangkat Daerah Pemerintah Provinsi Jawa Timur", align="C")
pdf.ln(5)
pdf.set_font("Times","", 16)
pdf.cell(0, 10, "Hierarchical Clustering Report", align="C")


# Add Images (2 side by side, 1 below)
image1 = os.path.join(script_dir, "hierarchical_dendrogram.png")
image2 = os.path.join(script_dir, "hierarchical_clusters.png")
image3 = os.path.join(script_dir, "hierarchical_pca.png")
image4 = os.path.join(script_dir, "hierarchical_confusion_matrix.png")

pdf.image(image1, x=10, y=55, w=90)
pdf.image(image2, x=110, y=55, w=90)
pdf.image(image3, x=10, y=130, w=90)
pdf.image(image4, x=110, y=130, w=90)

pdf.ln(190)  # Ensure table starts after images

# # Section Title
# pdf.set_font("Times", "B", 12)
# pdf.cell(0, 10, "Hierarchical Clustering Output", new_x="LMARGIN", new_y="NEXT", align="C")
# pdf.ln(5)

# # Load and Display hierarchical_output.csv with Fixed Column Widths
# hierarchical_output_path = os.path.join(script_dir, "hierarchical_output.csv")
# df = pd.read_csv(hierarchical_output_path)

# # Select columns and insert "BULAN" and "TAHUN"
# selected_columns = [
#     "UNIT KERJA", "LOKASI", "STATUS", "JENIS KELAMIN",
#     "BULAN", "TAHUN", "Completeness_Percentage", "Weighted_Completeness", "Cluster_Label"
# ]

# df = df[selected_columns]  # Keep only required columns

# # Fixed column widths
# fixed_col_widths = [75, 10, 10, 18, 10, 9, 25, 24, 14]
# row_height = 6

# # Add Table Header
# pdf.set_font("Times", "B", 6)
# for i, col in enumerate(selected_columns):
#     pdf.cell(fixed_col_widths[i], row_height, col, border=1, align="C")
# pdf.ln()

# # Add Rows
# pdf.set_font("Times", "", 5)
# for _, row in df.iterrows():
#     for i, col in enumerate(selected_columns):
#         text = str(row[col])[:65]  # Limit text length
#         pdf.cell(fixed_col_widths[i], row_height, text, border=1, align="L", new_x="RIGHT")
#     pdf.ln(row_height)

# pdf.ln(5)  # Space before next section

# Function to Add Other Tables
def add_table(pdf, title, csv_path, first_col_wider=False):
    df = pd.read_csv(csv_path)

    total_width = 190  # A4 max width
    num_columns = len(df.columns)

    if first_col_wider:
        first_col_width = 73  # Slightly bigger first column
        remaining_width = total_width - first_col_width
        other_col_width = remaining_width / (num_columns - 1)
        col_widths = [first_col_width] + [other_col_width] * (num_columns - 1)
    else:
        col_widths = [total_width / num_columns] * num_columns  # Equal column width

    row_height = 6  

    # Section Title
    pdf.set_font("Times", "B", 12)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    # Add Table Header
    pdf.set_font("Times", "B", 6)
    for i, col in enumerate(df.columns):
        pdf.cell(col_widths[i], row_height, col, border=1, align="C")
    pdf.ln()

    # Add Table Rows
    pdf.set_font("Times", "", 5)
    for _, row in df.iterrows():
        for i, col in enumerate(df.columns):
            text = str(row[col])[:68]  # Limit text length
            pdf.cell(col_widths[i], row_height, text, border=1, align="L")
        pdf.ln(row_height)

    pdf.ln(5)  # Space after table

# Add Other Tables
add_table(pdf, "Hierarchical Clustering Metrics", os.path.join(script_dir, "hierarchical_metrics.csv"))
add_table(pdf, "Hierarchical Classification Report", os.path.join(script_dir, "hierarchical_classification_report.csv"))
add_table(pdf, "Hierarchical Group By UNIT KERJA", os.path.join(script_dir, "hierarchical_best_unit_kerja_report.csv"), first_col_wider=True)
add_table(pdf, "Hierarchical Group By TINGKAT", os.path.join(script_dir, "hierarchical_best_tingkat_report.csv"))
add_table(pdf, "Hierarchical Group By LOKASI", os.path.join(script_dir, "hierarchical_best_lokasi_report.csv"))
add_table(pdf, "Hierarchical Group By PROVINSI", os.path.join(script_dir, "hierarchical_best_provinsi_report.csv"))
add_table(pdf, "Hierarchical Group By STATUS", os.path.join(script_dir, "hierarchical_best_status_report.csv"))
add_table(pdf, "Hierarchical Group By JENIS KELAMIN", os.path.join(script_dir, "hierarchical_best_jenis_kelamin_report.csv"))

# Save PDF
pdf.output(os.path.join(script_dir, "hierarchical_report.pdf"))
