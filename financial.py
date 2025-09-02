try: 
    import yfinance
except Exception:
    yfinance = None
try: 
    from pycoingecko import CoinGeckoAPI
except Exception:
    CoinGeckoAPI = None
try:
    import requests
except Exception:
    requests = None





## TODO: | cash and items implementation | 
# TODO: gold and silver prices non API?
## TODO: long term storage, 



 

# static setting of current holdings
Stocks = {"AMZN": 1.0}
crypto = {"pi-network": 1700.0}
bullion = {"gold": 1.1, "silver": 16.0}
cash = {"cash": 0}
items = {"bicycle": 1000.0, "4090 Gigabyte": 2000.0}





# STOCK PRICE
# gets price using the ticker symbol 
def getPrice(ticker: str) -> float | None: 
    if yfinance is None: 
        return None
    try: 
        tick = yfinance.Ticker(ticker)
        historyPrice = tick.history(period="1d")
        if not historyPrice.empty:
            return float(historyPrice["Close"].iloc[-1])
        if hasattr(tick, 'fast_info') and "last_price" in tick.fast_info:
            return float(tick.fast_info["last_price"])
        information = tick.info
        if "regularMarketPrice" in information:
            return float(information["regularMarketPrice"])
    except Exception as e:
        print(f"Error retrieving the price for {ticker}: {e}")
    return None





# DEBT TRACKER
def debtTracker():
    debt = {"Apple Card": 2144.00, "Venture One": 2501.00}
    while True: 
        print("\nDebt Tracker")
        print(" 1. View Debt\n 2. Add Debt\n 3. Subtract Debt\n 4. Remove Debt Account\n 5. Exit")
        debtInput = input("Input a value ").strip()
        if debtInput == "1":
            if not debt:
                print("No debt(s) recorded")
            else: 
                print("\nCurrent Debts")
                for name, amount in debt.items():
                    print(f"{name}: ${amount:.2f}")
                    continue
            continue
        elif debtInput == "2":
            if debt:
                print("Selectable debt account(s)")
                for name in debt.keys():
                    print(f"Current Selectable Choices for Debt Accounts: \n{name}")
            print("Type [quit] to return to the main menu")
            debtSelect = input("Enter the name of a debt account: ")
            AccountMatch = next((match for match in debt if match.lower() == debtSelect.lower()), None)
            if debtSelect == "quit":
                continue
            if not AccountMatch:
                while True: 
                    print(f"Account [{debtSelect}] not found, would you like to add the account?")
                    yorn = input("Enter y or n: ").strip().lower()
                    if yorn in ("y"):
                        AccountMatch = debtSelect
                        debt[AccountMatch] = 0.0
                        print(f"Created Account {AccountMatch},  Successfully!")
                        break
                    elif yorn in ("n"):
                        print("The account will not be added.")
                        break
                    else: 
                        print("please enter a valid y or n")
            if not AccountMatch:
                continue
            try: 
                print("Remember, the banks do not mind the monthly payment")
                print("Suggestion to sign on for payment plans you can afford")
                print("Try not to leave unpaid balances at months end")
                debtAddition = float(input("Enter a number to add to the debt: ").strip())  
            except ValueError: 
                print("Invalid input, try again.")    
                continue
            debt[AccountMatch] = debt.get(AccountMatch, 0.0) + max(0.0, debtAddition)
            print(f"Debt and account added: {AccountMatch}: ${debt[AccountMatch]:,.2f}")
            #print(f"{AccountMatch}: {debt[AccountMatch]:.2f}")
        elif debtInput == "3":
             if not debt: 
                 print("No debt accounts found")
                 continue
             print("Current Debt Accounts:")
             for name in debt.keys():
                 print(f"{name}")
             removeAmount = input("Enter the account name to subtract debt from ").strip()
             match = next((matches for matches in debt if matches.lower() == removeAmount.lower()), None)
             if not match:
                print("Account Not Found")
                continue
             try: 
                 amount = float(input("Enter an amount to subtract as an whole number with up to two decimal places "))
             except ValueError:
                 print("Invalid Number, please enter something valid")
                 continue
             oldBalance = debt[match]
             debt[match] = max(0.0, oldBalance - max(0.0, amount))
             print(f"{match}: \nOld Balance ${oldBalance:,.2f} \nNew Balance ${debt[match]:,.2f}")
        elif debtInput == "4":
            name = input("Enter the name of the debt account to remove: ").strip()
            if name in debt: 
                del debt[name]
                print(f"Removed {name} from debts")
            else: 
                print("Account Not Found")
            continue
        elif debtInput == "5":
            break
        else: 
            print("Please enter a valid choice")
            continue

        



# STOCK
# takes the ticker symbol and and quantity and returns prices
def parse_positions(s= "AMZN: 1.0", section="totals", quiet=False) -> dict[str, float]:

    section = (section or "totals").strip().lower()
    show_stocks  = section in ("stocks", "stock", "a", "totals")    
    tickerANDAmounts = s.split(",")

    extraRemoved = [strippedParts.strip() for strippedParts in tickerANDAmounts]
    outputDictionary = {}
    for splitParts in extraRemoved: 
        ticker, quantity = splitParts.split(":", 1)
        outputDictionary[ticker] = float(quantity)
    subtotal = 0.0
    try:   
        if show_stocks: 
            for ticker, quantity in Stocks.items():
                #tickerInformation = yfinance.Ticker(ticker)
                tickerPrice = getPrice(ticker)
                if tickerPrice is None:
                    if not quiet:
                        print(f"Could not retrieve price for ticker: {ticker}")
                    continue
                TotalValue = tickerPrice * quantity
                subtotal += TotalValue
                
                if show_stocks: 
                    if section in ("stocks", "stock", "a", "totals"):
                        if not quiet:
                            print(f"{ticker}: {quantity} shares at ${tickerPrice:.2f} each, Total Value: ${TotalValue:.2f}")
                if section not in ("stocks", "stock", "a", "totals"):
                    print("Invalid Input")
    except Exception as e:
        if not quiet: 
            print(f"Error retrieving data for ticker:", e)
        
    return subtotal

def add_stock_to_positions():
    StockTicker = input("Enter stock ticker symbol, e.g. AAPL: ").strip().upper()
    if not StockTicker:
        print("Canceled")
        return
    try: 
        quantityStock = float(input("Enter number of shares to add: "))
    except ValueError:
        print("Invalid Number Entered")
        return
    Stocks[StockTicker] = Stocks.get(StockTicker, 0.0) + max(0.0, quantityStock)
    print(f"Updated [{StockTicker}], with {Stocks[StockTicker]} shares")




# CRYPTO PRICE
def showCrypto(section="totals", quiet=False) -> float:
        section = (section or "totals").strip().lower()
        show_crypto  = section in ("crypto", "cryptos", "b", "totals")  
        if not show_crypto:
            return 0.0
        if CoinGeckoAPI is None:
            if not quiet: 
                print("Crypto Prices are unavailable right now")
            return 0.0
        subtotal = 0.0
        coinGecko = CoinGeckoAPI()
        for cryptoName, quantityCrypto in crypto.items():
            try: 
                data = coinGecko.get_price(ids=[cryptoName], vs_currencies="usd")
                price = data[cryptoName]["usd"]
            except Exception:
                price = None
            if price is None:
                if not quiet: 
                    print(f"Could not fetch price for {cryptoName}")
                continue
            CryptoWorth = quantityCrypto * price
            subtotal += CryptoWorth
            if not quiet: 
                print(f"{cryptoName}: {quantityCrypto} at the current price ${price:.2f}, Total Value: ${CryptoWorth:.2f}")
        return subtotal

def add_crypto_to_positions():
    coinGeckoID = input("Enter CoinGecko ID, e.g. bitcoin: ").strip()
    if not coinGeckoID:
        print("canceled")
        return
    try: 
        quantityCrypto = float(input("Enter number of units to add: "))
    except ValueError:
        print("Invalid Number Entered")
        return
    crypto[coinGeckoID] = crypto.get(coinGeckoID, 0.0) + max(0.0, quantityCrypto)
    print(f"Updated [{coinGeckoID}], with {crypto[coinGeckoID]} shares")





#BULLION PRICE
def showBullion(section="totals", quiet=False) -> float:
    api_key = "5ebce4f9043996096c6855b1bee178a1"
    url = f"https://api.metalpriceapi.com/v1/latest?api_key={api_key}&base=USD&currencies=XAU,XAG"
    headers = {"x-access-token": api_key, "Content-Type": "application/json", "Accept": "application/json"}
    if requests is not None: 
        try: 
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            rates = (data or {}).get("rates") or {}
            xau = rates.get("XAU")
            xag = rates.get("XAG")
            gold_price = (1 / xau) if xau else None
            silver_price = (1 / xag) if xag else None
        except Exception as e:
            #print(f"Error fetching metal prices: {e}")
            gold_price = None
            silver_price = None
    else: 
        gold_price = None
        silver_price = None

    section = (section or "totals").strip().lower()
    show_bullion = section in ("bullion", "c", "totals")           
    
    if not show_bullion: 
        return 0.0
    subtotal = 0.0
    try: 
        goldPrice = float(gold_price) if gold_price is not None else None
        silverPrice = float(silver_price) if silver_price is not None else None
    except NameError:
        goldPrice = silverPrice = None
    goldOunce = bullion.get("gold", 0.0)
    silverOunce = bullion.get("silver", 0.0)
       
    if goldPrice is not None:
       # goldOunce = bullion.get("gold", 0.0)
        goldValue = goldOunce * goldPrice
        subtotal += goldValue
        if not quiet: 
            print(f"Gold : {goldOunce} at ${goldPrice:.2f}\n Total Gold Value: ${goldValue:.2f}")
    else: 
        if not quiet:
            print(f"Gold : {bullion.get('gold', 0.0)}oz @ N/A\n Total Gold Value N/A")
    if silverPrice is not None:
        #silverOunce = bullion.get("silver", 0.0)
        silverValue = silverOunce * silverPrice
        subtotal += silverValue
        if not quiet: 
            print(f"Silver : {silverOunce} at ${silverPrice:.2f}\n Total Gold Value: ${silverValue:.2f}")
    else:
        if not quiet:
            print(f"Silver : {bullion.get("silver", 0.0)} at N/A\n Total Gold Value: N/A")
    
    if goldPrice is None and silverPrice is None:
        if not quiet: 
            print("Bullion prices are unavailable right now...\n")
    return subtotal

def add_bullion_to_positions():
    bullionGoldORSilver = input("Enter metal [gold | silver]: ").strip().lower()
    if bullionGoldORSilver in ("au", "xau"): bullionGoldORSilver = "gold"
    if bullionGoldORSilver in ("ag", "xag"): bullionGoldORSilver = "silver"
    if bullionGoldORSilver not in ("gold", "silver"):
        print("Please enter either gold or silver...")
        return
    try: 
        metalOunce = float(input("Enter number of units to add: ").strip())
    except ValueError:
        print("Invalid Number Entered")
        return
    bullion[bullionGoldORSilver] = bullion.get(bullionGoldORSilver, 0.0) + max(0.0, metalOunce)
    print(f"Updated [{bullionGoldORSilver}], with {bullion[bullionGoldORSilver]} shares")




# MAIN MENU
def _main_menu_():
    while True: 
        print("\nWelcome to the asset and debt tracker!")
        print("1. positions")
        print("2. debt")
        print("3. exit")
        choice = input("Enter a choice of 1, 2 or 3: ")
        if choice == "1":
            while True: 
                print("\nPositions")
                print("  a) Stocks")
                print("  b) Crypto")
                print("  c) Bullion")
                print("  d) Totals")
                print("  e) Cash ")
                print("  f) Items")
                print("  g) Add/Update Position")
                print("  h) Exit")
                entry = input("Choose a/b/c/d/e/f/g or h: ").strip().lower()
                section = {"a": "stocks", "b": "crypto", "c": "bullion", "d": "totals", "h": "exit", "e": "cash", "f": "items", "g": "add"}
                
                if entry in ("h", "exit"):
                    break 

                if entry not in section:
                    print("Invalid Selection, please enter a different choice. ")
                    continue
                else: 
                    section = section[entry]

                if section in ("stocks", "stock", "a"):
                    parse_positions(section="stocks")
                elif section in ("crypto", "cryptos", "b"):
                    showCrypto(section="crypto")
                elif section in ("bullion", "c"):
                    showBullion(section="bullion")
                elif section in ("d", "totals"):
                    print("\n Totals:  ")
                    print("\n Stocks ")
                    parse_positions(section="stocks")
                    print("\n Crypto ")
                    showCrypto(section="crypto")
                    print("\n Bullion")
                    showBullion(section="bullion")
                    stockTotal = parse_positions(section="stocks", quiet=True) or 0.0
                    cryptoTotal = showCrypto(section="crypto", quiet=True) or 0.0
                    bullionTotal = showBullion(section="bullion", quiet=True) or 0.0
                    Totals = stockTotal + cryptoTotal + bullionTotal
                    print(f"\nGrand Total of Assets: ${Totals:,.2f}")
                    print("\n")
                elif section in ("e", "cash"):
                    print("Cash Amount Here")
                elif section in ("f", "items"):
                    print("item(s) Here")
                elif section in ("g", "add"):
                    print("\nAdd/Update A Position")
                    print("  1) Stock")
                    print("  2) Crypto (CoinGecko ID)")
                    print("  3) Bullion (gold|Silver)")
                    print("  4) Exit")
                    selectionUpdate = input("Please Choose 1/2/3 or 4: ").strip()
                    if selectionUpdate == "1":
                        add_stock_to_positions()
                    if selectionUpdate == "2":
                        add_crypto_to_positions()
                    if selectionUpdate == "3":
                        add_bullion_to_positions()
                    else: 
                        print("")
                else: 
                    print("Invalid Selection, Please Enter a/b/c/d/e/f or g")
        elif choice == "2":
            debtTracker()
        elif choice == "3":
            print("Exiting...")
            break

if __name__ == "__main__":
    _main_menu_()