import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# Page Config
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for some minor tweaks
st.markdown("""
    <style>
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 15px;
        margin-bottom: 20px;
    }
    @media (max-width: 1024px) {
        .kpi-container {
            grid-template-columns: repeat(4, 1fr);
        }
    }
    @media (max-width: 768px) {
        .kpi-container {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    .kpi-card {
        background-color: transparent;
        border-left: 4px solid #2E86C1;
        padding: 10px 15px;
        margin: 5px 0;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        border-radius: 4px;
        background-color: #ffffff;
    }
    .kpi-label {
        font-size: 14px;
        color: #555555;
        margin-bottom: 5px;
    }
    .kpi-value {
        font-size: 22px;
        font-weight: bold;
        color: #17202A;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Data Loading
@st.cache_data
def load_data():
    base_path = "Backend/Processed"
    
    customers_path = os.path.join(base_path, "customers_clean.csv")
    orders_path = os.path.join(base_path, "orders_clean.csv")
    products_path = os.path.join(base_path, "products_clean.csv")
    
    missing_files = []
    if not os.path.exists(customers_path): missing_files.append("customers_clean.csv")
    if not os.path.exists(orders_path): missing_files.append("orders_clean.csv")
    if not os.path.exists(products_path): missing_files.append("products_clean.csv")
        
    if missing_files:
        st.error(f"The following files were not found in {base_path}: {', '.join(missing_files)}. Please check the Processed folder.")
        st.stop()
        
    try:
        customers = pd.read_csv(customers_path)
        orders = pd.read_csv(orders_path)
        products = pd.read_csv(products_path)
        
        # Prepare data
        orders["OrderDate"] = pd.to_datetime(orders["OrderDate"], errors="coerce")
        if "OrderDateOnly" in orders.columns:
            orders["OrderDateOnly"] = pd.to_datetime(orders["OrderDateOnly"], errors="coerce").dt.date
        else:
            orders["OrderDateOnly"] = orders["OrderDate"].dt.date
            
        return customers, orders, products
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

def format_currency(value):
    if pd.isna(value):
        return "₹0.00"
    if value >= 10000000:
        return f"₹{value/10000000:.2f} Cr"
    elif value >= 100000:
        return f"₹{value/100000:.2f} L"
    else:
        return f"₹{value:,.2f}"

def format_number(value):
    if pd.isna(value):
        return "0"
    return f"{value:,.0f}"

try:
    customers_df, orders_df, products_df = load_data()
    
    # Merge datasets for comprehensive filtering and analysis
    merged_df = orders_df.merge(customers_df, on="CustomerID", how="left")
    merged_df = merged_df.merge(products_df, on="ProductID", how="left")
    
    # Sidebar
    st.sidebar.title("SALES ANALYTICS 📊")
    
    # Data Quality Section in Sidebar
    with st.sidebar.expander("Data Quality & Overview", expanded=False):
        st.markdown(f"**Orders:** {len(orders_df):,} rows")
        st.markdown(f"**Customers:** {len(customers_df):,} rows")
        st.markdown(f"**Products:** {len(products_df):,} rows")
        st.markdown(f"**Date Range:** {orders_df['OrderDateOnly'].min()} to {orders_df['OrderDateOnly'].max()}")
        st.markdown("---")
        st.markdown("**SQL Analysis:**")
        st.markdown("MySQL analysis views (e.g., `vw_business_kpis`, `vw_category_sales`) are documented in the backend database. This dashboard operates on processed CSVs for reliability.")

    # Apply Filters cascadingly
    filtered_df = merged_df.copy()
    
    # Year
    years = ["All"] + sorted(filtered_df["Year"].dropna().unique().tolist())
    selected_year = st.sidebar.selectbox("Year", years)
    if selected_year != "All":
        filtered_df = filtered_df[filtered_df["Year"] == selected_year]
        
    # Month
    months = ["All"] + sorted(filtered_df["Month"].dropna().unique().tolist())
    selected_month = st.sidebar.selectbox("Month", months)
    if selected_month != "All":
        filtered_df = filtered_df[filtered_df["Month"] == selected_month]
        
    # Category
    categories = ["All"] + sorted(filtered_df["Category"].dropna().unique().tolist())
    selected_category = st.sidebar.selectbox("Category", categories)
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["Category"] == selected_category]
        
    # City
    cities = ["All"] + sorted(filtered_df["City"].dropna().unique().tolist())
    selected_city = st.sidebar.selectbox("City", cities)
    if selected_city != "All":
        filtered_df = filtered_df[filtered_df["City"] == selected_city]
        
    # Payment Method
    payment_methods = ["All"] + sorted(filtered_df["PaymentMethod"].dropna().unique().tolist())
    selected_payment = st.sidebar.selectbox("Payment Method", payment_methods)
    if selected_payment != "All":
        filtered_df = filtered_df[filtered_df["PaymentMethod"] == selected_payment]
        
    # Order Status
    order_statuses = ["All"] + sorted(filtered_df["OrderStatus"].dropna().unique().tolist())
    selected_status = st.sidebar.selectbox("Order Status", order_statuses)
    if selected_status != "All":
        filtered_df = filtered_df[filtered_df["OrderStatus"] == selected_status]
        
    # Date Range (based on available dates in filtered data)
    min_date = filtered_df["OrderDateOnly"].min()
    max_date = filtered_df["OrderDateOnly"].max()
    
    # Fallback if no dates available
    if pd.isna(min_date) or pd.isna(max_date):
        min_date = merged_df["OrderDateOnly"].min()
        max_date = merged_df["OrderDateOnly"].max()
        
    date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=merged_df["OrderDateOnly"].min(), max_value=merged_df["OrderDateOnly"].max())
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df["OrderDateOnly"] >= start_date) & (filtered_df["OrderDateOnly"] <= end_date)]
    elif len(date_range) == 1:
        start_date = date_range[0]
        filtered_df = filtered_df[filtered_df["OrderDateOnly"] == start_date]
        
    # Download Data Button
    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="📥 Download Filtered Data",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name='sales_data_filtered.csv',
        mime='text/csv',
    )
        
    # Main Dashboard Title
    st.title("Sales Analytics Dashboard")
    
    # KPIs
    total_orders = filtered_df["OrderID"].nunique()
    total_customers = filtered_df["CustomerID"].nunique()
    total_products_sold = filtered_df["Quantity"].sum()
    gross_revenue = filtered_df["Revenue"].sum()
    net_sales = filtered_df["FinalAmount"].sum()
    avg_order_value = filtered_df["FinalAmount"].mean()
    total_discount = filtered_df["DiscountAmount"].sum()
    
    kpi_html = f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-label">Total Orders</div>
            <div class="kpi-value">{format_number(total_orders)}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Total Customers</div>
            <div class="kpi-value">{format_number(total_customers)}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Products Sold</div>
            <div class="kpi-value">{format_number(total_products_sold)}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Gross Revenue</div>
            <div class="kpi-value">{format_currency(gross_revenue)}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Net Sales</div>
            <div class="kpi-value">{format_currency(net_sales)}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Avg Order Value</div>
            <div class="kpi-value">{format_currency(avg_order_value)}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Total Discount</div>
            <div class="kpi-value">{format_currency(total_discount)}</div>
        </div>
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Overview", "Sales Analysis", "Product Analysis", 
        "Customer Analysis", "Order Analysis", "Payment Analysis"
    ])
    
    with tab1:
        st.subheader("Business Insights")
        insight_col1, insight_col2 = st.columns(2)
        
        with insight_col1:
            if not filtered_df.empty:
                top_category = filtered_df.groupby("Category")["FinalAmount"].sum().idxmax()
                top_category_val = filtered_df.groupby("Category")["FinalAmount"].sum().max()
                st.info(f"**Highest Revenue Category:** {top_category} ({format_currency(top_category_val)})")
                
                top_city = filtered_df.groupby("City")["FinalAmount"].sum().idxmax()
                top_city_val = filtered_df.groupby("City")["FinalAmount"].sum().max()
                st.info(f"**Highest Revenue City:** {top_city} ({format_currency(top_city_val)})")
                
        with insight_col2:
            if not filtered_df.empty:
                top_payment = filtered_df["PaymentMethod"].mode()[0] if not filtered_df["PaymentMethod"].empty else "N/A"
                st.info(f"**Most Common Payment Method:** {top_payment}")
                
                top_product = filtered_df.groupby("Product")["Quantity"].sum().idxmax()
                st.info(f"**Most Sold Product:** {top_product}")

        st.markdown("---")
        st.subheader("Correlation Analysis")
        # Correlation Heatmap
        numeric_cols = ["Quantity", "Price", "DiscountPercent", "FinalAmount", "Revenue", "DiscountAmount"]
        available_cols = [c for c in numeric_cols if c in filtered_df.columns]
        if available_cols and len(filtered_df) > 1:
            corr_matrix = filtered_df[available_cols].corr()
            fig = px.imshow(corr_matrix, text_auto=".2f", aspect="auto", color_continuous_scale="Blues", title="Correlation Matrix")
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Monthly Sales Trend")
        if not filtered_df.empty and "Year" in filtered_df.columns and "MonthNumber" in filtered_df.columns:
            monthly_sales = filtered_df.groupby(["Year", "MonthNumber", "Month"]).agg({
                "OrderID": "nunique",
                "Revenue": "sum",
                "FinalAmount": "sum"
            }).reset_index()
            
            monthly_sales = monthly_sales.sort_values(["Year", "MonthNumber"])
            monthly_sales["Previous Month Sales"] = monthly_sales["FinalAmount"].shift(1)
            monthly_sales["Growth Percentage"] = ((monthly_sales["FinalAmount"] - monthly_sales["Previous Month Sales"]) / monthly_sales["Previous Month Sales"] * 100).fillna(0)
            
            # Format month name for display
            monthly_sales["MonthYear"] = monthly_sales["Month"] + " " + monthly_sales["Year"].astype(str)
            
            fig = px.line(monthly_sales, x="MonthYear", y="FinalAmount", markers=True, title="Net Sales Over Time")
            fig.update_traces(line_color="#2E86C1", fill='tozeroy')
            st.plotly_chart(fig, use_container_width=True)
            
            # Table
            display_cols = ["MonthYear", "OrderID", "Revenue", "FinalAmount", "Previous Month Sales", "Growth Percentage"]
            table_df = monthly_sales.rename(columns={"OrderID": "Total Orders", "Revenue": "Gross Revenue", "FinalAmount": "Net Sales"})
            
            # Format columns
            table_df["Gross Revenue"] = table_df["Gross Revenue"].apply(format_currency)
            table_df["Net Sales"] = table_df["Net Sales"].apply(format_currency)
            table_df["Previous Month Sales"] = table_df["Previous Month Sales"].apply(lambda x: format_currency(x) if pd.notna(x) else "N/A")
            table_df["Growth Percentage"] = table_df["Growth Percentage"].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
            
            st.dataframe(table_df[["MonthYear", "Total Orders", "Gross Revenue", "Net Sales", "Previous Month Sales", "Growth Percentage"]], use_container_width=True)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Revenue by Category")
            if not filtered_df.empty and "Category" in filtered_df.columns:
                cat_sales = filtered_df.groupby("Category").agg({
                    "FinalAmount": "sum"
                }).reset_index().sort_values("FinalAmount", ascending=True)
                
                cat_sales["Percentage of Total Revenue"] = (cat_sales["FinalAmount"] / cat_sales["FinalAmount"].sum()) * 100
                
                fig = px.bar(cat_sales, x="FinalAmount", y="Category", orientation='h', title="Net Sales by Category")
                fig.update_traces(marker_color="#2E86C1")
                st.plotly_chart(fig, use_container_width=True)
                
                # Table
                cat_table = cat_sales.copy().sort_values("FinalAmount", ascending=False)
                cat_table["FinalAmount"] = cat_table["FinalAmount"].apply(format_currency)
                cat_table["Percentage of Total Revenue"] = cat_table["Percentage of Total Revenue"].apply(lambda x: f"{x:.2f}%")
                cat_table.rename(columns={"FinalAmount": "Revenue"}, inplace=True)
                st.dataframe(cat_table, use_container_width=True)

        with col2:
            st.subheader("Top 10 Products by Revenue")
            if not filtered_df.empty and "Product" in filtered_df.columns:
                prod_sales = filtered_df.groupby(["Product", "Category"]).agg({
                    "Quantity": "sum",
                    "OrderID": "nunique",
                    "Revenue": "sum",
                    "FinalAmount": "sum"
                }).reset_index()
                
                prod_sales["Average Selling Price"] = prod_sales["FinalAmount"] / prod_sales["Quantity"]
                prod_sales = prod_sales.sort_values("FinalAmount", ascending=True).tail(10)
                
                fig = px.bar(prod_sales, x="FinalAmount", y="Product", orientation='h', title="Top 10 Products (Net Sales)")
                fig.update_traces(marker_color="#2E86C1")
                st.plotly_chart(fig, use_container_width=True)
                
                # Table
                prod_table = prod_sales.sort_values("FinalAmount", ascending=False).copy()
                prod_table.rename(columns={"Quantity": "Units Sold", "OrderID": "Total Orders", "FinalAmount": "Net Sales", "Revenue": "Gross Revenue"}, inplace=True)
                prod_table["Net Sales"] = prod_table["Net Sales"].apply(format_currency)
                prod_table["Gross Revenue"] = prod_table["Gross Revenue"].apply(format_currency)
                prod_table["Average Selling Price"] = prod_table["Average Selling Price"].apply(format_currency)
                st.dataframe(prod_table, use_container_width=True)

    with tab4:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Top 10 Customers by Spending")
            if not filtered_df.empty and "CustomerName" in filtered_df.columns:
                cust_sales = filtered_df.groupby(["CustomerID", "CustomerName", "City"]).agg({
                    "OrderID": "nunique",
                    "Quantity": "sum",
                    "FinalAmount": "sum"
                }).reset_index()
                
                cust_sales["AverageOrderValue"] = cust_sales["FinalAmount"] / cust_sales["OrderID"]
                cust_sales = cust_sales.sort_values("FinalAmount", ascending=False).head(10)
                
                cust_table = cust_sales.rename(columns={
                    "OrderID": "TotalOrders", 
                    "Quantity": "ProductsBought", 
                    "FinalAmount": "TotalSpent"
                })
                
                cust_table["TotalSpent"] = cust_table["TotalSpent"].apply(format_currency)
                cust_table["AverageOrderValue"] = cust_table["AverageOrderValue"].apply(format_currency)
                
                st.dataframe(cust_table, use_container_width=True)
                
        with col2:
            st.subheader("Customer Segmentation")
            if not filtered_df.empty and "OrderValueCategory" in filtered_df.columns:
                seg_sales = filtered_df.groupby("OrderValueCategory").agg({
                    "CustomerID": "nunique",
                    "FinalAmount": "sum",
                    "OrderID": "nunique"
                }).reset_index()
                
                seg_sales["Average Customer Value"] = seg_sales["FinalAmount"] / seg_sales["CustomerID"]
                seg_sales["Average Orders Per Customer"] = seg_sales["OrderID"] / seg_sales["CustomerID"]
                
                fig = px.bar(seg_sales, x="OrderValueCategory", y="FinalAmount", title="Revenue by Segment")
                fig.update_traces(marker_color="#2E86C1")
                st.plotly_chart(fig, use_container_width=True)
                
                seg_table = seg_sales.rename(columns={"CustomerID": "Total Customers", "FinalAmount": "Total Revenue"})
                seg_table["Total Revenue"] = seg_table["Total Revenue"].apply(format_currency)
                seg_table["Average Customer Value"] = seg_table["Average Customer Value"].apply(format_currency)
                seg_table["Average Orders Per Customer"] = seg_table["Average Orders Per Customer"].apply(lambda x: f"{x:.2f}")
                
                st.dataframe(seg_table.drop("OrderID", axis=1), use_container_width=True)

    with tab5:
        st.subheader("City-wise Revenue")
        if not filtered_df.empty and "City" in filtered_df.columns:
            city_sales = filtered_df.groupby("City").agg({
                "OrderID": "nunique",
                "CustomerID": "nunique",
                "Quantity": "sum",
                "Revenue": "sum",
                "FinalAmount": "sum"
            }).reset_index()
            
            city_sales["Average Order Value"] = city_sales["FinalAmount"] / city_sales["OrderID"]
            city_sales = city_sales.sort_values("FinalAmount", ascending=True).tail(15)
            
            fig = px.bar(city_sales, x="FinalAmount", y="City", orientation='h', title="Top 15 Cities by Net Sales")
            fig.update_traces(marker_color="#2E86C1")
            st.plotly_chart(fig, use_container_width=True)
            
            city_table = city_sales.sort_values("FinalAmount", ascending=False).rename(columns={
                "OrderID": "Total Orders", 
                "CustomerID": "Total Customers",
                "Quantity": "Units Sold",
                "Revenue": "Gross Revenue",
                "FinalAmount": "Net Sales"
            })
            
            city_table["Gross Revenue"] = city_table["Gross Revenue"].apply(format_currency)
            city_table["Net Sales"] = city_table["Net Sales"].apply(format_currency)
            city_table["Average Order Value"] = city_table["Average Order Value"].apply(format_currency)
            
            st.dataframe(city_table, use_container_width=True)

        st.markdown("---")
        st.subheader("Order Status Analysis")
        if not filtered_df.empty and "OrderStatus" in filtered_df.columns:
            status_sales = filtered_df.groupby("OrderStatus").agg({
                "OrderID": "nunique",
                "Revenue": "sum",
                "FinalAmount": "sum"
            }).reset_index()
            
            status_sales["Order Percentage"] = (status_sales["OrderID"] / status_sales["OrderID"].sum()) * 100
            
            col1, col2 = st.columns([1, 2])
            with col1:
                fig = px.pie(status_sales, values="OrderID", names="OrderStatus", title="Orders by Status", hole=0.3)
                st.plotly_chart(fig, use_container_width=True)
                
            with col2:
                status_table = status_sales.rename(columns={
                    "OrderID": "Total Orders",
                    "Revenue": "Gross Revenue",
                    "FinalAmount": "Net Sales"
                })
                
                status_table["Gross Revenue"] = status_table["Gross Revenue"].apply(format_currency)
                status_table["Net Sales"] = status_table["Net Sales"].apply(format_currency)
                status_table["Order Percentage"] = status_table["Order Percentage"].apply(lambda x: f"{x:.1f}%")
                
                st.dataframe(status_table, use_container_width=True)

    with tab6:
        st.subheader("Payment Method Analysis")
        if not filtered_df.empty and "PaymentMethod" in filtered_df.columns:
            payment_sales = filtered_df.groupby("PaymentMethod").agg({
                "OrderID": "nunique",
                "FinalAmount": "sum"
            }).reset_index()
            
            payment_sales["Average Order Value"] = payment_sales["FinalAmount"] / payment_sales["OrderID"]
            payment_sales["Order Percentage"] = (payment_sales["OrderID"] / payment_sales["OrderID"].sum()) * 100
            
            col1, col2 = st.columns([1, 2])
            with col1:
                fig = px.pie(payment_sales, values="OrderID", names="PaymentMethod", title="Orders by Payment Method", hole=0.3)
                st.plotly_chart(fig, use_container_width=True)
                
            with col2:
                payment_table = payment_sales.rename(columns={
                    "OrderID": "Total Orders",
                    "FinalAmount": "Net Sales"
                })
                
                payment_table["Net Sales"] = payment_table["Net Sales"].apply(format_currency)
                payment_table["Average Order Value"] = payment_table["Average Order Value"].apply(format_currency)
                payment_table["Order Percentage"] = payment_table["Order Percentage"].apply(lambda x: f"{x:.1f}%")
                
                st.dataframe(payment_table, use_container_width=True)

except Exception as e:
    st.error(f"An unexpected error occurred during dashboard generation: {str(e)}")
