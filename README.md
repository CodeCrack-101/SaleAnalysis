# Sales Analytics Dashboard

## Project Overview
This project transforms a data analytics pipeline into a professional, interactive Data Analytics Dashboard using Streamlit. It demonstrates proficiency in Python, Pandas, Matplotlib, Seaborn, SQL Analytics, and Streamlit.

## Objectives
- Process and analyze raw sales data (Customers, Orders, Products)
- Maintain an accurate historical record of data transformations via a Jupyter Notebook
- Serve interactive visualizations through a Streamlit Dashboard
- Display important KPI metrics for business intelligence
- Present professional data analysis insights seamlessly

## Dataset
The project includes three core datasets:
- **Customers**: Demographics, contact info, location.
- **Orders**: Sales transactions, payment method, order status, discounts.
- **Products**: Category, pricing, product names.

## Data Cleaning
Data is cleaned and transformed using Python (Pandas) within the `Backend/Notebooks/Analysis.ipynb` notebook. The clean data is output to `Backend/Processed/` as:
- `customers_clean.csv`
- `orders_clean.csv`
- `products_clean.csv`

## Exploratory Data Analysis
Comprehensive EDA was performed to unearth key trends in:
- Revenue growth over months
- Top revenue categories and products
- City-wise sales distributions
- Order statuses and returns
- Customer segmentation (High, Medium, Low value)

## SQL Analysis
While this dashboard natively parses the processed CSV files for high performance, an underlying SQL Analysis layer exists. MySQL was used to create aggregated analytical views:
- `vw_business_kpis`
- `vw_category_sales`
- `vw_city_sales`
- `vw_customer_analysis`
- `vw_customer_segments`
- `vw_monthly_growth`
- `vw_monthly_sales`
- `vw_order_status`
- `vw_payment_analysis`
- `vw_product_sales`

## Dashboard
The final user-facing dashboard is built with **Streamlit**. It directly loads the processed CSV datasets, allowing stakeholders to interactively filter and analyze the data without relying on a constantly running SQL server.

## Technologies
- **Python** (Pandas, NumPy)
- **Matplotlib** / **Seaborn** (Visualizations)
- **Jupyter Notebook** (EDA, cleaning)
- **MySQL** / **SQL** (Analytical querying and views)
- **Streamlit** (Interactive Dashboard UI)

## Project Structure
```
sales-analytics-dashboard/
│
├── Backend/
│   ├── Data/
│   │   ├── customers.csv
│   │   ├── orders.csv
│   │   └── products.csv
│   │
│   ├── Notebooks/
│   │   └── Analysis.ipynb
│   │
│   └── Processed/
│       ├── customers_clean.csv
│       ├── orders_clean.csv
│       └── products_clean.csv
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## How to Install
1. Clone the repository and navigate to the project directory.
2. Install the necessary dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run
Start the Streamlit application by running:
```bash
streamlit run app.py
```

## Key Insights
- **Business Insights**: Dynamically calculated best-selling categories, top cities by revenue, and most popular payment methods.
- **Correlation**: Heatmap analysis for quantitative fields like quantity, price, discount, and final amount.
- **KPI Metrics**: Comprehensive, at-a-glance cards showing gross revenue, net sales, order counts, and discount statistics.

## Screenshots
*(Insert screenshots of the dashboard here)*
