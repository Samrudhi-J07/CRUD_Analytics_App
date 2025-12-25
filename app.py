import sqlite3
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- DATABASE ----------------
conn = sqlite3.connect("sales.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product TEXT,
    quantity INTEGER,
    price REAL
)
""")
conn.commit()

# ---------------- UI ----------------
st.title("📊 CRUD Analytics App")
st.write("Insert, Update, Delete records and see live analytics")

st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Add Data", "Update / Delete"])

# ---------------- ADD DATA ----------------
if page == "Add Data":
    st.header("➕ Insert Sales Data")

    product = st.text_input("Product Name", key="product")
    quantity = st.number_input("Quantity", min_value=1, step=1, key="insert_qty")
    price = st.number_input("Price", min_value=1.0, key="price")

    if st.button("Insert Record"):
        cursor.execute(
            "INSERT INTO sales (product, quantity, price) VALUES (?, ?, ?)",
            (product, quantity, price)
        )
        conn.commit()
        st.success("Record inserted successfully!")

# ---------------- LOAD DATA ----------------
df = pd.read_sql("SELECT * FROM sales", conn)

# ---------------- DASHBOARD ----------------
if page == "Dashboard":
    st.header("📊 Dashboard")

    if df.empty:
        st.info("No data available yet.")
    else:
        # Product filter
        product_filter = st.selectbox(
            "Filter by Product",
            ["All"] + list(df["product"].unique()),
            key="filter_product"
        )

        filtered_df = df.copy()
        if product_filter != "All":
            filtered_df = filtered_df[filtered_df["product"] == product_filter]

        # KPI Metrics
        col1, col2, col3 = st.columns(3)
        total_sales = (filtered_df["quantity"] * filtered_df["price"]).sum()
        total_orders = len(filtered_df)
        avg_price = filtered_df["price"].mean()

        col1.metric("💰 Total Sales", f"{total_sales:.2f}")
        col2.metric("📦 Total Orders", total_orders)
        col3.metric("📊 Avg Price", f"{avg_price:.2f}")

        # Sales Table
        st.subheader("📋 Sales Table")
        st.dataframe(filtered_df)

        # Sales Analytics Chart
        st.subheader("📈 Sales Analytics")
        filtered_df["Total Sales"] = filtered_df["quantity"] * filtered_df["price"]

        fig, ax = plt.subplots()
        filtered_df.groupby("product")["Total Sales"].sum().plot(kind="bar", ax=ax)
        ax.set_ylabel("Total Sales")
        st.pyplot(fig)

# ---------------- UPDATE / DELETE ----------------
if page == "Update / Delete":
    st.header("✏️ Update / Delete Records")

    if df.empty:
        st.info("No records to update or delete.")
    else:
        # Select record
        selected_id = st.selectbox(
            "Select Record ID",
            df["id"],
            key="update_id"
        )

        # ---------------- UPDATE ----------------
        new_quantity = st.number_input(
            "New Quantity",
            min_value=1,
            step=1,
            key="update_quantity"
        )

        if st.button("Update Quantity"):
            cursor.execute(
                "UPDATE sales SET quantity=? WHERE id=?",
                (new_quantity, selected_id)
            )
            conn.commit()
            st.success(f"Record ID {selected_id} updated successfully!")

        st.divider()

        # ---------------- DELETE ----------------
        confirm_delete = st.checkbox("⚠️ I confirm delete this record", key="confirm_delete")

        if st.button("Delete Record") and confirm_delete:
            cursor.execute("DELETE FROM sales WHERE id=?", (selected_id,))
            conn.commit()
            st.success(f"Record ID {selected_id} deleted successfully!")
