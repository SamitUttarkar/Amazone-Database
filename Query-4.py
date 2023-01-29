# Create dataframe for pastOrders using aggregation pipeline
df_pastOrders = pd.DataFrame(myDB.pastOrders.aggregate([{
   '$project': {
'_id': 1,
'order_date': '$order_date',
'customer_id': '$customer_id',
# Raise Sub-documents to top-level under new name 'product_id': '$order_details.product_id', 'quantity': '$order_details.quantity',
'cost': '$order_details.cost',
'total_cost': '$total_cost',
'partner_id': '$partner_id',
'supplier_id': '$supplier_id',
'order_status': '$order_status'
} }]))
# Cleaning embedded values
lis = ['product_id','quantity','cost']
for i in lis:
   df_pastOrders[i] = df_pastOrders[i].apply(lambda x: x[0])
# Create dataframe for inventoryRecord
df_inventoryRecord = pd.DataFrame(myDB.dailyInventoryRecord.aggregate([{
   '$project': {
       '_id': 0,
       'supplier_id': '$_id.supplier_id',
       'product_id': '$_id.product_id',
       'date': '$inventory_data.datetime',
       'quantity':'$inventory_data.inventory_quantity'
} }]))
# Cleaning embedded values
lis = ['date','quantity']
for i in lis:
   df_inventoryRecord[i] = df_inventoryRecord[i].apply(lambda x: x[0])
# Splitting pastOrders for each month
df_October = df_pastOrders.loc[(df_pastOrders['order_date'] > '2022-10-01') &
(df_pastOrders['order_date'] <= '2022-10-31')]
df_November = df_pastOrders.loc[(df_pastOrders['order_date'] > '2022-11-01') &
(df_pastOrders['order_date'] <= '2022-11-30')]
# Create dataframe for products for referencing product names with product ID
df_products = pd.DataFrame(myDB.products.aggregate([{
'$project': {
       '_id': 1,
       'name': '$name',
       'category': '$category'
   }
}]))
df_products = df_products.rename(columns={"_id": "product_id"})
# Merge monthwise pastOrders with products and drop redundant columns df_salesAnalysis_October = pd.merge(df_October,df_products,on='product_id') df_salesAnalysis_October = df_salesAnalysis_October.drop(['_id', 'customer_id', 'partner_id','supplier_id','order_status'], axis=1)
df_salesAnalysis_November = pd.merge(df_November,df_products,on='product_id')
df_salesAnalysis_November = df_salesAnalysis_November.drop(['_id', 'customer_id',
'partner_id','supplier_id','order_status'], axis=1)
# Grouping records bases on quantity and cost
df_quantity_October = df_salesAnalysis_October.groupby('name')['quantity'].sum()
df_quantity_October = df_quantity_October.reset_index()
df_Cost_October = df_salesAnalysis_October.groupby('name')['cost'].mean()
df_Cost_October = df_Cost_October.reset_index()
df_quantity_November = df_salesAnalysis_November.groupby('name')['quantity'].sum()
df_quantity_November = df_quantity_November.reset_index()
df_Cost_November = df_salesAnalysis_November.groupby('name')['cost'].mean()
df_Cost_November = df_Cost_November.reset_index()
# Plot sales performance for each product in October
fig, ax1 = plt.subplots(figsize=(20,7))
ax2 = ax1.twinx()
ax1.bar(df_quantity_October['name'],df_quantity_October['quantity'], color = 'g') ax2.plot(df_Cost_October['name'],df_Cost_October['cost'],'b-') ax1.set_xlabel('Product Name')
ax1.set_ylabel('Quantity Ordered',color = 'g')
ax2.set_ylabel('Price',color = 'b')
ax1.set_xticklabels(df_quantity_October['name'],rotation = 90,size = 8) plt.title('October Sales')
plt.show()
# Plot sales performance for each product in November
fig, ax1 = plt.subplots(figsize=(20,7))
ax2 = ax1.twinx()
ax1.bar(df_quantity_November['name'],df_quantity_November['quantity'], color = 'g') ax2.plot(df_Cost_November['name'],df_Cost_November['cost'],'b-') ax1.set_xlabel('Product Name')
ax1.set_ylabel('Quantity Ordered',color = 'g')
ax2.set_ylabel('Price',color = 'b') 
ax1.set_xticklabels(df_quantity_November['name'],rotation = 90,size = 8) plt.title('November Sales')
plt.show()

#Manager checking inventory

# Extracting day only from datetime for each month
df_salesAnalysis_October['order_day'] = df_salesAnalysis_October.order_date.dt.day
df_salesAnalysis_November['order_day'] = df_salesAnalysis_November.order_date.dt.day
# Grouping daily sales perfomance for each month
sales_byDay_Oct = df_salesAnalysis_October.groupby('order_day')['total_cost'].sum()
sales_byDay_Oct = sales_byDay_Oct.reset_index()
sales_byDay_Nov = df_salesAnalysis_November.groupby('order_day')['total_cost'].sum() sales_byDay_Nov = sales_byDay_Nov.reset_index()
# Plotting daily sales performance for October
plt.figure(figsize = (20,7))
sns.barplot(x="order_day",
          y="total_cost",
          data=sales_byDay_Oct)
plt.title('Sales per day for October')
# Plotting daily sales performance for November
plt.figure(figsize = (20,7))
sns.barplot(x="order_day",
          y="total_cost",
          data=sales_byDay_Nov)
plt.title('Sales per day for November')