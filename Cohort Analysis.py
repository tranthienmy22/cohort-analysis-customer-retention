# import libraries
import pandas as pd
import numpy as np
import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt
%matplotlib inline
import warnings
warnings.filterwarnings("ignore")

# load csv file into dataframe and get overview of it
df = pd.read_csv('sales.csv')
pd.set_option('display.max_columns', 100)
print("Shape of data is ", df.shape)
df.head()
df.info()


# filter for necessary columns only
df = df[['order_id', 'order_date', 'cust_id', 'Customer Since', 'qty_ordered', 'price', 'value', 'discount_amount', 'total']]
df.head(10)

# it's likely that there're some errors with quantity, as quantity*price-discount is different from total (by a unit price each)
# need to check with data source, in this project let's fix it by subtract 1 from qty-ordered
df['qty_ordered'] = df['qty_ordered'] -1
df.head()

# filter columns again and keep just most relevant columns
df = df.drop(columns=['price', 'value', 'discount_amount'])
df.head()

# format data type of order_date and customer_since from object to datatime 
df['order_date'] = pd.to_datetime(df['order_date'], format='%Y-%m-%d')
df['Customer Since'] = pd.to_datetime(df['Customer Since'], format='%m/%d/%Y')

# change data type of quantity from  float to int
df['qty_ordered'] = df['qty_ordered'].astype('int64')
df.info()

# check and drop duplicates
print(df.duplicated().sum())
df = df.drop_duplicates()
print(df.duplicated().sum())

# change columns name to be more understandable
df.columns = ['order_id', 'order_date', 'customer_id', 'customer_since', 'quantity', 'total_sales']
df.head()

# get statistic summary of all columns
df.describe(include='all')

# unique order_id is less than count of order_id, let's group by order_id, order_date anc customer_id
da = pd.DataFrame(df.groupby(["order_date","customer_id", "order_id"]).agg({'customer_since': min, 'quantity': sum, 'total_sales': sum})).reset_index()
print("Shape of data is ", da.shape)
da.head()

# add new columns - month of order and year of acquirement
da['order_month'] = da['order_date'].dt.to_period('M')
da['acquired_year'] = da['customer_since'].dt.to_period('Y')
da.head()

# as acquired years spread too wide, let's create bins and assign acquired year to them
# change datatype of acquire_year ti int for easier calculation
da.acquired_year = da.acquired_year.astype('str')
da.acquired_year = da.acquired_year.astype('int64')

da['acquired_year_bins'] = pd.cut(x=da.acquired_year, bins= list(range(np.min(da.acquired_year), np.max(da.acquired_year) +5, 5)))
da.head(10)

# count distinct customers in each bin
total_cust = pd.DataFrame(da.groupby('acquired_year_bins', as_index=False).agg({'customer_id':'nunique'}))
total_cust.columns = ['acquired_year_bins','total_cust']
total_cust

# create a bar plot to see the number of unique customers per cohort
fig, ax = plt.subplots(figsize = (10, 6))
sns.barplot(data = total_cust, x = 'acquired_year_bins', y = 'total_cust', palette = 'mako')
plt.title('Number of Customers by Cohort', fontsize = 12)
plt.xlabel('Cohort Year')
plt.ylabel('Number of Customers')

plt.show()

# create pivot table from dataframe and calculate the number of unique customers acquired per month per cohort 
cohort_matrix = pd.pivot_table(da,
                             index='acquired_year_bins',
                             columns= 'order_month',
                             values='customer_id',
                             aggfunc=pd.Series.nunique)

cohort_matrix

# create a heatmap to see the number of unique customers per cohort over time
fig, ax = plt.subplots(figsize = (10, 6))
sns.heatmap(cohort_matrix, annot=True, annot_kws={"size": 7}, fmt=".0f", linewidths = .4, cmap="Blues", cbar_kws={'label': 'Number of Customers'})
plt.title('Number of Customers by Cohort', fontsize = 12)
plt.xlabel('Month')
plt.ylabel('Acquired Year')

plt.show()

cohort_matrix_percentage = cohort_matrix.div(total_cust.iloc[:,1].values, axis=0)
cohort_matrix_percentage

# create a heatmap to see retention rate of customers by cohort over time
fig, ax = plt.subplots(figsize = (10, 6))
sns.heatmap(cohort_matrix_percentage, annot=True, annot_kws={"size": 7}, fmt=".2%", linewidths = .4, cmap="OrRd", cbar_kws={'label': 'Retention Rate'})
plt.title('Retention Rate by Cohort', fontsize = 12)
plt.xlabel('Month')
plt.ylabel('Acquired Year')

plt.show()

# create pivot table from dataframe and calculate the average number of items per order per cohort over time
cohort_matrix_quantity = pd.pivot_table(da,
                             index='acquired_year_bins',
                             columns='order_month',
                             values='quantity',
                             aggfunc=pd.Series.mean)

cohort_matrix_quantity

# create a heatmap to see the average order items per cohort over time
fig, ax = plt.subplots(figsize = (10, 6))
sns.heatmap(cohort_matrix_quantity, annot=True, annot_kws={"size": 7}, fmt=".2f", linewidths = .4, cmap="Purples", cbar_kws={'label': 'Average Items'})
plt.title('Average order items per cohort over time', fontsize = 12)
plt.xlabel('Month')
plt.ylabel('Acquired Year')

plt.show()

# create pivot table from dataframe and calculate the order median sales amount per cohort over time
cohort_matrix_sales= pd.pivot_table(da,
                             index='acquired_year_bins',
                             columns='order_month',
                             values='total_sales',
                             aggfunc=pd.Series.median)

cohort_matrix_sales

# Let's see if customers in certain cohorts spend more money than others
fig, ax = plt.subplots(figsize = (10, 6))
sns.heatmap(cohort_matrix_sales, annot=True, annot_kws={"size": 7}, fmt=".2f", linewidths = .4, cmap="Greens", cbar_kws={'label': 'Median Sales Amount'})
plt.title('Median Order Sales Amount per cohort over time', fontsize = 12)
plt.xlabel('Month')
plt.ylabel('Acquired Year')

plt.show()