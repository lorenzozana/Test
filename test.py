#! /usr/bin/env python

# Lorenzo Zana July 2017
# lorenzozana@gmail.com
#
# Usage:
# test.py <input_file.tx> <OPTIONAL: output_file_name.txt>
#
# PLEASE NOTE: the Calculated Volume Weighted Stock Price and the GBCE All Share Index are calculated from the same output file. If you have different ensembles, use different output files for each of them.

import os, sys, math
import numpy as np
import time



        
convert_perc = lambda x: float(x.strip("%"))/100.
# Get the input  file
if len(sys.argv) < 2:
    print "\nYou must enter the input file you wish to analyze as the first arguement. Exiting \n"
    sys.exit(1)
pass
try:
    input_file = file( sys.argv[1], 'r')
    input_file_name = sys.argv[1]
except:
    print "\nThe entered file cannot be opened, please enter a vaild input file. Exiting. \n"
    sys.exit(1)

#Define the output file
if len(sys.argv) > 2:    output_file_name = sys.argv[2]
else:                    output_file_name = "output.txt"


                                    

data = np.genfromtxt(input_file_name, names=True, dtype=None, converters={3: convert_perc})

#store variables so will be easier to use

Stock_Symbol = []
Type = []
l_div = []
f_div = []
p_val = []

tot_entries = data.shape[0]
print "Data has " + str(tot_entries) + " entries"

for i in range(0,tot_entries):
    Stock_Symbol.append(data[i][0])
    Type.append(data[i][1])
    l_div.append(float(data[i][2])/100)  # value is in pence
    f_div.append(data[i][3])
    p_val.append(float(data[i][4])/100) # value is in pence
 

#Getting STOCK of interest
list_of_stock = "Enter the stock of interest between (" + ",".join(Stock_Symbol) +") :"
input_stock = raw_input(list_of_stock)
price_stock = float(input("Enter price (pounds):")) 

#Get the time
timestamp = time.time()
   
#defining functions with default values in case the Stock is not in the database
div_y = 0.0
P_E = 0.0
n_shares = 0.0

buy_indicator = 0  # I will assume if the last Dividend is > 0.0 I will buy it, if not I will sell it  ( buy_indicator = 0 --> Sell  buy_indicator = 1 --> Buy)
check_stock_db = 0

for i in range(0,tot_entries):
    if Stock_Symbol[i] == input_stock:
        print "found stock " + input_stock + " in database"
        check_stock_db = 1
        if Type[i]=="Common":
            print "Stock type is Common"
            div_y = l_div[i]/price_stock
            
        else:
            print "Stock type is Preferred"
            div_y = f_div[i]*p_val[i]/price_stock
            

        if div_y != 0.0:
            print "Calculating P/E ratio"
            P_E = 1./div_y
        else: print "Dividend is= 0.0 --> Cannot calculate P/E ratio"
    
        n_shares = price_stock / p_val[i]

        if l_div[i] > 0.0 : buy_indicator = 1

if check_stock_db == 0: 
    print "NO STOCK FOUND in the database !!!!"            
    sys.exit(1)

#Print first results
result = "Dividend Yield= " + str(div_y) + "\nP/E ratio= " + str(P_E)
print result



#Check how many transaction I have already done
num_lines = sum(1 for line in open(output_file_name))
print "Total number of entries already on file=" + str(num_lines)

#Define 15 minutes in seconds (timestamp is in seconds)
default_min = 900.0

#if at least a transaction, get a record of the previous ones (a file is saved every time, for book keeping) One can create different files for different assets

VWSP_num = 0.0   #Volume Weighted Stock Price numerator
VWSP_den = 0.0   #Volume Weighted Stock Price denominator

GBCE_All_Share_Index = 1.0

if num_lines > 0 :
    output_data = np.genfromtxt(output_file_name)
    if num_lines == 1 :
        GBCE_All_Share_Index = GBCE_All_Share_Index * output_data[3] 
        if output_data[0]>(timestamp-default_min) :  # Just the transactions in the last 15 minutes
            VWSP_num += output_data[3] * output_data[1]   # Sum price_i * quantity_i
            VWSP_den += output_data[1]                       # Sum quantity_i 
    else:
        for i in range(0,num_lines):
            GBCE_All_Share_Index = GBCE_All_Share_Index * output_data[i][3] 
            if output_data[i][0]>(timestamp-default_min) :  # Just the transactions in the last 15 minutes
                VWSP_num += output_data[i][3] * output_data[i][1]   # Sum price_i * quantity_i
                VWSP_den += output_data[i][1]                       # Sum quantity_i 

#Let's add now the last transaction
GBCE_All_Share_Index = GBCE_All_Share_Index * price_stock
GBCE_All_Share_Index = math.sqrt(GBCE_All_Share_Index)

VWSP_num += price_stock * n_shares   # Sum price_i * quantity_i
VWSP_den += n_shares                 # Sum quantity_i 

VWSP = 0.0
if VWSP_den > 0.0 : VWSP = VWSP_num / VWSP_den

print "The Volume Weighted Stock Price based on trades in past 15 minutes = " + str(VWSP)
print "The GBCE All Share Index = " + str(GBCE_All_Share_Index)


output_file = file(output_file_name, 'w')
#Rewrite the output file with all the previous records
if num_lines > 0:
    if num_lines == 1:
        output_file.write(str(output_data[0]) + " \t" + str(output_data[1]) + " \t" + str(output_data[2]) + " \t" + str(output_data[3]) +"\n")
    else:
        for i in range(0,num_lines):
            output_file.write(str(output_data[i][0]) + " \t" + str(output_data[i][1]) + " \t" + str(output_data[i][2]) + " \t" + str(output_data[i][3]) + "\n") 

#Add the last record
output_file.write(str(timestamp) + " \t" + str(n_shares) + " \t" + str(buy_indicator) + " \t" + str(price_stock) )
    
