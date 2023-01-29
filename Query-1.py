# 1. Read the customer's data
# Connecting to products collection customersCollection = myDB["customers"] # set customer
customer_id = "C1"
c1_doc = customersCollection.find_one({"_id": "C1"})
customer_coordinates = c1_doc["addresses"][-1]['location']['coordinates']
# 2. Set order details
order_datetime = datetime.datetime(2023, 1, 9, 17, 31, 00)
order_id = order_datetime.strftime("%Y%M%D%H%M%S") + customer_id
ordered_product_id = "FP1"
ordered_quantity = 3
shipping_id = c1_doc["addresses"][-1]["_id"]
# 3. Calculate total cost of the order
# read cost of the product
productsCollection = myDB["products"]
ordered_product_doc = productsCollection.find_one({"_id": "FP1"}) cost_per_product = ordered_product_doc['std_price']
 # multiply it with quantity
total_cost = cost_per_product * ordered_quantity
# 4. Assign a Morrisons store which is nearest to the customer # read real-time inventory in store collection suppliersCollection = myDB['suppliers']
morrisons_stores = suppliersCollection.aggregate([
     {
         "$geoNear": {
             "near": { 'type': "Point", "coordinates": customer_coordinates },
             "distanceField": "dist.calculated",
             "maxDistance": 2000,
} },
     {'$unwind': '$realtime_inventory'},
    {'$match': {'realtime_inventory.product_id': ordered_product_id,
'realtime_inventory.quantity': {'$gte': ordered_quantity}}},
     {'$sort': {"dist.calculated": 1}},
     {'$limit': 1}
])
for i in morrisons_stores:
     # pprint.pprint(i)
     nearest_supplier_id = i["_id"]
     nearest_supplier_coordinates = i["location"]["coordinates"]
     assigned_supplier_inventory_timestamp = i["realtime_inventory"]["timestamp"]
     assigned_supplier_inventory_quantity = i["realtime_inventory"]["quantity"]
     dist_from_supplier_to_customer = i["dist"]["calculated"]
# 5. Assign a partner to deliver the product
# read driver's locations
partnersCollection = myDB['partners']
# Find the nearest partner to the Morrison store partnersCollection.create_index([("availabilty.location", "2dsphere")]) find_nearest_partner = [
     {
         "$geoNear": {
             "near": { 'type': "Point", "coordinates": nearest_supplier_coordinates },
             "distanceField": "dist.calculated",
             "maxDistance": 2000,
} },
     {'$match': {'availabilty.is_active': 1, 'availabilty.on_delivery': 0}},
     {'$sort': {"dist.calculated": 1}},
     {'$limit': 1}
]
available_partners = partnersCollection.aggregate(find_nearest_partner)
for i in available_partners:
     assigned_partner_id = i["_id"]
     dist_from_partner_to_supplier = i["dist"]["calculated"]
     assigned_partner_coordinates = i["availabilty"]["location"]["coordinates"]
# 6. Update all docs (customers.currnet_order, partners.status,
suppliers_realtime_inventory, dailyInventoryRecord)
 # Update customers
new_order = {
     "_id": order_id,
     "date": order_datetime,
     "order_status": 3,
     "total_cost": total_cost,
     "partner_id": assigned_partner_id,
     "shipping_id": shipping_id,
     "supplier_id": nearest_supplier_id,
     "order_details": [{"product_id": ordered_product_id}]
 }
customersCollection.update_one(
     {"_id": customer_id},
     {"$push": {"current_orders": new_order}}
 )
# Update partners

  update_driver_status = partnersCollection.update_one({'_id':"PA2s"},{'$set':{
'availabilty.on_delivery': 0 }})
# Update dailyInventoryRecord
dailyInventoryRecordCollection = myDB["dailyInventoryRecord"]
 new_inventory_record = {
     'datetime': assigned_supplier_inventory_timestamp,
     'inventory_quantity': assigned_supplier_inventory_quantity
 }
daily_inventory_record_id = {
     'supplier_id': nearest_supplier_id,
     'product_id': ordered_product_id,
     'start_date': order_datetime.strftime("%d/%m/%Y 00:00"),
     'end_date': order_datetime.strftime("%d/%m/%Y 23:59")
 }
dailyInventoryRecordCollection.update_one(
     {"_id": daily_inventory_record_id},
     {
        "$set": {
            "supplier_location.longitude":  nearest_supplier_coordinates[0],
            "supplier_location.latitude": nearest_supplier_coordinates[1]
            },
        "$addToSet": {"inventory_data": new_inventory_record}
    },
     upsert = True
 )
# Update suppliers
updated_quantity = assigned_supplier_inventory_quantity - ordered_quantity
update_suppliers = suppliersCollection.update_one({'_id':nearest_supplier_id,"realtime_inventory.product_id":ordered_product_id},{'$set':{ 'realtime_inventory.$.quantity':updated_quantity,'realtime_inventory.$.timestamp':order_datetime}})
# 7. Return
 # Read product details
product_detail = productsCollection.find({"_id":ordered_product_id},{"_id":0,"name":1,"avg_ratings":1,"std_price":1})
for i in product_detail:
     product_name = i["name"]
     product_rating=i["avg_ratings"]
     product_price=i["std_price"]
print("Product name:",product_name,"rating:",product_rating, "price:",product_price)
# Read delivery details
product_detail =
partnersCollection.find({"_id":assigned_partner_id},{"_id":0,"name":1,"phone":1,"deliveries_made":1})
 for i in product_detail:
     partner_name = i["name"]
     partner_phone=i["phone"]

partner_deliveries=i["deliveries_made"]
print("Partner name:",partner_name,"phone number:",partner_phone, "number of delivery made:",partner_deliveries)
# Calc ETA
dist_partner_drives = dist_from_partner_to_supplier + dist_from_supplier_to_customer partner_driving_speed = 300 # metre per minute
estimated_minutes_for_driving = dist_partner_drives / partner_driving_speed
eta = order_datetime + datetime.timedelta(minutes = estimated_minutes_for_driving) print(f'Ordered Time: {order_datetime} \nDelivery Partner\'s Location: {assigned_partner_coordinates} \nETA: {eta}')