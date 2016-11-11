from django.shortcuts import render
from django.http import HttpResponse
import datetime
import urllib2, sys, time, os, re
import sqlite3
import os.path

from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

# Database
# 1. total_performance.dat (Total performance so far)
# 2. total_history.dat (history : Date / Company Name / TOP-BOTTOM / Entry Price / Next day closed price / Profit)
# 3. current_trading.dat (Current Holding stocks) : Company name / How many / LONG / Get-in price


#################################################################################
# Sleipnir: Common Functions
#################################################################################

# Display Home page
def sleipnir_main(request):
    #html = "<HTML>HELLO, HERO</HTML>"
    return render_to_response('sleipnir/sleipnir_index.html')



# Get the total fund (How much I do have)
def check_total_perf():
    if os.path.exists('sleipnir/total_perf.dat'):
        # if exist
        with open('sleipnir/total_perf.dat') as f:
            line = f.readlines()
            data_content = line[0]
    else:
        total_perf = open('sleipnir/total_perf.dat', 'w+')
        total_perf.write('200000.00')
        total_perf.close()
        data_content = '2000000.00'
    return data_content



# Return the list holding stocks
def open_holding_stocks():

    company_list = []
    if os.path.exists('sleipnir/holding_stock.dat'):
        with open('sleipnir/holding_stock.dat') as fp:
            for line in fp:
                if line == '' or line == '\n':
                    pass
                else:
                    company_list.append(line)
        return company_list
    else:
        return company_list


def add_new_stock(stock_info):

    new_stock = open('sleipnir/holding_stock.dat', 'a+')
    new_stock.write(stock_info)
    new_stock.write('\n')
    new_stock.close()
    return
       

def renew_holding_stock(stock_list):

    new_stock = open('sleipnir/holding_stock.dat', 'w')
    for item in stock_list:
        new_stock.write(item)
    new_stock.close()
    return



# Update total fund
def renew_total_perf(fund):
    fund = round(fund,2)
    renewal = open('sleipnir/total_perf.dat', 'w+')
    renewal.write(str(fund))
    return 


# You know ...
def sleipnir_get_stock_price_only(company_name):
    # Get Google Finance API
    url = "http://finance.google.com/finance/info?client=ig&q="
    url = url + company_name
    match = urllib2.urlopen(url).read()
    price = sleipnir_grab_price_only(match)
    return float(price)


# You know ...
def sleipnir_grab_price_only(match):
    price = ''
    price_element = match.split(',')
    for xx in range (0, len(price_element)):
        if '"l" :' in price_element[xx]: # Include price info
            price = price_element[xx].split(':')[1]
            price = price.replace('"', '')
            price = price.replace(' ', '')

    return price



#################################################################################
# Sleipnir: Current Holding Function
#################################################################################


def sleipnir_holding_status(request):
    company_list = []
    total_perf = []

    # Get the holding company list
    company_list = open_holding_stocks()

    html = ''
    if company_list:
        html = html + '<!DOCTYPE html> <html> <head> <style> table {     border-collapse: collapse;     width: 70%;  } th, td {    text-align: left;'
        html = html + '    padding: 8px; } tr:nth-child(even){background-color: #f2f2f2} th   {  background-color: #4CAF50;    color: white;  } '
        html = html + ' </style> </head> <body> <h2>Current Holding Status </h2> <table>   <tr>    <th>Company</th>    <th>Amount</th> '
        html = html + '<th>Long or Short</th> <th> Get-in Price </th> <th> Current Price </th> <th> Performance </th>   </tr>'

        for item in company_list:
            current_list = item.split(',')
            html = html + '<tr>    <td>' + current_list[0] + '</td> <td>' + current_list[1] + '</td> <td>' + current_list[2] + '</td> <td>' + current_list[3] + '</td> <td>' 
            company_price = sleipnir_get_stock_price_only(current_list[0])
            html = html + str(company_price) + ' </td> <td> '
            getin_perf = float(current_list[1]) * float(current_list[3])
            current_perf = company_price * float(current_list[1])
            final_perf = current_perf - getin_perf
            total_perf.append(str(final_perf))
            html = html + str(final_perf) + '</td> </tr>'

        html = html + '</table>'
        perf_sum = 0.00
        for x in total_perf:
            perf_sum = perf_sum + float(x)
        html = html + '<br><br> Total Performance : ' + str(perf_sum) + ' <br><br> <a href=/sleipnir_main/ style="text-decoration:none"> Back to main page </a></body> </html>'
    else:
        html = "You don't hold any stock"

    return HttpResponse(html)



#################################################################################
# Sleipnir: New Trade (Buy / Sell Short)
#################################################################################
#
# A user can buy or hold up to 5 companies
#


# Display New Trade HTML (Asking 5 companies to a user)
def sleipnir_new_trade(request):

    html = ''
    total_perf = []
    # Get the holding company list
    company_list = open_holding_stocks()
    holding_number = len(company_list)
    available_stock_number = 5 - holding_number
    radio_button = 1

    html = html + '<!DOCTYPE html> <html> <head> <style> table {     border-collapse: collapse;     width: 70%;  } th, td {    text-align: left;'
    html = html + '    padding: 8px; } tr:nth-child(even){background-color: #f2f2f2} th   {  background-color: #0ad1cd;    color: white;  } '
    html = html + ' </style> </head> <body> <h2>Purchase & Holding Stock Information </h2>'
    html = html + '<form action="/sleipnir_purchase/" method="get">'
    
    if company_list:
        html = html + '<table>   <tr>    <th>Company</th>    <th>Amount</th> '
        html = html + '<th>Long or Short</th> <th> Get-in Price </th> <th> Current Price </th> <th> Performance </th>  </tr> '

        for item in company_list:
            current_list = item.split(',')
            html = html + '<tr>    <td>' + current_list[0] + '</td> <td>' + current_list[1] + '</td> <td>' + current_list[2] + '</td> <td>' + current_list[3] + '</td> <td>' 
            company_price = sleipnir_get_stock_price_only(current_list[0])
            html = html + str(company_price) + ' </td> <td> '
            getin_perf = float(current_list[1]) * float(current_list[3])
            current_perf = company_price * float(current_list[1])
            final_perf = current_perf - getin_perf
            total_perf.append(str(final_perf))
            html = html + str(final_perf) + '</td> </tr>'

        html = html + '</table>'
        perf_sum = 0.00
        for x in total_perf:
            perf_sum = perf_sum + float(x)
        html = html + '<br><br> Total Performance : ' + str(perf_sum) + ' <br><br>'

    if holding_number == 5:
        html = html + 'Warning:: You already have 5 stocks holding. You can\'t buy more until you sell something. <br>'
        html = html + 'This app is designed to buy/sell short up to only 5 stocks. <br><br>'
    else:
        html = html + '<form action="/sleipnir_purchase/" method="get">'
        html = html + '<table>   <tr>    <th>Company</th>    <th> Name </th> <th>Long or Short</th> <th> </th> <th> </th>'
        for x in range(0, available_stock_number):
            html = html + '<tr>  <td> Enter name:</td>   <td> <input type="text" name="com' + str(radio_button) + '"> </td> <td>Long or Short?</td>'
            html = html + ' <td> <input type="radio" name="long' + str(radio_button) + '" value="long" checked="yes"/> Long </td>'
            html = html + ' <td> <input type="radio" name="long' + str(radio_button) + '" value="short"> Short </td> </tr>'
            radio_button = radio_button + 1
        html = html + '<input type="hidden" value="' + str(available_stock_number) + '" name="stock_number" />'
        html = html + '</table> <br><br><input type="submit" value="Submit the list"><br><br>'
        
        html = html + ' <a href=/sleipnir_main/ style="text-decoration:none"> Back to main page </a></body> </html>'


    return HttpResponse(html)



# Received 5 company list & pass it to result page
def sleipnir_purchase(request):

    pur_1 = request.GET.getlist('stock_number')
    purchase_number = pur_1[0]
    com_list = []
    long_list = []
    html = ''
    remain_fund = 0.00
    
    for x in range(1, int(purchase_number)+1):
        get_value1 = request.GET['com' + str(x)]
        get_value2 = request.GET['long' + str(x)]
        if get_value1 == '':
            pass
        else:
            com_list.append(get_value1)
            long_list.append(get_value2)
            html = html + get_value1 + "<br>"
            html = html + get_value2 + "<br>"

    # Get remain funds
    total_fund = check_total_perf()
    each_fund = float(total_fund) / int(purchase_number)
    remain_fund = float(total_fund) - (each_fund * int(purchase_number))
    remain_fund = remain_fund + ((int(purchase_number)-len(com_list))*each_fund)

    for item in range(0, len(com_list)):
        if long_list[item] == 'long':
            return_fund = buy_stock(com_list[item], each_fund)
            remain_fund = remain_fund + return_fund
        elif long_list[item] == 'short':
            return_fund = sellshort_stock(com_list[item], each_fund)
            remain_fund = remain_fund + return_fund

    renew_total_perf(remain_fund)
    html = "purchase is done. Go back to main page and check your current holding status. <br><br>"
    html = html + ' <a href=/sleipnir_main/ style="text-decoration:none"> Back to main page </a>'

    return HttpResponse(html)


# Buy: stock
def buy_stock(com1, fund):
    current_price = sleipnir_get_stock_price_only(com1)
    remain_fund = 0.00

    if current_price > fund:
        return fund
    else:
        purchase_amount = float(fund) / float(current_price)
        remain_fund = fund - (int(purchase_amount) * float(current_price))
        remain_fund = round(remain_fund,2)
        new_stock = com1 + ', ' + str(int(purchase_amount)) + ', LONG, ' + str(current_price)
        add_new_stock(new_stock)
        return remain_fund


# SellShort: stock
def sellshort_stock(com1, fund):
    current_price = sleipnir_get_stock_price_only(com1)
    remain_fund = 0.00

    if current_price > fund:
        return fund
    else:
        purchase_amount = float(fund) / float(current_price)
        remain_fund = fund - (int(purchase_amount) * float(current_price))
        remain_fund = round(remain_fund,2)
        new_stock = com1 + ', ' + str(int(purchase_amount)) + ', SHORT, ' + str(current_price)
        add_new_stock(new_stock)
        return remain_fund




#################################################################################
# Sleipnir: Sell your holding
#################################################################################


def sleipnir_sell(request):
    company_list = open_holding_stocks()
    html = ''
    item_number = 0

    html = html + '<!DOCTYPE html> <html> <head> <style> table {     border-collapse: collapse;     width: 70%;  } th, td {    text-align: left;'
    html = html + '    padding: 8px; } tr:nth-child(even){background-color: #f2f2f2} th   {  background-color: #4c58af;    color: white;  } '
    html = html + ' </style> </head> <body> <h2>Current Holding Status </h2>'
    html = html + '<form action="/sleipnir_sold/" method="get">'
    if company_list:
        
        html = html + '<table>   <tr>    <th>Company</th>    <th>Amount</th> '
        html = html + '<th>Long or Short</th> <th> Get-in Price </th> <th> Current Price </th> <th> Performance </th> <th> Sell? </th>  </tr> '

        for item in company_list:
            current_list = item.split(',')
            html = html + '<tr>    <td>' + current_list[0] + '</td> <td>' + current_list[1] + '</td> <td>' + current_list[2] + '</td> <td>' + current_list[3] + '</td> <td>' 
            company_price = sleipnir_get_stock_price_only(current_list[0])
            html = html + str(company_price) + ' </td> <td> '
            getin_perf = float(current_list[1]) * float(current_list[3])
            current_perf = company_price * float(current_list[1])
            final_perf = current_perf - getin_perf
            html = html + str(final_perf) + '</td> <td>'

            html = html + '<input type=\'checkbox\' name=\'controller\' value=\'' + current_list[0] + ':' + str(item_number) + '\'>' + ' </td>  </tr>'
            item_number = item_number + 1

        html = html + '</table> <br><br> <input type="submit" value="Submit">  </form>'
        html = html + '<br><br> <a href=/sleipnir_main/ style="text-decoration:none"> Back to main page </a></body> </html>'
    else:
        html = "You don't hold any stock"


    return HttpResponse(html)




# Purchasing function


def sleipnir_sold(request):
    html = ''
    sell_stocks = request.GET.getlist('controller')
    company_list = open_holding_stocks()
    sell_list = []

    # Get sell stock's number
    for item in sell_stocks:
        new_number = item.split(':')
        sell_list.append(new_number[1])

    html = html + '<!DOCTYPE html> <html> <head> <style> table {     border-collapse: collapse;     width: 70%;  } th, td {    text-align: left;'
    html = html + '    padding: 8px; } tr:nth-child(even){background-color: #f2f2f2} th   {  background-color: #3179c6;    color: white;  } '
    html = html + ' </style> </head> <body> <h2>Stocks you will sell </h2>'
    html = html + '<table>   <tr>    <th>Company</th>    <th>Amount</th> '
    html = html + '<th>Long or Short</th> <th> Get-in Price </th> <th> Current Price </th> <th> Performance </th> </tr> '

    for item in sell_list:
        current_list = company_list[int(item)].split(',')
        html = html + '<tr>    <td>' + current_list[0] + '</td> <td>' + current_list[1] + '</td> <td>' + current_list[2] + '</td> <td>' + current_list[3] + '</td> <td>' 
        company_price = sleipnir_get_stock_price_only(current_list[0])
        html = html + str(company_price) + ' </td> <td> '
        getin_perf = float(current_list[1]) * float(current_list[3])
        current_perf = company_price * float(current_list[1])
        final_perf = current_perf - getin_perf
        html = html + str(final_perf) + '</td> </tr>'

    html = html + '</table> <br><br><br><br><br>'

    # Calculate total fund
    remain_fund = float(check_total_perf())
    for num in sell_list:
        current_list = company_list[int(num)].split(',')
        if 'LONG' in current_list[2]:
            remain_fund = remain_fund + float(sell_stock(current_list[0], int(current_list[1])))
        elif 'SHORT' in current_list[2]:
            html = html + "company name = " + current_list[0] + " amount is : " + current_list[1] + " getin price is : " + current_list[3] + "<br><br>"
            remain_fund = remain_fund + float(buytocover_stock(current_list[0], int(current_list[1]), float(current_list[3])))
            html = html + "remain fund of sellshort: " + str(float(buytocover_stock(current_list[0], int(current_list[1]), float(current_list[3]))))
        else:
            remain_fund = 10.00
            html = html + ":" + current_list[2] + ":<br>"

    renew_total_perf(float(remain_fund))


    # Remove sell_stocks
    renew_stock = []
    for num in range(0, len(company_list)):
        if str(num) in sell_list:
            pass
        else:
            renew_stock.append(company_list[int(num)])
    renew_holding_stock(renew_stock)

    company_list = open_holding_stocks()

    # Print out Sell stock & remain stock
    html = html + '<h2>Remain Stocks </h2>'
    if company_list:
        
        html = html + '<table>   <tr>    <th>Company</th>    <th>Amount</th> '
        html = html + '<th>Long or Short</th> <th> Get-in Price </th> <th> Current Price </th> <th> Performance </th> </tr> '

        for item in company_list:
            current_list = item.split(',')
            html = html + '<tr>    <td>' + current_list[0] + '</td> <td>' + current_list[1] + '</td> <td>' + current_list[2] + '</td> <td>' + current_list[3] + '</td> <td>' 
            company_price = sleipnir_get_stock_price_only(current_list[0])
            html = html + str(company_price) + ' </td> <td> '
            getin_perf = float(current_list[1]) * float(current_list[3])
            current_perf = company_price * float(current_list[1])
            final_perf = current_perf - getin_perf
            html = html + str(final_perf) + '</td> </tr>'
        html = html + '</table>'

    html = html + '<br><br> <a href=/sleipnir_main/ style="text-decoration:none"> Back to main page </a></body> </html>'

    return HttpResponse(html)


# Sell: stock
def sell_stock(com1, amount):
    current_price = sleipnir_get_stock_price_only(com1)
    remain_fund = 0.00

    remain_fund = (current_price * amount)
    remain_fund = round(remain_fund,2)

    return remain_fund


# BuytoCover: stock
def buytocover_stock(com1, amount, getin_price):
    current_price = sleipnir_get_stock_price_only(com1)
    remain_fund = 0.00
    profit = 0.00

    profit = (float(getin_price)*int(amount)) - (float(current_price) * int(amount))
    original_fund = float(getin_price)*int(amount)
    remain_fund = original_fund + profit
    remain_fund = round(remain_fund,2)
    return remain_fund


#################################################################################
# Sleipnir: Practice function
#################################################################################


def sleipnir_test_function(request):
    company_name = 'AAPL'

    # Grab HTML
    url = "http://finance.google.com/finance/info?client=ig&q="
    url = url + company_name
    match = urllib2.urlopen(url).read()
    price = sleipnir_grab_price_only(match)

    html = "<html><body><br>"
    html = html + "HERO: APPLE stock price is %s" % str(price)
    #html = html + "<br><br>bebe<br>" + url
    return HttpResponse(html)


def sleipnir_grab_price_only(match):
    price = ''
    price_element = match.split(',')
    for xx in range (0, len(price_element)):
        if '"l" :' in price_element[xx]: # Include price info
            price = price_element[xx].split(':')[1]
            price = price.replace('"', '')
            price = price.replace(' ', '')

    return price



#################################################################################
# Sleipnir: Not sure functions
#################################################################################


def sleipnir_total_perf(request):

    if os.path.exists('sleipnir/total_perf.dat'):
        with open('sleipnir/total_perf.dat', 'r') as f:
            read_data = f.read()
            html = 'Your total performance is ' + str(read_data)
    else:
        fund_data = check_total_perf()
        html = 'Your total performance is ' + str(fund_data)

    return HttpResponse(html)        




# Create your views here.
