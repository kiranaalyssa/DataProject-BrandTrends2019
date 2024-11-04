import datetime
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Baca style CSS
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Menambahkan headline dengan gaya dari CSS
st.markdown('<div class="headline">Visualisasi Penjualan Desember 2019: Tren Merek, Distribusi Produk, dan Analisis Korelasi</div>', unsafe_allow_html=True)

# Baca dataset
dataset = pd.read_csv('https://storage.googleapis.com/dqlab-dataset/retail_raw_reduced.csv')
dataset['order_month'] = dataset['order_date'].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").strftime('%Y-%m'))
dataset['gmv'] = dataset['item_price'] * dataset['quantity']

# Layout dashboard: Baris pertama untuk Plot 1 dan Plot 2
col1, col2 = st.columns(2)

# Plot 1: Daily Sold Quantity Dec 2019 - Breakdown by Brands
with col1:
    top_brands = (dataset[dataset['order_month']=='2019-12'].groupby('brand')['quantity']
                    .sum()
                    .reset_index()
                    .sort_values(by='quantity',ascending=False)
                    .head(5))
    dataset_top5brand_dec = dataset[(dataset['order_month']=='2019-12') & (dataset['brand'].isin(top_brands['brand'].to_list()))]

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    dataset_top5brand_dec.groupby(['order_date', 'brand'])['quantity'].sum().unstack().plot(marker='.', cmap='plasma', ax=ax1)

    ax1.set_title('Tren Penjualan Harian Brand Teratas - Desember 2019', loc='center', pad=30, fontsize=15, color='blue')
    ax1.set_xlabel('Order Date', fontsize=12)
    ax1.set_ylabel('Quantity', fontsize=12)
    ax1.grid(color='darkgray', linestyle=':', linewidth=0.5)
    ax1.set_ylim(ymin=0)

    # Anotasi lonjakan
    ax1.annotate('Terjadi lonjakan', xy=(7, 310), xytext=(8, 300),
                 weight='bold', color='red',
                 arrowprops=dict(arrowstyle='->',
                                 connectionstyle="arc3",
                                 color='red'))
    st.pyplot(fig1)

# Plot 2: Number of Sold Products per Brand, December 2019
with col2:
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    dataset_top5brand_dec.groupby('brand')['product_id'].nunique().sort_values(ascending=False).plot(kind='bar', color='green', ax=ax2)
    ax2.set_title('Jumlah Produk Terjual per Brand - Desember 2019', loc='center', pad=30, fontsize=15, color='blue')
    ax2.set_xlabel('Brand', fontsize=15)
    ax2.set_ylabel('Number of Products', fontsize=15)
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=0)
    st.pyplot(fig2)

# Layout dashboard: Baris kedua untuk Plot 3 dan Plot 4
col3, col4 = st.columns(2)

# Plot 3: Stacked Chart for Products Sold >=100 and <100
with col3:
    dataset_top5brand_dec_per_product = dataset_top5brand_dec.groupby(['brand','product_id'])['quantity'].sum().reset_index()
    dataset_top5brand_dec_per_product['quantity_group'] = dataset_top5brand_dec_per_product['quantity'].apply(lambda x: '>= 100' if x>=100 else '< 100')
    s_sort = dataset_top5brand_dec_per_product.groupby('brand')['product_id'].nunique().sort_values(ascending=False)

    fig3, ax3 = plt.subplots(figsize=(10, 5))
    dataset_top5brand_dec_per_product.groupby(['brand', 'quantity_group'])['product_id'].nunique().reindex(index=s_sort.index, level='brand').unstack().plot(kind='bar', stacked=True, ax=ax3)
    ax3.set_title('Distribusi Jumlah Produk Terjual per Brand: >= 100 vs < 100', loc='center', pad=30, fontsize=15, color='blue')
    ax3.set_xlabel('Brand', fontsize=15)
    ax3.set_ylabel('Number of Products', fontsize=15)
    ax3.set_xticklabels(ax2.get_xticklabels(), rotation=0)
    st.pyplot(fig3)

# Plot 4: Scatterplot for Quantity vs GMV per Product
with col4:
    data_per_product_top5brand_dec = dataset_top5brand_dec.groupby('product_id').agg({'quantity': 'sum', 'gmv':'sum', 'item_price':'median'}).reset_index()

    fig4, ax4 = plt.subplots(figsize=(10, 8))
    ax4.scatter(data_per_product_top5brand_dec['quantity'],data_per_product_top5brand_dec['gmv'], marker='+', color='red')
    ax4.set_title('Korelasi Antara Jumlah Terjual dan GMV per Produk\nTop 5 Merek Desember 2019', fontsize=15, color='blue')
    ax4.set_xlabel('Quantity', fontsize=12)
    ax4.set_ylabel('GMV (in Millions)', fontsize=12)
    ax4.set_xlim(xmin=0,xmax=300)
    ax4.set_ylim(ymin=0,ymax=200000000)

    # Menampilkan label y-axis dalam juta
    labels, locations = plt.yticks()
    plt.yticks(labels, (labels/1000000).astype(int))

    st.pyplot(fig4)