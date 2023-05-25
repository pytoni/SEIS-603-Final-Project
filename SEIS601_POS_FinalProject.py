#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#Initial set-up
from datetime import datetime
import pickle
from prettytable import PrettyTable
import os
today = datetime.today().strftime('%Y-%m-%d')
current_month = datetime.strptime(today, '%Y-%m-%d').month
current_year = datetime.strptime(today, '%Y-%m-%d').year
options = {'level_1':0, 'level_2':0}
#Create stored usernames, passwords
users = {"AliNaqvi": "mypassword", "Toni": "mypassword", "Ana": "password123"}
def login():
    """Log in system"""
    global username
    login_count = 0
    print("Welcome to the POS System")
    while login_count < 3:
        username = input("Please enter userid: ")
        mypassword = input("Please enter password: ")
        if (username, mypassword) in users.items() and login_count<3:
            break
        if login_count < 2:
            print("Incorrect user id or password. Please try again")
        login_count +=1
    if login_count == 3:
        print(f"{username} Your Account has been locked out. Please contact your system admin")
        return False
    else:
        print("Log in Successful!")
        return True     
class Item:
    """Class representing an inventory item"""
    def __init__(self, upc, description, item_max_qty, order_threshold, replenishment_order_qty, item_on_hand, unit_price):
        self.upc = upc
        self.description = description
        self.item_max_qty = item_max_qty
        self.order_threshold = order_threshold
        self.replenishment_order_qty = replenishment_order_qty
        self.item_on_hand = item_on_hand
        self.unit_price = unit_price
        
    def UpdateUnitOnHand(self, numberOfItems):
        """Update the item's inventory"""
        self.item_on_hand -= numberOfItems
class SaleItem(Item):
    """Class representing a sale item"""
    def __init__(self, upc, description, unit_price, sold_qty, item_max_qty = 0, order_threshold = 0, replenishment_order_qty = 0, 
                 item_on_hand = 0):
        super().__init__(upc, description, item_max_qty, order_threshold, replenishment_order_qty, item_on_hand, unit_price)
        self.sold_qty = sold_qty
        self.return_qty_max = sold_qty
    def UpdateSoldQty(self, input_qty):
        """Update the sold_qty quantity"""
        self.sold_qty += input_qty
    def UpdateReturnQty(self, return_qty):
        """Update the returned quantity limit"""
        self.return_qty_max -= return_qty
        
#Create and save dictionary item objects
# Check if backup file exists
if os.path.isfile("inventory.pik"):
    #Load data from backup file
    with open("inventory.pik", "rb") as f:
        myItems = pickle.load(f)
else:
    #Load data from source text file
    myItems = {}
    with open("RetailStoreItemData.txt") as f:
        for line in f.readlines()[1:]:
                if line.find('"') > 0: #Clean data
                    left_pos = line.find('"')
                    right_pos = line.rfind('"')
                    line = ''.join([line[:left_pos], line[left_pos:right_pos].replace(',',';'), line[right_pos:]])
                lst = line.strip().split(",")
                myItems[lst[0]] = Item(lst[0], lst[1].replace(';',','), float(lst[2]), float(lst[3]), float(lst[4]), float(lst[5]), 
                                           float(lst[6]))
    #Create backup file
    with open("inventory.pik", "wb") as f:
        pickle.dump(myItems, f)
    
def get_myItems():
    """Get myItems dictionary"""
    with open("inventory.pik", "rb") as f:
        myItems = pickle.load(f)
    return myItems

def get_sales_dict():
    """Get sold items records"""
    try:
        with open("sales_dict.pik", "rb") as f:
                sales_dict = pickle.load(f)
    except:
        sales_dict = {}
    return sales_dict

def get_returns_dict():
    """Get returned items records"""
    try:
        with open("returns_dict.pik", "rb") as f:
                returns_dict = pickle.load(f)
    except:
        returns_dict = {}
    return returns_dict

def total_price(sale_items):
    """Calculate the total price of sold items from a sale dictionary"""
    price = sum(sale_items[upc].unit_price*sale_items[upc].sold_qty for upc in sale_items)
    return price

def save_receipt(receipt_id, input_upc, input_qty, date = today):
    """Save an receipt information into the sales_dict.pik"""
    #If there's existing data in the file
    try:
        with open("sales_dict.pik", "rb") as f:
            sales_dict = pickle.load(f)

        #Write new receipt id into sales_dict
        if receipt_id not in sales_dict:
            item = myItems[input_upc]
            sale_item = SaleItem(item.upc, item.description, item.unit_price, input_qty)
            sales_dict[receipt_id] = {'date': date, 'sale_items': {input_upc: sale_item}}
        else:
            if input_upc in sales_dict[receipt_id]['sale_items']:
                sales_dict[receipt_id]['sale_items'][input_upc].UpdateSoldQty(input_qty)
            else:
                item = myItems[input_upc]
                sale_item = SaleItem(item.upc, item.description, item.unit_price, input_qty)
                sales_dict[receipt_id]['sale_items'][input_upc] = sale_item
           
        #Write updated data back to file
        with open("sales_dict.pik", "wb") as f:
            pickle.dump(sales_dict, f)
            
    #Initilize the sales_dict for the first run
    except:
        with open("sales_dict.pik", "wb") as f:
            sales_dict={}
            item = myItems[input_upc]
            sale_item = SaleItem(item.upc, item.description, item.unit_price, input_qty)
            sales_dict[receipt_id] = {'date': date, 'sale_items': {input_upc:sale_item}}
            pickle.dump(sales_dict, f)   

def get_receipt_max_number():
    """Get the maxium receipt number"""
    try:
        with open("sales_dict.pik", "rb") as f:
            sales_dict = pickle.load(f)
            return max(list(sales_dict.keys()))
    except:
        return 0           

def save_return_items(return_receipt_id, return_upc, return_qty, date = today):
    """Write returned items into returns_dict.pik"""
    #For existing data in the file
    try:
        with open("returns_dict.pik", "rb") as return_file:
            returns_dict = pickle.load(return_file)
            
        if date not in returns_dict:
            returns_dict[date] = {return_receipt_id: {return_upc: return_qty}}
            
        else:
            if return_receipt_id not in returns_dict[date]:
                returns_dict[date][return_receipt_id] = {return_upc: return_qty}
            else:
                newdic = returns_dict[date][return_receipt_id]
                newdic[return_upc] = newdic.setdefault(return_upc,0) + return_qty 
                     
        #Write updated data back to file
        with open("returns_dict.pik", "wb") as return_file:
            pickle.dump(returns_dict, return_file)
    
    #Initialize for the first run
    except:
        with open("returns_dict.pik", "wb") as return_file:
            returns_dict = {date: {return_receipt_id: {return_upc:return_qty}}}
            pickle.dump(returns_dict, return_file)
            
def update_sales_dict(return_receipt_id, return_upc, return_qty):
    """Update Return Quantity Limit in sales_dict.pik"""
    with open("sales_dict.pik", "rb") as f:
        sales_dict = pickle.load(f)
    sales_dict[return_receipt_id]['sale_items'][return_upc].UpdateReturnQty(return_qty)     
         
    # Write updated data back to file
    with open("sales_dict.pik", "wb") as f:
        pickle.dump(sales_dict, f) 
            
def get_items_to_return (sale_items, returned_items):
    """Get the items to return"""
    for key in set(sale_items.keys()) | set(returned_items.keys()):
        items_to_return[key] = sale_items.get(key, 0) - returned_items.get(key, 0)
    return items_to_return

def print_sale_items(receipt_id):
    """Print out the sale items"""
    sales_dict =get_sales_dict()
    output = PrettyTable()
    
    if receipt_id not in sales_dict:
        print("Thank you!")
    else:
        print("Your receipt number is: ", receipt_id)
        print("Your sale items:")
        output.field_names = ["UPC", "Description", "Quantity", "Unit Price", "Total Price"]
        for item in sales_dict[receipt_id]['sale_items']:
            sale_obj = sales_dict[receipt_id]['sale_items'][item]
            row = [item, sale_obj.description, sale_obj.sold_qty, sale_obj.unit_price,
                   round(sale_obj.sold_qty* sale_obj.unit_price,2)]
            output.add_row(row)
        print(output)
        print(f"Your total price is: {total_price(sales_dict[receipt_id]['sale_items']):.2f}")

def inventory_report():
    """Inventory report: listing off all inventory items with name, quantity, threshold, and quantity of items available in store"""
    myItems = get_myItems()
    inv_rpt = PrettyTable()
    inv_rpt.field_names = ["UPC", "Description", "Quantity", "Threshold", "Items on hand"]
    for item in myItems:
        if myItems[item].item_on_hand > 0:
            rowlist = [myItems[item].upc, myItems[item].description, myItems[item].item_max_qty, 
                       myItems[item].order_threshold, myItems[item].item_on_hand]
            inv_rpt.add_row(rowlist)
    print("INVENTORY REPORT")
    print(inv_rpt)
    
def daily_report(date = today):
    """Report of daily sales"""
    sales_dict = get_sales_dict()
    returns_dict = get_returns_dict()

    daily_rpt = PrettyTable()
    daily_rpt.field_names = ["UPC", "Description", "Qty Sold", "Sold Price", "Qty Returned", "Amount Returned"]

    #create a daily items sold
    daily_items_sold = {}      
    for receipt_id in sales_dict:
        if sales_dict[receipt_id]['date'] == date:
            for upc in sales_dict[receipt_id]['sale_items']:
                daily_items_sold[upc] = daily_items_sold.setdefault(upc, 0) + sales_dict[receipt_id]['sale_items'][upc].sold_qty

    #create a daily items returned
    daily_items_returned = {}
    if date not in returns_dict:
        daily_items_returned = {}
    else:
        for receipt_id in returns_dict[date]:
            for upc, qty in returns_dict[date][receipt_id].items():
                daily_items_returned[upc] = daily_items_returned.setdefault(upc, 0) + qty
    
    #Create daily transaction items
    transaction_items = list(daily_items_sold.keys() | daily_items_returned.keys())       
    
    for upc in transaction_items:
        row = [upc, 
               myItems[upc].description, 
               daily_items_sold.setdefault(upc, 0),
               round(myItems[upc].unit_price * daily_items_sold.setdefault(upc, 0),2),
               daily_items_returned.setdefault(upc, 0), 
               round(myItems[upc].unit_price * daily_items_returned.setdefault(upc, 0),2)]
        daily_rpt.add_row(row)
    total_sold_amount = sum(myItems[upc].unit_price*qty for upc, qty in daily_items_sold.items())
    total_return_amount = sum(myItems[upc].unit_price*qty for upc, qty in daily_items_returned.items())
    print("DAILY SALES REPORT")
    print(f"Total Item Sold Price on {date} is: ${total_sold_amount:.2f}")
    print(f"Total Amount Return on {date} is: ${total_return_amount:.2f}")
    print(f"Total Sales in {date} is: ${total_sold_amount-total_return_amount:.2f}")
    print("Total Sales in detail:")
    print(daily_rpt)
    
def monthly_report(month = current_month, year = current_year):
    """Report of monthly sales"""
    sales_dict = get_sales_dict()
    returns_dict = get_returns_dict()

    monthly_rpt = PrettyTable()
    monthly_rpt.field_names = ["UPC", "Description", "Qty Sold", "Sold Price", "Qty Returned", "Amount Returned"]

    #create a monthly items sold
    monthly_items_sold = {}  
    for receipt_id in sales_dict:
        get_year = datetime.strptime(sales_dict[receipt_id]['date'], '%Y-%m-%d').year
        get_month = datetime.strptime(sales_dict[receipt_id]['date'], '%Y-%m-%d').month
        if get_year == year and get_month == month:
            for upc in sales_dict[receipt_id]['sale_items']:
                monthly_items_sold[upc] = monthly_items_sold.setdefault(upc, 0) + sales_dict[receipt_id]['sale_items'][upc].sold_qty

    #create a monthly items returned
    monthly_items_returned = {}
    for date in returns_dict:
        get_year = datetime.strptime(date, '%Y-%m-%d').year
        get_month = datetime.strptime(date, '%Y-%m-%d').month
        if get_year == year and get_month == month:
            for receipt_id in returns_dict[date]:
                for upc, qty in returns_dict[date][receipt_id].items():
                    monthly_items_returned[upc] = monthly_items_returned.setdefault(upc, 0) + qty
    
    #create a monthly transaction
    monthly_transaction_items = list(monthly_items_sold.keys() | monthly_items_returned.keys())       
    
    for upc in monthly_transaction_items:
        row = [upc, 
               myItems[upc].description, 
               monthly_items_sold.setdefault(upc, 0),
               round(myItems[upc].unit_price * monthly_items_sold.setdefault(upc, 0),2),
               monthly_items_returned.setdefault(upc, 0), 
               round(myItems[upc].unit_price * monthly_items_returned.setdefault(upc, 0),2)]
        monthly_rpt.add_row(row)
    total_sold_amount = sum(myItems[upc].unit_price*qty for upc, qty in monthly_items_sold.items())
    total_return_amount = sum(myItems[upc].unit_price*qty for upc, qty in monthly_items_returned.items())
    print("MONTHLY SALES REPORT")
    print(f"Total Item Sold Price in {month}/{year} is: ${total_sold_amount:.2f}")
    print(f"Total Amount Return in {month}/{year} is: ${total_return_amount:.2f}")
    print(f"Total Sales in {month}/{year} is: ${total_sold_amount-total_return_amount:.2f}")
    print("Total Sales in detail:")
    print(monthly_rpt)
    
def new_sale():
    """Process a new sale"""
    global options, receipt_id 
    sales_dict = get_sales_dict()
    myItems = get_myItems()
    
    #Ask for item UPC
    while True:
        input_upc = input("Please enter the UPC: ")
        if input_upc not in myItems.keys() or myItems[input_upc].item_on_hand <=0:
            print(f"Sorry! Item {input_upc} is not available! Please choose another UPC") #In case item is not available
            continue
    
        print("You entered:", myItems[input_upc].description)
        while True:
            try:
                input_qty = int(input("Please enter quantity: "))

                #Check if input is greater than zero:
                if input_qty <= 0:
                    print("Quantity should be greater than zero!")
                    continue

                #Check enough quantity:
                if input_qty > myItems[input_upc].item_on_hand:
                    print(f"Sorry! There is only {myItems[input_upc].item_on_hand} of {myItems[input_upc].description} left!")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a number.")

        #Calculate price
        price = input_qty * myItems[input_upc].unit_price
        print(f"The price for {input_qty} of {myItems[input_upc].description} is: {price:.2f}")
        
        #Update to sales_dict
        save_receipt(receipt_id, input_upc, input_qty)
        
        #Update inventory
        with open("inventory.pik", "rb") as inv_file:
            myItems = pickle.load(inv_file)
            myItems[input_upc].UpdateUnitOnHand(input_qty)
            
        with open("inventory.pik", "wb") as save_inv_file:
            pickle.dump(myItems, save_inv_file)
        break      
    
    #Ask for next options
    print("1 = Sell another item, 2 = Return Item/s, 9 = Complete Sale")
    
    while True:
        try:
            options['level_2'] = int(input("Please select your option: "))
            if options['level_2'] not in [1, 2, 9]:
                print("Invalid input. Please select your option again!")
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a number.")
    if options['level_2'] == 9:        
        print_sale_items(receipt_id)
    elif options['level_2'] == 1:
            print("Sell another item")
            new_sale()
    else:  
        print("Return Item/s")
        item_return()      

def item_return():
    """Process a return"""
    global options, receipt_id
    sales_dict = get_sales_dict()
    myItems = get_myItems()
    
    #Case when returning items during sale process
    if options['level_1'] == 1:
        return_receipt_id = receipt_id
        items_to_return = sales_dict[receipt_id]['sale_items']
    else:
        #Return items that are sold previously, need to ask for the receipt id
        while True:
            try:
                return_receipt_id = int(input("Please enter the receipt number: "))
                
                if return_receipt_id not in sales_dict:
                    print("Invalid receipt id. Please enter receipt id again!")
                else: 
                    break
            except:
                print("The receipt number is wrong or not existing. Please try again")
        
        items_to_return = sales_dict[return_receipt_id]['sale_items']
              
    #Ask for return option    
    print("1 = Return single item, 2 = Return all items")
    while True:
        try:
            return_option = int(input("Please select your option: "))
            if return_option not in [1, 2]:
                print("Invalid input. Please select your option again!")
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a number.")
        
    if return_option == 1:
        #Ask for item UPC
        print("List of items to return: ", list(items_to_return.keys()))
                
        while True:
            return_upc = input("Please enter UPC to be returned: ")
            if return_upc not in items_to_return.keys():
                print("Invalid UPC. Please enter UPC again!")
            else:
                break
        
        print("You enter ", myItems[return_upc].description)
                
        while True:
            try:
                return_qty = int(input("Please enter quantity: "))
                if return_qty < 0:
                    print("Quantity should not smaller than zero!")
                    continue
                if return_qty > sales_dict[return_receipt_id]['sale_items'][return_upc].return_qty_max:
                    print(f"Sorry. You have only {sales_dict[return_receipt_id]['sale_items'][return_upc].return_qty_max} to return!")
                else:
                    break
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        #Update inventory
        with open("inventory.pik", "rb") as f:
            myItems = pickle.load(f)
            myItems[return_upc].UpdateUnitOnHand(-return_qty)
        with open("inventory.pik", "wb") as f:
            pickle.dump(myItems, f)
        
        #Update sale items
        if options['level_1'] == 1:
            #just update sale items again
            with open("sales_dict.pik", "rb") as f:
                sales_dict = pickle.load(f)
            sales_dict[return_receipt_id]['sale_items'][return_upc].sold_qty -= return_qty
            # Write updated data back to file
            with open("sales_dict.pik", "wb") as f:
                pickle.dump(sales_dict, f)            
        else:
                       
            #Update the returned items
            save_return_items(return_receipt_id, return_upc, return_qty)
            #update return limit
            update_sales_dict(return_receipt_id, return_upc, return_qty)
            
        print("Return Amount: ",round(return_qty*myItems[return_upc].unit_price,2))
        
    if return_option == 2:
        while True:
            confirm = input("Are you sure you want to return all? y = yes, n = no ")
            if confirm not in ['y', 'n']:
                print("Invalid input. Please choose y = yes, n = no")
            else:
                break
        if confirm == 'y':
            
            #Update inventory
            with open("inventory.pik", "rb") as f:
                myItems = pickle.load(f)
                for upc, obj in items_to_return.items():
                    myItems[upc].UpdateUnitOnHand(-obj.return_qty_max)          
            with open("inventory.pik", "wb") as f:
                pickle.dump(myItems, f)
            
            #Update sale items
            if options['level_1'] == 1:
                with open("sales_dict.pik", "rb") as f:
                    sales_dict = pickle.load(f)
                del sales_dict[receipt_id]
                # Write updated data back to file
                with open("sales_dict.pik", "wb") as f:
                    pickle.dump(sales_dict, f)
                
            else:  #Update the returned items
                #For existing data in the file
                for return_upc, obj in items_to_return.items():
                    save_return_items(return_receipt_id, return_upc, obj.return_qty_max)
                                
                #update return limit 
                with open("sales_dict.pik", "rb") as f:
                    sales_dict = pickle.load(f)
                for upc in sales_dict[return_receipt_id]['sale_items']:
                    sales_dict[return_receipt_id]['sale_items'][upc].return_qty_max=0
                    
                # Write updated data back to file
                with open("sales_dict.pik", "wb") as f:
                    pickle.dump(sales_dict, f) 
                                 
            return_amount = 0
            print("You enter:\n")
            item_list = PrettyTable()
            item_list.field_names =["UPC", "Description", "Quantity", "Unit Price", "Total Price"]
            for return_upc, obj in items_to_return.items():
                row = [return_upc, myItems[return_upc].description, obj.return_qty_max,
                      round(myItems[return_upc].unit_price,2), round(obj.return_qty_max*myItems[return_upc].unit_price,2)]
                return_amount += obj.return_qty_max*myItems[return_upc].unit_price
                item_list.add_row(row)
      
            print(item_list)          
            print(f"Return Amount: {return_amount:0.2f}")
                
    #Ask for next options            
    if options['level_1'] == 1:
        print("1 = Sell another item, 2 = Return Item/s, 9 = Complete Sale")
        while True:
            try:
                options['level_2'] = int(input("Please select your option: "))
                if options['level_2'] not in [1, 2, 9]:
                    print("Invalid input. Please select your option again!")
                else:
                    break
            except ValueError:
                print("Invalid input. Please enter a number.")
        if options['level_2'] == 9:
            print_sale_items(receipt_id)
        elif options['level_2'] == 1:
                print("Sell another item")
                new_sale()
        else:
            print("Return Item/s")
            item_return()
      
#Main part of POS system
#Initialize run myItems
try:
    with open("inventory.pik", "rb") as f:
        myItems = pickle.load(f)
    # Write updated data back to file
    with open("inventory.pik", "wb") as f:
        pickle.dump(myItems, f)  
except: #Initialize for the first run
    with open("inventory.pik", "wb") as f:
        pickle.dump(myItems, f)

while True:
    if login():        
        
        print("Please select your options")        
        while True:
            print("1 = New Sale, 2 = Return Item/s, 3 = Backroom Operations, 9 = Exit Application")
            while True:
                try:
                    options['level_1'] = int(input("Please select your option: "))
                    if options['level_1'] not in [1, 2, 3, 9]:
                            print("Invalid input. Please select your option again!")
                    else:
                        break
                except ValueError:
                    print("Invalid input. Please enter a number.")

            #Option new sale
            if options['level_1'] == 1:
                print("New Sale")
                receipt_id = get_receipt_max_number() + 1
                new_sale()
            elif options['level_1'] == 2:
                print("Return Item/s")
                item_return()
                
            elif options['level_1'] == 9:
                print("Thank you!")
                print("Exit Application")
                break
            else:
                print("Go to Backroom Operations!")
                break
        if options['level_1'] in [3, 9]:
            break
        else:
            continue
    else:
        break          
             


# In[ ]:


inventory_report()   
daily_report()
monthly_report()

