# Author: Dash Vallance
# Adapted from example code provided by Sunil Lal

# This is a simple HTTP server which listens on port 8080, accepts connection request, and processes the client request
# in sepearte threads. It implements basic service functions (methods) which generate HTTP response to service the HTTP requests.
# Currently there are 3 service functions; default, welcome and getFile. The process function maps the requet URL pattern to the service function.
# When the requested resource in the URL is empty, the default function is called which currently invokes the welcome function.
# The welcome service function responds with a simple HTTP response: "Welcome to my homepage".
# The getFile service function fetches the requested html or img file and generates an HTTP response containing the file contents and appropriate headers.

# To extend this server's functionality, define your service function(s), and map it to suitable URL pattern in the process function.

# This web server runs on python v3
# Usage: execute this program, open your browser (preferably chrome) and type http://servername:8080
# e.g. if server.py and broswer are running on the same machine, then use http://localhost:8080

# List of bugs I don't have time to understand/fix:
# 'Reset' fails to clear the most recently added item, because the POST message
# which appended it is resent on the refresh (issue with /updatePortfolio, likely not using the correct
# HTTP status in some way)
import sys
from socket import *
import os
import _thread
import requests  # apparently pycurl struggles with heroku? It looked so fast too!
import json
import math
import base64
from decimal import *


# Extract the given header value from the HTTP request message
def getHeader(message, header):
    if message.find(header) > -1:
        value = message.split(header)[1].split()[0]
    else:
        value = None

    return value


# service function to fetch the requested file, and send the contents back to the client in a HTTP response.
def getFile(filename):
    try:
        # open and read the file contents. This becomes the body of the HTTP response
        f = open(filename, "rb")

        body = f.read()
        f.close()

        header = ("HTTP/1.1 200 OK\r\n\r\n").encode()
    except IOError:
        # Send HTTP response message for resource not found
        header = "HTTP/1.1 404 Not Found\r\n\r\n".encode()
        body = "<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode()

    return header, body


# service function for requests which error out, to fetch a page body
def getFileNoHeader(filename):
    try:
        # open and read the file contents. This becomes the body of the HTTP response
        f = open(filename, "rb")

        body = f.read()
        f.close()

    except IOError:

        # Send HTTP response message for resource not found
        header = "HTTP/1.1 404 Not Found\r\n\r\n".encode()
        body = "<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode()
        return header, body

    return body


# service function to generate HTTP response with a simple welcome message
def welcome(message):
    header = "HTTP/1.1 200 OK\r\n\r\n".encode()
    body = "<html><head></head><body><h1>Welcome to my homepage</h1></body></html>\r\n".encode()

    return header, body


def portfolio(message):
    with open('stockportfolio.html', 'rb') as f:
        body = f.read()

    header = 'HTTP/1.1 200 OK\r\n\r\n'.encode()

    return header, body


# To avoid constantly downloading and parsing the massive stock symbol list for validation,
# lets build a local copy. In the real world, we could have a script refresh this as often as required.
# Instead, I'm just going to comment/uncomment a call to this function
def buildValidSymbolFile():
    validSymbols = []
    try:
        response = requests.get(
            'https://cloud.iexapis.com/stable/ref-data/symbols?token=pk_2502efcdd63f4ac1aa76ecf413ea4e65 ')
        response.raise_for_status()
        asJson = response.json()
        for values in asJson:
            if values['type'] == 'cs':
                validSymbols.append(values['symbol'])

        with open('valid_symbols.json', 'w') as f:
            json.dump(validSymbols, f)

    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')


def validateSymbol(givenSymbol):
    with open('valid_symbols.json', 'r') as f:
        toValidate = json.load(f)

    if givenSymbol in toValidate:
        return True

    return False


# Error: price must be positive and reasonable, and we only want prices with > 2 decimal places
def validatePrice(price):
    p = float(price)
    num_decimals = round(p - math.floor(p), 6)  # round to correct floating point math
    maxStockPrice = 316248.31  # value of the most expensive stock in the world, USD
    if p < 0 or p > maxStockPrice or num_decimals > 2:
        return False
    return True


def isInteger(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def resetJSON():
    with open('portfolio.json', 'w') as f:
        f.write('')

    header, body = getFile('stockportfolio.html')
    header = 'HTTP/1.1 226 IM Used'.encode()
    return header, body

def shortUpdate(updateData):
    # parse out the header
    updateData = updateData.split('\r\n\r\n')
    body = updateData[1].split('&')

    # parse the form data into a 2d array; structure = [0] : symbol; [1] : quantity; [2] : price
    # ie. [0][x] returns a key, eg. [0][0] = symbol; while [x][1] returns the value. eg. [0][1] may be AAPL
    upArray = []
    for v in body:
        upArray.append(v.split('='))

    # ensure the stock given as updateData is valid
    if not validateSymbol(upArray[0][1]):
        header = 'HTTP/1.1 400 Bad Request\r\n\r\n'.encode()
        body = getFileNoHeader('stockportfolio.html')
        return header, body

    # Error: quantity must be a positive integer within reasonable bounds
    if not isInteger(upArray[1][1]) or int(upArray[1][1]) < 0 \
            or int(upArray[1][1]) > 1000000:
        header = 'HTTP/1.1 400 Bad Request\r\n\r\n'.encode()
        body = getFileNoHeader('stockportfolio.html')
        return header, body

    if not validatePrice(upArray[2][1]):
        header = 'HTTP/1.1 400 Bad Request\r\n\r\n'.encode()
        body = getFileNoHeader('stockportfolio.html')
        return header, body

        # Create entry
    portfolio_stocks = [{
        upArray[0][0]: upArray[0][1],
        upArray[1][0]: upArray[1][1],
        'purchasePrice': upArray[2][1] # to correct form, which calls this 'price'
    }]

    with open('portfolio.json', 'w') as f:
        json.dump({'portfolio': portfolio_stocks}, f)

    return getFile('stockportfolio.html')


def updatePortfolio(update):
    # check if there are any existing entries
    try:
        bool = os.stat('portfolio.json').st_size != 0
    except OSError as err:
        print("OS error: {0}".format(err))
        return shortUpdate(update)

    if not bool:
        return shortUpdate(update)

    # download the current portfolio as a dict
    with open('portfolio.json', 'r+') as f:
        data = json.load(f)

    # parse out the header
    updateData = update.split('\r\n\r\n')
    if updateData[1] == '':
        return getFile('stockportfolio.html')
        # header, body = pageError()
        # return header, body


    body = updateData[1].split('&')

    # parse the form data into a 2d array; structure = [0] : symbol; [1] : quantity; [2] : price
    # ie. [0][x] returns a key, eg. [0][0] = symbol; while [x][1] returns the value. eg. [0][1] may be AAPL
    upArray = []
    for v in body:
        upArray.append(v.split('='))

    # ensure the stock given as updateData is valid
    if not validateSymbol(upArray[0][1]):
        header = 'HTTP/1.1 400 Bad Request\r\n\r\n'.encode()
        body = getFileNoHeader('stockportfolio.html')
        return header, body

    # lookup stock in portfolio
    existing = -1
    portfolio_stocks = data['portfolio']

    for values in portfolio_stocks:
        if upArray[0][1] in values['symbol']:
            existing = values

    if existing == -1:  # append new stock to portfolio
        # Error: quantity must be a positive integer within reasonable bounds
        if not isInteger(upArray[1][1]) or int(upArray[1][1]) < 0 \
                or int(upArray[1][1]) > 1000000:
            header = 'HTTP/1.1 400 Bad Request\r\n\r\n'.encode()
            body = getFileNoHeader('stockportfolio.html')
            return header, body

        if not validatePrice(upArray[2][1]):
            header = 'HTTP/1.1 400 Bad Request\r\n\r\n'.encode()
            body = getFileNoHeader('stockportfolio.html')
            return header, body

        # Create entry
        portfolio_stocks.append({
            upArray[0][0]: upArray[0][1],
            upArray[1][0]: upArray[1][1],
            'purchasePrice': upArray[2][1] # to correct form, which calls this 'price'
        })

        # Reorganise and then store the portfolio
        sorted_portfolio = sorted(portfolio_stocks, key=lambda k: k['symbol'])
        print(sorted_portfolio)
        with open('portfolio.json', 'w') as f:
            json.dump({'portfolio': sorted_portfolio}, f)

        header = "HTTP/1.1 200 OK".encode()

    else:  # amend existing stock in portfolio
        # Error: quantity must be an integer, within reasonable bounds
        if not isInteger(upArray[1][1]) or \
                int(upArray[1][1]) > 1000000:
            header = 'HTTP/1.1 400 Bad Request\r\n\r\n'.encode()
            body = getFileNoHeader('stockportfolio.html')
            return header, body

        if not validatePrice(float(upArray[2][1])):
            header = 'HTTP/1.1 400 Bad Request\r\n\r\n'.encode()
            body = getFileNoHeader('stockportfolio.html')
            return header, body

        # To keep stock removal easy: if users enter a negative number greater than the number of stocks
        # they own, we'll pretend they entered exactly the quantity which they own
        if int(upArray[1][1]) < 0 and abs(int(upArray[1][1])) > int(existing['quantity']):
            upArray[1][1] = -int((existing['quantity']))

        # calculate the new quantity and price
        total_val_of_existing = int(existing['quantity']) * float(existing['purchasePrice'])
        total_val_of_update = int(upArray[1][1]) * float(upArray[2][1])
        total_val = total_val_of_existing + total_val_of_update

        total_quantity = int(existing['quantity']) + int(upArray[1][1])

        if total_quantity == 0:
            price_per_unit = total_val
        else:
            price_per_unit = float(round(Decimal(total_val / total_quantity), 2))

        # update
        existing['quantity'] = total_quantity
        existing['purchasePrice'] = price_per_unit

        # Reorganise and then store the portfolio
        sorted_data = sorted(data['portfolio'], key=lambda k: k['symbol'])
        with open('portfolio.json', 'w') as f:
            json.dump({'portfolio': sorted_data}, f)

        header = 'HTTP/1.1 200 OK'.encode()

    return getFile('stockportfolio.html')

    # return portfolio('')


# default service function
def default(message):
    header, body = welcome(message)

    return header, body

def authenticate(message):
    text = message.split('\r\n')

    username = '14297367'
    password = '14297367'
    encoded = base64.b64encode((username + ':' + password).encode('utf-8')).decode('utf-8')

    for v in text:
        if ':' in v:
            varr = v.split(': ')
            if varr[0] == 'Authorization':
                if varr[1] == 'Basic '+encoded:
                    return True

    return False

# We process client request here. The requested resource in the URL is mapped to a service function which generates the HTTP response
# that is eventually returned to the client.
def process(connectionSocket):
    # buildValidSymbolFile()
    # Receives the request message from the client
    message = connectionSocket.recv(1024).decode()

    if len(message) > 1:
        # Validate authorization
        if not authenticate(message):
            # Send the HTTP response header line to the connection socket
            connectionSocket.send('HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic realm="User Visible Realm"\r\n\r\n'.encode())
            # Send the content of the HTTP body (e.g. requested file) to the connection socket
            connectionSocket.send(''.encode())
            # Close the client connection socket


        # Extract the path of the requested object from the message
        # Because the extracted path of the HTTP request includes
        # a character '/', we read the path from the second character
        resource = message.split()[1][1:]

        # map requested resource (contained in the URL) to specific function which generates HTTP response
        if resource == "":
            responseHeader, responseBody = default(message)
        elif resource == "reset":
            responseHeader, responseBody = resetJSON()
        elif resource == "updatePortfolio":
            responseHeader, responseBody = updatePortfolio(message)
        elif resource == "chart":
            responseHeader, responseBody = getFile('stockchart.html')
        elif resource == "portfolio":
            responseHeader, responseBody = getFile('stockportfolio.html')
        elif resource == "welcome":
            responseHeader, responseBody = welcome(message)
        else:
            responseHeader, responseBody = getFile(resource)

    # Append the basic authentication header
    # responseHeader = responseHeader.decode().rstrip('\r\n\r\n')
    # responseHeader += '\r\nWWW-Authenticate: Basic realm="User Visible Realm", charset="UTF-8"\r\n\r\n'
    # responseHeader = responseHeader.encode()

    # Send the HTTP response header line to the connection socket
    connectionSocket.send(responseHeader)
    # Send the content of the HTTP body (e.g. requested file) to the connection socket
    connectionSocket.send(responseBody)
    # Close the client connection socket
    connectionSocket.close()

def main(argv):
    print(argv)
    # not very safe arg-parsing
    if not isInteger(argv):
        print("Please give a valid port (0-65535)")
        exit()
    if int(argv) < 0 or int(argv) > 65535:
        print("Please give a valid port (0-65535)")
        exit()

    serverSocket = socket(AF_INET, SOCK_STREAM)

    serverPort = int(argv)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serverSocket.bind(("", serverPort))

    serverSocket.listen(5)
    print('The server is running')
    # Main web server loop. It simply accepts TCP connections, and gets the requests processed in separate threads.
    while True:
        try:
        # Set up a new connection from the client
            connectionSocket, addr = serverSocket.accept()
        # Clients timeout after 60 seconds of inactivity and must reconnect.
            connectionSocket.settimeout(60)
        # start new thread to handle incoming request
            _thread.start_new_thread(process, (connectionSocket,))
        except KeyboardInterrupt:
            exit()


if __name__ == '__main__':
     main(sys.argv[1])

#print(message)
#sys.stdout.flush()
