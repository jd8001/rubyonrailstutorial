import urllib
import MySQLdb
from bs4 import BeautifulSoup
import time
import argparse
import datetime
import sys

def Generate_Stock_URL(TickerSymbol):
    """This function will return the appropiate URL from google finance for the TickerSymbol provided"""
    front_string = "http://www.google.com/finance?q="
    back_string = "&fstype=ii"
    result = front_string + TickerSymbol + back_string
    return result

def Get_Page(URL):
    """This funaction will return the html file"""
    html = urllib.urlopen(URL).read()
    return html

def Get_Data(DataString, ParentID, Soup):
    """Pulls the data indicated by DataString from the annual statement in Soup"""
    Initials = Soup.find_all("td", text=DataString)
    
    #itterate through Initials looking for annual data
    for string in Initials:
        substring = string.find_parent("div")
        if substring['id'] == ParentID:
            #found the appropiate data, parse the row for return value
            value = string.find_next_sibling("td")

            #some values are set to '-' for zero, return 0 insteadt of -
            if value.string == "-":
                return 0.0
            
            #determine if in millions, throusands, etc
            power = substring.find_next("th")

            exp = 1
            if "Millions" in power.string:
                exp = 1e6
            elif "Thousands" in power.string:
                exp = 1e3
            elif "Billions" in power.string:
                exp = 1e9
            else:
                print "No exponent found"
            return float(value.string.replace(',', '')) * exp

    #print "Error, no data was found for %s with Parent %s", DataString, ParentID
    return 0.0

def Get_Price(Ticker):
    url = "http://www.google.com/finance/historical?q=" + Ticker
    html = Get_Page(url)
    soup = BeautifulSoup(html) 
    tag = soup.find("div", id='prices')
    i = 0
    for dec in tag.descendants:
        if i == 28:
            return float(dec.string.replace(',', ''))
        i = i + 1
    
    
            
    
    
    
    
    

def Compute_Return_On_Capital(Soup):
    """Returns the Net Working Capital Calculation from the page loaded into the Soup"""

    #Compute the numerator of the returned value
    Numerator = Get_Data("Total Revenue\n", "incannualdiv", Soup) -  Get_Data("Total Operating Expense\n", "incannualdiv", Soup)
    
    #Compute the denominator
    Denominator = Get_Data("Total Current Assets\n", "balannualdiv", Soup) - Get_Data("Total Current Liabilities\n", "balannualdiv", Soup) + Get_Data("Property/Plant/Equipment, Total - Gross\n", "balannualdiv", Soup) + Get_Data("Accumulated Depreciation, Total\n", "balannualdiv", Soup)

    if Denominator == 0:
        return 0.0

    return Numerator/Denominator

def Compute_Earnings_Yield(Soup,Price):
    """Returns the Earnings Yield Calculation from the page loaded into the Soup and the current share Price"""

    #Compute the numerator of the returned value
    Numerator = Get_Data("Total Revenue\n", "incannualdiv", Soup) -  Get_Data("Total Operating Expense\n", "incannualdiv", Soup)

    #Compute the Denominator - Multiple steps for code readibility
    Denominator = (Price * Get_Data("Total Common Shares Outstanding\n", "balannualdiv", Soup)) + Get_Data("Notes Payable/Short Term Debt\n", "balannualdiv", Soup)
    Denominator = Denominator + Get_Data("Accounts Payable\n", "balannualdiv", Soup) + Get_Data("Total Long Term Debt\n", "balannualdiv", Soup)
    Denominator = Denominator + Get_Data("Redeemable Preferred Stock, Total\n", "balannualdiv", Soup) + Get_Data("Preferred Stock - Non Redeemable, Net\n", "balannualdiv", Soup)
    Denominator = Denominator + Get_Data("Minority Interest\n", "balannualdiv", Soup) - Get_Data("Cash and Short Term Investments\n", "balannualdiv", Soup)

    if Denominator == 0:
        return 0.0

    return Numerator/Denominator

def Format_Stock_Symbol_String(Ticker):
    value = Ticker.replace(' ', '')
    value = value.replace('(', '')
    value = value.replace(')', '')
    value = value.replace(',', '')
    value = value.replace('\n', '')
    value = value.replace('\r', '')
    return value

def Populate_Stock_Symbols(Database, Table, FilePath):
    cursor = Database.cursor()
    Infile = open(FilePath, 'r')

    count = 0
    string = "x"
    while string != "":
        string = Infile.readline()
        string = Format_Stock_Symbol_String(string)
        Action = "INSERT INTO " + Table + " (sym) VALUES ('" + string + "');"
        try:
            cursor.execute(Action)
            Database.commit()
            count = count + 1
        except:
            Database.rollback()
            
        
    Infile.close()
    print count, " records updated in table ", Table

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


#Connect to the database server
db = MySQLdb.connect(args.host, args.username, args.password, args.database)
c=db.cursor()

#Get all the available stock symbols
c.execute ("select sym from ticker")
action = db.cursor()
results = c.fetchall()

i = 0
for string in results:

    if i >= (args.start * len(results) // 100) and i <= (args.end * len(results) // 100):
        print "Working on ", string[0]
        #get current time for database entry
        now = datetime.datetime.now()

        #get time for performance
        t1 = time.time()

        #build the URL, download the html file, and generate the soup
        url = Generate_Stock_URL(string[0])
        html = Get_Page(url)
        Soup = BeautifulSoup(html)


        #Get key data
        try:
            price = Get_Price(string[0])
            cap = Get_Data("Total Common Shares Outstanding\n", "balannualdiv", Soup) * price
            reteq = Compute_Return_On_Capital(Soup)
            earnyield = Compute_Earnings_Yield(Soup, price)
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

    

          









