import streamlit as st
import sqlite3
import pandas as pd
import io
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from datetime import datetime
import matplotlib.backends.backend_pdf

# ----------------- Database -----------------
conn = sqlite3.connect("records.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sno TEXT,
    date_of_intervention TEXT,
    yard_location TEXT,
    batchno TEXT,
    hold_no TEXT,
    material TEXT,
    lots_id TEXT,
    sgs_reference_id TEXT,
    planned_qty REAL,
    loaded_qty REAL,
    balance_qty REAL,
    dry_colour TEXT,
    wet_colour TEXT,
    loi REAL,
    mgo REAL,
    sio2 REAL,
    asbestos TEXT,
    truck_no TEXT,
    remarks TEXT,
    vessel_name TEXT,
    sgs_report_id TEXT
)
""")
conn.commit()

# ----------------- Helpers -----------------
def add_record(data):
    cursor.execute("""
    INSERT INTO products (
        sno,date_of_intervention,yard_location,batchno,hold_no,material,
        lots_id,sgs_reference_id,planned_qty,loaded_qty,balance_qty,
        dry_colour,wet_colour,loi,mgo,sio2,asbestos,truck_no,
        remarks,vessel_name,sgs_report_id
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, data)
    conn.commit()

def fetch_records(query="SELECT * FROM products", params=()):
    return pd.read_sql_query(query, conn, params=params)

def update_record(record_id, data):
    cursor.execute("""
    UPDATE products SET 
        sno=?,date_of_intervention=?,yard_location=?,batchno=?,hold_no=?,material=?,
        lots_id=?,sgs_reference_id=?,planned_qty=?,loaded_qty=?,balance_qty=?,
        dry_colour=?,wet_colour=?,loi=?,mgo=?,sio2=?,asbestos=?,truck_no=?,
        remarks=?,vessel_name=?,sgs_report_id=?
    WHERE id=?
    """, (*data, record_id))
    conn.commit()

def delete_record(record_id):
    cursor.execute("DELETE FROM products WHERE id=?", (record_id,))
    conn.commit()

# ----------------- Utilities -----------------
def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "sno": "S.No",
        "date_of_intervention": "Date Of Intervention",
        "yard_location": "Yard Location",
        "batchno": "Batch No.",
        "hold_no": "Hold No.",
        "material": "Material",
        "lots_id": "Lots ID",
        "sgs_reference_id": "SGS Reference ID",
        "planned_qty": "Planned Qty (Tons)",
        "loaded_qty": "Loaded Qty (Tons)",
        "balance_qty": "Balance Qty (Tons)",
        "dry_colour": "Dry Colour",
        "wet_colour": "Wet Colour",
        "loi": "LOI",
        "mgo": "MgO",
        "sio2": "SiO₂",
        "asbestos": "Asbestos",
        "truck_no": "Truck No.",
        "remarks": "Remarks",
        "vessel_name": "Vessel Name",
        "sgs_report_id": "SGS Report ID"
    }
    return df.rename(columns=rename_map)

# ----------------- PDF Export -----------------
def df_to_pdf_bytes(df: pd.DataFrame) -> io.BytesIO:
    pdf_bytes = io.BytesIO()
    pdf_pages = matplotlib.backends.backend_pdf.PdfPages(pdf_bytes)
    
    max_rows_per_page = 25
    total_rows = len(df)
    num_pages = (total_rows // max_rows_per_page) + 1
    
    for page in range(num_pages):
        start = page * max_rows_per_page
        end = start + max_rows_per_page
        sub_df = df.iloc[start:end]
        
        fig, ax = plt.subplots(figsize=(12, sub_df.shape[0]*0.3 + 1))
        ax.axis('tight')
        ax.axis('off')
        table = ax.table(cellText=sub_df.values, colLabels=sub_df.columns, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)
        
        pdf_pages.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    
    pdf_pages.close()
    pdf_bytes.seek(0)
    return pdf_bytes

# ----------------- Sidebar & Layout -----------------
st.set_page_config(page_title="Quality Control Management System", layout="wide")
st.markdown("<h2 style='text-align:center; color:#2C3E50;'>Quality Control Management System</h2>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🏭 ASNS Portal")
    menu = option_menu(
        None,
        ["➕ Add New Record", "📋 All Records", "🔎 Search & Filter", "📊 Reports"],
        icons=["plus-circle", "list-task", "search", "bar-chart"],
        menu_icon="cast",
        default_index=0,
    )

# ----------------- Pages -----------------
def add_new_record():
    st.subheader("➕ Add New Record")
    with st.form("add_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            sno = st.text_input("S.No")
            date_of_intervention = st.date_input("Date of Intervention")
            yard_location = st.text_input("Yard Location")
            batchno = st.text_input("Batch No")
            hold_no = st.text_input("Hold No")
            material = st.text_input("Material")
        with col2:
            lots_id = st.text_input("Lots ID")
            sgs_reference_id = st.text_input("SGS Reference ID")
            planned_qty = st.number_input("Planned Qty (Tons)", 0.0)
            loaded_qty = st.number_input("Loaded Qty (Tons)", 0.0)
            balance_qty = st.number_input("Balance Qty (Tons)", 0.0)
            dry_colour = st.text_input("Dry Colour")
        with col3:
            wet_colour = st.text_input("Wet Colour")
            loi = st.number_input("LOI", 0.0)
            mgo = st.number_input("MgO", 0.0)
            sio2 = st.number_input("SiO₂", 0.0)
            asbestos = st.text_input("Asbestos")
            truck_no = st.text_input("Truck No")
            remarks = st.text_area("Remarks")
            vessel_name = st.text_input("Vessel Name")
            sgs_report_id = st.text_input("SGS Report ID")

        submit = st.form_submit_button("💾 Save Record")
        if submit:
            data = (sno, str(date_of_intervention), yard_location, batchno, hold_no, material,
                    lots_id, sgs_reference_id, planned_qty, loaded_qty, balance_qty,
                    dry_colour, wet_colour, loi, mgo, sio2, asbestos, truck_no,
                    remarks, vessel_name, sgs_report_id)
            add_record(data)
            st.success("✅ Record added successfully!")

def show_all_records():
    st.subheader("📋 All Records")
    df = fetch_records()
    if df.empty:
        st.info("No records available.")
        return

    ids = df["id"].tolist()
    df_display = rename_columns(df).drop(columns=["id"])
    df_display.index = df_display.index + 1
    st.dataframe(df_display, use_container_width=True)

    selected_idx = st.selectbox("Select Record (by row number)", df_display.index.tolist())
    selected_id = ids[selected_idx - 1]

    st.markdown("### ✏️ Update Record")
    with st.form("update_form"):
        record = df[df["id"]==selected_id].iloc[0]
        col1, col2, col3 = st.columns(3)
        with col1:
            sno = st.text_input("S.No", record["sno"])
            date_of_intervention = st.date_input("Date of Intervention", pd.to_datetime(record["date_of_intervention"]))
            yard_location = st.text_input("Yard Location", record["yard_location"])
            batchno = st.text_input("Batch No", record["batchno"])
            hold_no = st.text_input("Hold No", record["hold_no"])
            material = st.text_input("Material", record["material"])
        with col2:
            lots_id = st.text_input("Lots ID", record["lots_id"])
            sgs_reference_id = st.text_input("SGS Reference ID", record["sgs_reference_id"])
            planned_qty = st.number_input("Planned Qty (Tons)", value=record["planned_qty"])
            loaded_qty = st.number_input("Loaded Qty (Tons)", value=record["loaded_qty"])
            balance_qty = st.number_input("Balance Qty (Tons)", value=record["balance_qty"])
            dry_colour = st.text_input("Dry Colour", record["dry_colour"])
        with col3:
            wet_colour = st.text_input("Wet Colour", record["wet_colour"])
            loi = st.number_input("LOI", value=record["loi"])
            mgo = st.number_input("MgO", value=record["mgo"])
            sio2 = st.number_input("SiO₂", value=record["sio2"])
            asbestos = st.text_input("Asbestos", record["asbestos"])
            truck_no = st.text_input("Truck No", record["truck_no"])
            remarks = st.text_area("Remarks", record["remarks"])
            vessel_name = st.text_input("Vessel Name", record["vessel_name"])
            sgs_report_id = st.text_input("SGS Report ID", record["sgs_report_id"])

        if st.form_submit_button("💾 Save Changes"):
            data = (sno, str(date_of_intervention), yard_location, batchno, hold_no, material,
                    lots_id, sgs_reference_id, planned_qty, loaded_qty, balance_qty,
                    dry_colour, wet_colour, loi, mgo, sio2, asbestos, truck_no,
                    remarks, vessel_name, sgs_report_id)
            update_record(selected_id, data)
            st.success("✅ Record updated successfully!")

    if st.button("🗑️ Delete Record"):
        delete_record(selected_id)
        st.warning("Record deleted successfully!")

    today = datetime.today().strftime("%Y-%m-%d")
    pdf_bytes = df_to_pdf_bytes(df_display)
    st.markdown("### 📄 PDF Preview (Table shown above)")
    st.download_button("📥 Download PDF", pdf_bytes, file_name=f"records_{today}.pdf", mime="application/pdf")

# ----------------- Search & Reports -----------------
def show_search_filter():
    st.subheader("🔎 Search & Filter Records")
    keyword = st.text_input("Enter keyword to search (Batch No / Material / Vessel)")
    if st.button("Search"):
        query = "SELECT * FROM products WHERE batchno LIKE ? OR material LIKE ? OR vessel_name LIKE ?"
        df = fetch_records(query, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        if df.empty:
            st.warning("⚠️ No records found.")
        else:
            ids = df["id"].tolist()
            df_display = rename_columns(df).drop(columns=["id"])
            df_display.index = df_display.index + 1
            st.dataframe(df_display, use_container_width=True)

            today = datetime.today().strftime("%Y-%m-%d")
            pdf_bytes = df_to_pdf_bytes(df_display)
            st.markdown("### 📄 PDF Preview (Table shown above)")
            st.download_button("📥 Download PDF", pdf_bytes, file_name=f"search_results_{today}.pdf", mime="application/pdf")

def show_reports():
    st.subheader("📊 Reports & Analytics")
    df = fetch_records()
    if not df.empty:
        df = rename_columns(df)
        report_type = st.selectbox("Select Report Type", ["Material vs Loaded Qty", "Yard vs Planned Qty"])
        if report_type == "Material vs Loaded Qty":
            chart_data = df.groupby("Material")["Loaded Qty (Tons)"].sum()
        else:
            chart_data = df.groupby("Yard Location")["Planned Qty (Tons)"].sum()

        fig, ax = plt.subplots()
        chart_data.plot(kind="bar", ax=ax)
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)

        today = datetime.today().strftime("%Y-%m-%d")
        img_bytes = io.BytesIO()
        fig.savefig(img_bytes, format="png", bbox_inches='tight')
        img_bytes.seek(0)
        st.download_button("📥 Download Chart (PNG)", img_bytes, f"report_{today}.png", "image/png")
        pdf_bytes = io.BytesIO()
        fig.savefig(pdf_bytes, format="pdf", bbox_inches='tight')
        pdf_bytes.seek(0)
        st.download_button("📥 Download Chart (PDF)", pdf_bytes, f"report_{today}.pdf", "application/pdf")
    else:
        st.info("No data available for reports.")

# ----------------- Routing -----------------
if menu == "➕ Add New Record":
    add_new_record()
elif menu == "📋 All Records":
    show_all_records()
elif menu == "🔎 Search & Filter":
    show_search_filter()
elif menu == "📊 Reports":
    show_reports()
