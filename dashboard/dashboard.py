import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data = pd.read_csv('main_data.csv')

data['order_purchase_timestamp'] = pd.to_datetime(data['order_purchase_timestamp'])
data['order_delivered_customer_date'] = pd.to_datetime(data['order_delivered_customer_date'])

st.sidebar.header('Filter by Date')
start_date = st.sidebar.date_input('Start Date', data['order_purchase_timestamp'].min().date())
end_date = st.sidebar.date_input('End Date', data['order_purchase_timestamp'].max().date())

filtered_data = data[(data['order_purchase_timestamp'].dt.date >= start_date) & 
                     (data['order_purchase_timestamp'].dt.date <= end_date)]

customer_purchase_count = filtered_data.groupby('customer_id').size().reset_index(name='purchase_count')
repeat_customers = customer_purchase_count[customer_purchase_count['purchase_count'] > 1]

repeat_purchases_by_region = pd.merge(
    repeat_customers, 
    filtered_data[['customer_id', 'customer_city', 'customer_state']], 
    on='customer_id'
).groupby(['customer_state', 'customer_city'])['purchase_count'].mean().sort_values(ascending=False)

product_ratings = filtered_data.groupby('product_id')['review_score'].mean().sort_values(ascending=False)
category_ratings = filtered_data.groupby('product_category_name')['review_score'].mean().sort_values(ascending=False)
payment_method_ratings = filtered_data.groupby('payment_type')['review_score'].mean().sort_values(ascending=False)


total_orders = filtered_data["order_id"].nunique()
value = f"{total_orders} orders"

st.title("Customer Purchase Analysis Dashboard :sparkles:")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Top 10 Regions", "Product Ratings", "RFM Analysis", "Payment Method Ratings"])

with tab1:
    
    st.metric("Total Orders", value=value)

    
    daily_orders_df = filtered_data.groupby(filtered_data['order_purchase_timestamp'].dt.date)['order_id'].count().reset_index()
    daily_orders_df.columns = ['order_date', 'order_count']

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(
        daily_orders_df["order_date"],
        daily_orders_df["order_count"],
        marker='o',
        linewidth=2,
        color="#90CAF9"
    )
    ax.set_title('Number of Orders per Day', fontsize=20)
    ax.set_xlabel('Order Date', fontsize=15)
    ax.set_ylabel('Order Count', fontsize=15)
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
    st.pyplot(fig)

with tab2:
    st.subheader("Top 10 Regions with Highest Average Repeat Purchases")
    st.write(repeat_purchases_by_region.head(10))

    fig, ax = plt.subplots(figsize=(10, 6))
    repeat_purchases_by_region.head(10).plot(kind='bar', ax=ax)
    ax.set_title('Top 10 Regions by Average Repeat Purchases')
    ax.set_xlabel('Region (State, City)')
    ax.set_ylabel('Average Repeat Purchases')
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

with tab3:
    st.subheader("Top Rated Products")
    st.write(product_ratings.head())

    fig, ax = plt.subplots(figsize=(10, 6))
    product_ratings.head(10).plot(kind='bar', ax=ax)
    ax.set_title('Top 10 Products by Average Rating')
    ax.set_xlabel('Product ID')
    ax.set_ylabel('Average Rating')
    st.pyplot(fig)

    st.subheader("Top Rated Categories")
    st.write(category_ratings.head())

    fig, ax = plt.subplots(figsize=(10, 6))
    category_ratings.head(10).plot(kind='bar', ax=ax)
    ax.set_title('Top 10 Categories by Average Rating')
    ax.set_xlabel('Category Name')
    ax.set_ylabel('Average Rating')
    st.pyplot(fig)

with tab4:
    st.subheader("RFM Analysis of Top Customers")

    # RFM Analysis
    filtered_data['total_price'] = filtered_data['price']

    rfm_df = filtered_data.groupby('customer_id').agg({
        'order_purchase_timestamp': 'max',  
        'order_id': 'nunique',  
        'total_price': 'sum'  
    }).reset_index()

    rfm_df.columns = ['customer_id', 'last_purchase_date', 'frequency', 'monetary']
    rfm_df['last_purchase_date'] = pd.to_datetime(rfm_df['last_purchase_date']).dt.date
    most_recent_date = filtered_data['order_purchase_timestamp'].dt.date.max()
    rfm_df['recency'] = rfm_df['last_purchase_date'].apply(lambda x: (most_recent_date - x).days)

    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

    sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), ax=ax[0])
    ax[0].set_title("Top 5 Customers by Recency (days)")

    sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), ax=ax[1])
    ax[1].set_title("Top 5 Customers by Frequency")

    sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), ax=ax[2])
    ax[2].set_title("Top 5 Customers by Monetary Value")

    st.pyplot(fig)

    st.write(rfm_df.head())

with tab5:
    st.subheader("Ratings by Payment Method")
    st.write(payment_method_ratings)

    fig, ax = plt.subplots(figsize=(10, 6))
    payment_method_ratings.plot(kind='bar', ax=ax)
    ax.set_title('Average Review Score by Payment Method')
    ax.set_xlabel('Payment Method')
    ax.set_ylabel('Average Review Score')
    plt.xticks(rotation=45)
    st.pyplot(fig)
