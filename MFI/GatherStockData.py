import urllib
import MySQLdb
from bs4 import BeautifulSoup
import time
import argparse
import datetime
import sys
import MFI

#standard development arg string: -s 0 -e 1 -a "localhost" -u "hector" -p "#BEck59187" -d "stocks"

#Parsing Args
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--start", type=int,
                    help="Starting Percentage of analysis")
parser.add_argument("-e", "--end", type=int,
                    help="Ending Percentage of analysis")
parser.add_argument("-a", "--host",
                    help="Database host address")
parser.add_argument("-u", "--username",
                    help="Database User Name")
parser.add_argument("-p", "--password",
                    help="Database Password")
parser.add_argument("-d", "--database",
                    help="Using Database")
args = parser.parse_args()

#timer
start = time.time()
#Connect to the database server
db = MySQLdb.connect(args.host, args.username, args.password, args.database)
c=db.cursor()

#Get all the available stock symbols
c.execute ("select sym from ticker")
action = db.cursor()
results = c.fetchall()

i = 0
x=[]
for string in results:

#only execute under two conditions: are we between the bracke set in the arguements and is there no entry already in current?
    if ((i >= (args.start * len(results) // 100)) and (i <= (args.end * len(results) // 100))) and (MFI.Check_For_Exisiting_Entries(db, string[0]) == 0):
        
        #get current time for database entry
        now = datetime.datetime.now()

        #get time for performance
        t1 = time.time()

        #build the URL, download the html file, and generate the soup
        j = 0

        #if google shuts down the connection we will sleep for 10 secs, try again. Give it 3 tries
        while j < 3:
            try:
                url = MFI.Generate_Stock_URL(string[0])
                html = MFI.Get_Page(url)
                Soup = BeautifulSoup(html)
                break
            except:
                time.sleep(10)
                j = j + 1
                


        #Get key data
        try:
            price = MFI.Get_Price(string[0])
            cap = MFI.Get_Data("Total Common Shares Outstanding\n", "balannualdiv", Soup) * price
            reteq = MFI.Compute_Return_On_Capital(Soup)
            earnyield = MFI.Compute_Earnings_Yield(Soup, price)
        except:
            print "Error gathering data for ", string[0]
            i = i + 1
            continue
            

        #remove symbols that do not have corresponding data
        if (price == 0) or (reteq == 0) or (earnyield == 0):
            ActionString = "delete from ticker where sym='" + string[0] + "';"
            try:
                action.execute(ActionString)
                db.commit()
                print "Record for ", string[0], "deleted"
            except:
                db.rollback()
                print "Data for ", string[0], " could not be found and the entry could not be removed"
                
        #If everything checks out insert into the current database 
        else:
            #build and execute the query for inserting into the current database
            ActionString = "insert into current (ticker, cap, reteq, earnyield, price) values ( '" + string[0] + "' , '" + str(cap) + "' , '" + str(reteq) + "' , '" + str(earnyield) + "' , '" + str(price) + "');"       
            try:
                action.execute (ActionString)
                db.commit()
            except:
                db.rollback()
                print "Error: could not commit symbol: ", string[0]

             
                
        t2 = time.time()

        x.append(t2-t1)

    i = i +1

i = 0
sum = 0
for a in x:
    sum = sum + a
    i = i + 1
print "Avg query time: ", sum/i, " sec"
print "total time: ", time.time() - start, " sec"