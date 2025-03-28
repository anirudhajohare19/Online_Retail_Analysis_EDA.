import pandas as pd

# Load dataset
file_path = "https://raw.githubusercontent.com/anirudhajohare19/Online_Retail_Analysis_EDA./refs/heads/main/Online%20Retail.csv"
df = pd.read_csv(file_path)

# Drop missing CustomerIDs
df = df.dropna(subset=['CustomerID'])

# Convert data types
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['CustomerID'] = df['CustomerID'].astype(str)

# Remove negative quantity & price
df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]

# Add Total Sales column
df['TotalSales'] = df['Quantity'] * df['UnitPrice']

# Display first few rows
df.head()

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("https://raw.githubusercontent.com/anirudhajohare19/Online_Retail_Analysis_EDA./refs/heads/main/Online%20Retail.csv")
    df = df.dropna(subset=['CustomerID'])
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['CustomerID'] = df['CustomerID'].astype(str)
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
    df['TotalSales'] = df['Quantity'] * df['UnitPrice']
    return df

df = load_data()

# Streamlit App
st.title("Customer Purchase Behavior Analysis")

# Sidebar Filters
country = st.sidebar.selectbox("Select Country", ["All"] + list(df["Country"].unique()))
if country != "All":
    df = df[df["Country"] == country]

# KPI Metrics
total_sales = df["TotalSales"].sum()
total_orders = df["InvoiceNo"].nunique()
total_customers = df["CustomerID"].nunique()

st.metric("Total Sales ($)", f"{total_sales:,.2f}")
st.metric("Total Orders", total_orders)
st.metric("Total Customers", total_customers)

# Sales Over Time
st.subheader("Sales Over Time")
df['MonthYear'] = df['InvoiceDate'].dt.to_period('M')
sales_trend = df.groupby('MonthYear')['TotalSales'].sum().reset_index()
sales_trend['MonthYear'] = sales_trend['MonthYear'].astype(str)

fig = px.line(sales_trend, x='MonthYear', y='TotalSales', title="Monthly Sales Trend")
st.plotly_chart(fig)

# Top 10 Best-Selling Products
st.subheader("Top 10 Best-Selling Products")
top_products = df.groupby('Description')['Quantity'].sum().nlargest(10).reset_index()
fig, ax = plt.subplots()
sns.barplot(x='Quantity', y='Description', data=top_products, ax=ax)
ax.set_xlabel("Total Quantity Sold")
ax.set_ylabel("Product Description")
st.pyplot(fig)

# Country-wise Revenue
st.subheader("Revenue by Country")
country_revenue = df.groupby("Country")["TotalSales"].sum().reset_index()
fig = px.bar(country_revenue, x="Country", y="TotalSales", title="Total Revenue by Country", color="TotalSales")
st.plotly_chart(fig)

# Customer Segmentation (RFM Analysis)
st.subheader("Customer Segmentation (RFM Analysis)")
latest_date = df['InvoiceDate'].max()
rfm = df.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (latest_date - x.max()).days,
    'InvoiceNo': 'count',
    'TotalSales': 'sum'
}).reset_index()

rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
rfm['Recency Score'] = pd.qcut(rfm['Recency'], 4, labels=[4, 3, 2, 1])
rfm['Frequency Score'] = pd.qcut(rfm['Frequency'], 4, labels=[1, 2, 3, 4])
rfm['Monetary Score'] = pd.qcut(rfm['Monetary'], 4, labels=[1, 2, 3, 4])

rfm['RFM Score'] = rfm[['Recency Score', 'Frequency Score', 'Monetary Score']].sum(axis=1)
vip_customers = rfm[rfm['RFM Score'] >= 10]

st.write("### VIP Customers")
st.dataframe(vip_customers.sort_values("Monetary", ascending=False).head(10))

# Conclusion
st.write("""
### **Key Insights**
1. Sales peak in **November-December** – plan holiday promotions.
2. **Top 10 products** drive a significant portion of sales – optimize inventory.
3. **UK contributes highest revenue** – focus marketing efforts there.
4. **VIP customers generate high revenue** – target them with loyalty programs.
""")