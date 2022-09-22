import requests

ticker = input("Enter the Stock Ticker: ")
exp = input("Enter the expiration date in the format \"yyyy-mm-dd\": ")
strike = input("Enter a Strike Price: ")
cORp = input("Call or Put? ").upper()

# With Exp Date
resp = requests.get('https://eodhistoricaldata.com/api/options/AAPL.US?api_token=OeAFFmMliFG5orCUuwAKQ8l4WWFQ67YX&from=%s&to=%s' % (exp, exp))

if resp.status_code != 200:
    # This means something went wrong.
    print('GET /tasks/ {}'.format(resp.status_code))

code = resp.json()['code']
data = resp.json()['data'][0]
options = data.get('options').get(cORp)
exp = data.get('expirationDate')

# Contains info in the following format:
# [Bid, Ask, Implied Vol, Delta, Gamma, Theta, Vega, Rho, Time Value]
importantData = {}

for contract in options:
    if contract.get('strike') == int(strike):
        importantData['Bid'] = contract.get('bid')
        importantData['Ask'] = contract.get('ask')
        importantData['Implied Volatility'] = contract.get('impliedVolatility')
        importantData['Delta'] = contract.get('delta')
        importantData['Gamma'] = contract.get('gamma')
        importantData['Theta'] = contract.get('theta')
        importantData['Vega'] = contract.get('vega')
        importantData['Rho'] = contract.get('rho')
        importantData['Time Value'] = contract.get('timeValue')
        break

if importantData == {}:
    print("There was an error retrieving the data.")
else:
    print("\n\n----------------\n\n\nShowing Data For: \n%s | %s\nExp: %s\n" % (ticker, strike, exp))
    for key, value in importantData.items():
        print("{}: {}".format(key, value))