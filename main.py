import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Burn vs Invoice Comparison", layout="wide")

st.title("📊 Burn vs Invoice Comparison Tool")

st.write("Upload Monthly Burn and Invoices CSV files to compare values.")

# -------------------------
# Side-by-side uploaders
# -------------------------
col1, col2 = st.columns(2)

with col1:
    burn_file = st.file_uploader("📂 Upload Monthly Burn CSV", type=["csv"])

with col2:
    invoice_file = st.file_uploader("📂 Upload Invoices CSV", type=["csv"])


# -------------------------
# Run comparison only if both uploaded
# -------------------------
if burn_file and invoice_file:

    # Reload files (because Streamlit file object is consumed after read)
    df_burn = pd.read_csv(burn_file, thousands=",")
    df_invoices = pd.read_csv(invoice_file, thousands=",")

    # Rename burn columns
    df_burn.columns = [
        'Office', 
        'Project Name', 
        'Project Manager', 
        'Account Manager',
        'Contractual Status', 
        'Currency', 
        'Time Burn (value)',
        'Expense Burn (value)', 
        'Total Burn (value)'
    ]

    # Split project name
    df_burn[["Project Number", "Project Description"]] = \
        df_burn["Project Name"].str.split(n=1, expand=True)

    df_burn = df_burn[
        [
            'Office', 
            'Project Number', 
            'Project Description',
            'Project Manager', 
            'Account Manager',
            'Contractual Status', 
            'Currency', 
            'Time Burn (value)',
            'Expense Burn (value)', 
            'Total Burn (value)'
        ]
    ]

    # Convert numeric columns
    for col in ['Time Burn (value)', 'Expense Burn (value)', 'Total Burn (value)']:
        df_burn[col] = pd.to_numeric(df_burn[col], errors="coerce")

    # Rename invoice columns
    df_invoices.columns = [
        'Organisation', 
        'Company', 
        'Project Number', 
        'Project', 
        'Invoice #',
        'Reference', 
        'Email Recipients', 
        'Invoice Date',
        'AM (current)',
        'PM (current)', 
        'PM (original)', 
        'Status', 
        'Due Date', 
        'Payment Date',
        'Invoiced Amount', 
        'Currency',
        'Tax Amount', 
        'Invoiced Amount With Tax',
        'Converted Amount',
        'Converted Currency'
    ]

    df_invoices['Invoiced Amount'] = pd.to_numeric(
        df_invoices['Invoiced Amount'], errors="coerce"
    )

    # -------------------------
    # Merge
    # -------------------------
    df_compare = df_burn.merge(
        df_invoices,
        on="Project Number",
        how="left"
    )

    df_compare["Difference"] = (
        df_compare["Total Burn (value)"] - df_compare["Invoiced Amount"]
    )

    df_compare["Comment"] = np.where(
        df_compare["Invoice #"].isna(),
        "NO INVOICE",
        np.where(
            df_compare["Difference"] == 0,
            "OK",
            np.where(
                df_compare["Difference"] > 0,
                "BURN > INVOICE",
                "BURN < INVOICE"
            )
        )
    )

    df_compare["Invoiced Amount"] = df_compare["Invoiced Amount"].fillna(0)
    df_compare["Difference"] = df_compare["Difference"].fillna(
        df_compare["Total Burn (value)"]
    )

    df_export = df_compare[
        [
            "Project Number", 
            "Project Description",
            "Project Manager", 
            "Account Manager",
            "Time Burn (value)",
            "Expense Burn (value)", 
            "Total Burn (value)",
            "Invoiced Amount",
            "Difference",
            "Comment"
        ]
    ]

    st.divider()
    st.subheader("📊 Comparison Results")
    
    # ---- Conditional formatting function ----
    def highlight_difference(val):
        if pd.isna(val):
            return ""
        elif val < 0:
            return "background-color: #f8d7da;"  # Soft red
        elif val > 0:
            return "background-color: #fff3cd;"  # Soft yellow
        else:
            return "background-color: #d4edda;"  # Soft green
        
            
    # Apply styling
    styled_df = df_export.style.applymap(
        highlight_difference,
        subset=["Difference"]
    )
    
    st.dataframe(styled_df, use_container_width=True)

    # Download
    csv = df_export.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Download Comparison CSV",
        data=csv,
        file_name="burn_vs_invoice_comparison.csv",
        mime="text/csv"
    )

else:
    st.info("Please upload both CSV files to run the comparison.")
