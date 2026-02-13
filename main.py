import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Burn vs Invoice Comparison", layout="wide")

st.title("📊 Burn vs Invoice Comparison Tool")

st.write("Upload Monthly Burn and Invoices CSV files to compare values.")

# File uploaders
burn_file = st.file_uploader("Upload Monthly Burn CSV", type=["csv"])
invoice_file = st.file_uploader("Upload Invoices CSV", type=["csv"])

if burn_file and invoice_file:

    # -------------------------
    # Load Monthly Burn
    # -------------------------
    df_burn = pd.read_csv(burn_file, thousands=",")

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

    df_burn['Time Burn (value)'] = pd.to_numeric(df_burn['Time Burn (value)'], errors="coerce")
    df_burn['Expense Burn (value)'] = pd.to_numeric(df_burn['Expense Burn (value)'], errors="coerce")
    df_burn['Total Burn (value)'] = pd.to_numeric(df_burn['Total Burn (value)'], errors="coerce")

    # -------------------------
    # Load Invoices
    # -------------------------
    df_invoices = pd.read_csv(invoice_file, thousands=",")

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

    df_invoices['Invoiced Amount'] = pd.to_numeric(df_invoices['Invoiced Amount'], errors="coerce")

    # -------------------------
    # Merge
    # -------------------------
    df_compare = df_burn.merge(
        df_invoices,
        on="Project Number",
        how="left"
    )

    # Compute difference BEFORE fillna
    df_compare["Difference"] = (
        df_compare["Total Burn (value)"] - df_compare["Invoiced Amount"]
    )

    # Comments logic
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

    # Replace NaN values after logic
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

    st.success("Comparison Completed ✅")

    # Show table
    st.dataframe(df_export, use_container_width=True)

    # Download button
    csv = df_export.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Comparison CSV",
        data=csv,
        file_name="burn_vs_invoice_comparison.csv",
        mime="text/csv"
    )

else:
    st.info("Please upload both CSV files to begin.")
