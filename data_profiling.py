import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from ydata_profiling import ProfileReport
from sqlalchemy import create_engine
from matplotlib.backends.backend_pdf import PdfPages
import os

# Step 1: Connect to the database
print("Connecting to the database...")
engine = create_engine("mysql+pymysql://root:root@localhost:3307/housing_db")
df = pd.read_sql("SELECT * FROM housing_data", engine)
print(f"Data loaded successfully. Shape: {df.shape}")

# Step 2: Create output folder
output_dir = "profiling_reports"
os.makedirs(output_dir, exist_ok=True)
print(f"Output folder created: {output_dir}")

# Step 3: Generate Summary Statistics Report (HTML)
print("Generating summary statistics report...")
profile = ProfileReport(df, title="Housing Data Profiling Report", explorative=True)
profile_path = os.path.join(output_dir, "housing_data_profile.html")
profile.to_file(profile_path)
print(f"Summary report saved: {profile_path}")

# Step 4: Generate consolidated Histograms PDF
print("Generating consolidated histograms PDF...")
numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns
histogram_pdf_path = os.path.join(output_dir, "all_histograms.pdf")

with PdfPages(histogram_pdf_path) as pdf:
    for col in numerical_cols:
        plt.figure(figsize=(8, 5))
        sns.histplot(df[col].dropna(), kde=True)
        plt.title(f'Histogram: {col}')
        plt.xlabel(col)
        plt.ylabel('Frequency')
        plt.tight_layout()
        pdf.savefig()
        plt.close()
print(f"All histograms saved to: {histogram_pdf_path}")

# Step 5: Generate consolidated Boxplots PDF
print("Generating consolidated boxplots PDF...")
boxplot_pdf_path = os.path.join(output_dir, "all_boxplots.pdf")

with PdfPages(boxplot_pdf_path) as pdf:
    for col in numerical_cols:
        plt.figure(figsize=(8, 5))
        sns.boxplot(x=df[col].dropna())
        plt.title(f'Boxplot: {col}')
        plt.xlabel(col)
        plt.tight_layout()
        pdf.savefig()
        plt.close()
print(f"All boxplots saved to: {boxplot_pdf_path}")

# Step 6: Generate consolidated Bar charts PDF (Top N categories only)
print("Generating consolidated bar charts PDF...")
categorical_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns
barchart_pdf_path = os.path.join(output_dir, "all_barcharts.pdf")
TOP_N = 20  # Limit to top N categories

with PdfPages(barchart_pdf_path) as pdf:
    for col in categorical_cols:
        top_categories = df[col].value_counts().nlargest(TOP_N)
        plt.figure(figsize=(10, 6))
        sns.barplot(x=top_categories.index, y=top_categories.values)
        plt.title(f'Bar Chart (Top {TOP_N}): {col}')
        plt.xlabel(col)
        plt.ylabel('Count')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        pdf.savefig()
        plt.close()
print(f"All bar charts saved to: {barchart_pdf_path}")

print("All profiling reports have been generated successfully!")
print(f"Check the folder: {output_dir}")
