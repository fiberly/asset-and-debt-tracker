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
try: 
    import json
except Exception:
    json = None
try: 
    import os
except Exception:
    os = None
try: 
    import re
except Exception:
    re = None
try: 
    import sys
except Exception:
    sys = None
## TODO: last saved price(s)? shares owned still showing without internet?
# TODO: GUI?
# TODO: exit functionality from within menus: Remove menus needs and debt tracker
# TODO: removing items with a number instead of writing out stocks has, crypto needs
# TODO: Fix breaking out of loops in menus 
 # TODO: ebay item lookup
 # TODO: Value over entry of input check, such as dollar amounts...
# TODO: First time use asset additions and debt additions
# TODO: motivational moments within the app
# TODO: Caching/saving the last loaded asset price
# TODO: Charts? Chats?
#TODO: different currency support
# variable setting of current holdings
Stocks = {}
crypto = {}
bullion = {}
cash = {}
items = {}
debt = {}
data_file = "data_save.json"
def save_data():
    data = {"stocks": Stocks, "crypto": crypto, "bullion": bullion, "cash": cash, "items": items, "debt": debt}
    with open(data_file, "w") as f:
        json.dump(data, f, indent=4)
    print("Data saved successfully.")
def load_data(): 
    global Stocks, crypto, bullion, cash, items, debt
    if os.path.exists(data_file): 
        with open(data_file, "r") as f: 
            data = json.load(f)
            Stocks = data.get("stocks", {})
            crypto = data.get("crypto", {})
            bullion = data.get("bullion", {})
            cash = data.get("cash", {})
            items = data.get("items", {})
            debt = data.get("debt", {})
        print("Data loaded successfully.")
    else: 
        print("No save file found. Starting with a new file. ")
# STOCK PRICE
# gets price using the ticker symbol 
def getPrice(ticker: str) -> float | None: 
    if yfinance is None: 
        return None
    try: 
        if yfinance is None:
            return None
        null = None
        original_stdout = None
        original_stderr = None
        if sys is not None and os is not None:
            null = open(os.devnull, "w")
            original_stdout, original_stderr = sys.stdout, sys.stderr
            sys.stdout = null
            sys.stderr = null
        tick = yfinance.Ticker(ticker)
        historyPrice = tick.history(period="1d")
        if historyPrice is not None and not historyPrice.empty:
            return float(historyPrice["Close"].iloc[-1])
        if hasattr(tick, 'fast_info') and isinstance(tick.fast_info, dict):
            lastValue = tick.fast_info.get("last_price")
            if lastValue is not None:
                return float(lastValue)
        information = getattr(tick, "info", {}) or {}
        if isinstance(information, dict) and information.get("regularMarketPrice") is not None: 
            return float(information["regularMarketPrice"])
    except Exception:
        return None
    finally: 
        if sys is not None and null is not None:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            null.close()
    return None
# STOCK
# takes the ticker symbol and and quantity and returns prices
def parse_positions(s= "AMZN: 1.0", section="totals", quiet=True) -> dict[str, float]:
    section = (section or "totals").strip().lower()
    show_stocks  = section in ("stocks", "stock", "1", "totals")    
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
                tickerPrice = getPrice(ticker)
                if tickerPrice is None:
                    if not quiet:
                        print(f"Could not retrieve price for ticker: {ticker} with {quantity} share.")
                    continue
                TotalValue = tickerPrice * quantity
                subtotal += TotalValue
                if show_stocks: 
                    if section in ("stocks", "stock", "1", "totals"):
                        if not quiet:
                            print(f"\n{ticker}: {quantity} shares at ${tickerPrice:.2f} each, Total Value: ${TotalValue:.2f}")
                if section not in ("stocks", "stock", "1", "totals"):
                    print("Invalid Input")
        if not Stocks:
            print("No stock(s) in positions.")
            return
    except Exception as e:
        if not quiet: 
            print(f"\nError retrieving data for ticker:", e)
    return subtotal
def is_valid_ticker(ticker: str) -> bool:
    ticker = (ticker or "").strip()
    if not ticker or len(ticker) > 10:
        return False
    return ticker.isalpha()
def add_stock_to_positions():
    while True: 
        StockTicker = input("Enter stock ticker symbol, e.g. AAPL or type exit to return to menu: ").strip().upper()
        if StockTicker.lower() == "exit":
            print("Exiting...")
            break
        if not StockTicker:
            print("Canceled")
            continue
        if not is_valid_ticker(StockTicker):
            print("Invalid ticker format, only letter A-Z and a-z allowed, no spaces or numbers. Please Try Again.")
            continue
        quantityInput = input("Enter number of shares to add or type exit to return to menu: ").strip()
        if quantityInput.lower() == "exit":
            print("Exiting...")
            break
        try: 
            quantityStock = float(quantityInput)
        except ValueError:
            print("Invalid Number Entered")
            continue
        if quantityStock >= 9_999_999:
            print("Number of shares can not exceed 9,999,999.")
            continue
        if quantityStock <= 0:
            print("Please enter a non negative number.")
            continue
        tickerSymbol = StockTicker.upper()
        Stocks[tickerSymbol] = Stocks.get(tickerSymbol, 0.0) + max(0.0, quantityStock)
        print(f"Updated [{tickerSymbol}], with {Stocks[tickerSymbol]} shares")
        save_data()
        break
def remove_stock_from_positions():
    while True: 
        print("Stock List")
        if not Stocks:
            print("No stock position(s)")
            return
        keysSorted = sorted(Stocks.keys())
        for number, key in enumerate(keysSorted, 1):
            print(f"{number}) {key},  {Stocks[key]} shares")
        StockTickerRemove = input("Enter stock ticker symbol, e.g. AAPL or exit to return to menu: ").strip().upper()
        if StockTickerRemove.lower() == "exit":
            print("Exiting...")
            break
        if not StockTickerRemove:
            print("Cancelled")
            return
        ticker = None   
        if StockTickerRemove.isdigit():
            ids = int(StockTickerRemove)
            if 1 <= ids <= len(keysSorted):
                ticker = keysSorted[ids - 1]     
        if ticker is None: 
            ticker = StockTickerRemove.upper()
        if ticker not in Stocks:
            print("Please enter a stock from the list.")
            return
        quantityStock = input("Enter number of shares to remove or exit to return to menu: ").strip()
        if quantityStock == "exit":
            print("Exiting...")
            break
        try: 
            quantityStocks = float(quantityStock)
        except ValueError:
            print("Invalid Number Entered")
            return
        if quantityStocks <= 0:
            print("Please enter a positive number or non zero.")
            return
        oldQuantity = float(Stocks.get(ticker, 0.0))
        newQuantity = max(0.0, oldQuantity - quantityStocks)
        if newQuantity <= 1e-12:
            del Stocks[ticker]
            print(f"Removed {ticker}, 0 shares remaining.")
            save_data()
        else: 
            Stocks[ticker] = newQuantity
            print(f"Updated {ticker}, {newQuantity} shares, (removed {quantityStocks})")
            save_data()
# CRYPTO PRICE
def showCrypto(section="totals", quiet=False) -> float:
        section = (section or "totals").strip().lower()
        show_crypto = section in ("crypto", "cryptos", "2", "totals")  
        
        if not show_crypto:
            return 0.0
        if not show_crypto:
            if not quiet: 
                print("No crypto was/is saved.")
            return 0.0
        if CoinGeckoAPI is None:
            if not quiet: 
                print("CoinGecko is not available.")
            return 0.0
        crypto_id = list(crypto.keys())
        prices = {}
        try: 
            from concurrent.futures import ThreadPoolExecutor, TimeoutError
            coingGecko = CoinGeckoAPI()
            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(coingGecko.get_price, ids=crypto_id, vs_currencies="usd")
            try:
                data = future.result(timeout=1) or {}
            except TimeoutError:
                try: 
                    future.cancel()
                except Exception:
                    pass
                executor.shutdown(wait=False)
                if not quiet:
                    print("")
                data = {}
            finally:
                try: 
                    executor.shutdown(wait=False)
                except Exception:
                    pass
            for cryptoNames, CryptoQuantities in (data or {}).items():
                if isinstance(CryptoQuantities, dict):
                    prices[cryptoNames] = CryptoQuantities.get("usd")
        except Exception:
                if not quiet: 
                    print("Crypto prices are unavailable right now.")
                return 0.0
        subtotal = 0.0
        for cryptoName, quantityCrypto in crypto.items():
            information = data.get(cryptoName)
            price = information.get("usd") if isinstance(information, dict) else None
            if price is None:
                if not quiet: 
                    print(f"Could not fetch price for {cryptoName} with {quantityCrypto} units.")
                   ### LAST RECORDED PRICE HERE ###
                continue
            CryptoWorth = quantityCrypto * price
            subtotal += CryptoWorth
            if not quiet: 
                print(f"\n{cryptoName}: {quantityCrypto} at the current price ${price:.2f}, Total Value: ${CryptoWorth:.2f}")
        return subtotal
def is_valid_coingeckoid(cid: str) -> bool:
    cid = (cid or "").strip()
    if not cid or len(cid) > 50:
        return False
    return bool(re.match(r'^[a-z\-]+$', cid))
def add_crypto_to_positions():
    while True: 
        coinGeckoID = input("Enter CoinGecko ID, e.g. bitcoin or type exit to return to menu: ").strip()
        if coinGeckoID.lower() == "exit":
            print("Exiting...")
            break
        if not coinGeckoID:
            print("Canceled")
            return
        if not is_valid_coingeckoid(coinGeckoID):
                print("Invalid ticker format, only letters a-z and - are allowed. Please Try Again.")
                continue
        quantityInput = input("Enter number of units to add or type exit to return to menu: ").strip()
        if quantityInput.lower() == "exit":
            print("Exiting...")
            break
        try: 
            quantityCrypto = float(quantityInput)
        except ValueError:
            print("Invalid Number Entered")
            return
        if quantityCrypto >= 9_999_999:
            print("Number of shares can not exceed 9,999,999.")
            continue
        if quantityCrypto <= 0:
            print("Please enter a non negative number.")
            continue
        coingeckoIDKey = coinGeckoID.lower()
        crypto[coingeckoIDKey] = crypto.get(coingeckoIDKey, 0.0) + max(0.0, quantityCrypto)
        print(f"\nUpdated [{coingeckoIDKey}], with {crypto[coingeckoIDKey]} shares")
        save_data()
        return
    
def remove_crypto_from_positions():
    if not crypto:
        print("No crypto position(s)")
        return
    print("Current Crypto Positions: ")
    for name, keys in crypto.items():
        print(f"{name} : {keys} unit(s)/share(s)")
    coinGeckoID = input("Enter CoinGecko ID, e.g. bitcoin: ").strip()
    if not coinGeckoID:
        print("Canceled")
        return
    try: 
        quantityCrypto = float(input("Enter number of units to remove: "))
    except ValueError:
        print("Invalid Number Entered")
        return
    oldQuantityCrypto = crypto.get(coinGeckoID, 0.0)
    newQuantityCrypto = max(0.0, oldQuantityCrypto - quantityCrypto)
    if newQuantityCrypto < 1e-12:
        del crypto[coinGeckoID]
        print(f"Removed {coinGeckoID}, 0 share(s)/unit(s) remaining")
        save_data()
    else: 
        crypto[coinGeckoID] = newQuantityCrypto
        print(f"Updated {coinGeckoID} to {newQuantityCrypto}, (removed {quantityCrypto})")
        save_data()






#BULLION PRICE
def showBullion(section="totals", quiet=False) -> float:
    url = "https://api.gold-api.com"
    if requests is not None: 
        try: 
            xau = requests.get(f"{url}/price/XAU", timeout=10).json()["price"]  # USD/oz
            xag = requests.get(f"{url}/price/XAG", timeout=10).json()["price"]
            xpd = requests.get(f"{url}/price/XPD", timeout=10).json()["price"]
            hg = requests.get(f"{url}/price/HG", timeout=10).json()["price"]
        except Exception as e:
            xau = xag = xpd = hg = None
    else: 
        xau = xag = xpd = hg = None

    section = (section or "totals").strip().lower()
    show_bullion = section in ("bullion", "3", "totals")           
    if not show_bullion: 
        return 0.0
    subtotal = 0.0
    try: 
        goldPrice = float(xau) if xau is not None else None
        silverPrice = float(xag) if xag is not None else None
        palladiumPrice = float(xpd) if xpd is not None else None
        copperPrice = float(hg) if hg is not None else None
    except NameError:
        goldPrice = silverPrice = palladiumPrice = copperPrice = None
        
    goldOunce = bullion.get("gold", 0.0)
    silverOunce = bullion.get("silver", 0.0)
    palladiumOunce = bullion.get("palladium", 0.0)
    copperOunce = bullion.get("copper", 0.0)
    if goldPrice is not None:
       # goldOunce = bullion.get("gold", 0.0)
        goldValue = goldOunce * goldPrice
        subtotal += goldValue
        if not quiet: 
            print(f"\nGold : {goldOunce} at ${goldPrice:.2f}\n Total Gold Value: ${goldValue:.2f}")
    else: 
        if not quiet:
            print(f"\nGold : {bullion.get('gold', 0.0)}oz @ N/A\n Total Gold Value N/A")
    if silverPrice is not None:
        silverValue = silverOunce * silverPrice
        subtotal += silverValue
        if not quiet: 
            print(f"\nSilver : {silverOunce} at ${silverPrice:.2f}\n Total Gold Value: ${silverValue:.2f}")
    else:
        if not quiet:
            print(f"\nSilver : {bullion.get("silver", 0.0)} at N/A\n Total Silver Value: N/A")
    if palladiumPrice is not None: 
        palladiumValue = palladiumOunce * palladiumPrice
        subtotal += palladiumValue
        if not quiet: 
            print(f"\nPalladium : {palladiumOunce} at ${palladiumPrice:.2f}\n Total Palladium Value: ${palladiumValue:.2f}")
    else:
        if not quiet:
            print(f"\nPalladium : {bullion.get('palladium', 0.0)}oz @ N/A\n Total Palladium Value N/A")
    if copperPrice is not None: 
        copperValue = copperOunce * copperPrice
        subtotal += copperValue
        if not quiet: 
            print(f"\nCopper : {copperOunce} at ${copperPrice:.2f}\n Total Copper Value: ${copperValue:.2f}")
    else: 
        if not quiet:
            print(f"\nCopper : {bullion.get('copper', 0.0)}oz @ N/A\n Total Copper Value N/A")
    if goldPrice and silverPrice and palladiumPrice and copperPrice is None: 
        if not quiet: 
            print("\nBullion prices are unavailable right now...\n")


    
    return subtotal

def add_bullion_to_positions():
    while True: 
        bullionGoldORSilver = input("Enter metal [gold | silver | palladium | copper] or type exit to return to menu: ").strip().lower()
        if bullionGoldORSilver == "exit": 
            print("Exiting...")
            return
        if bullionGoldORSilver in ("au", "xau"): bullionGoldORSilver = "gold"
        if bullionGoldORSilver in ("ag", "xag"): bullionGoldORSilver = "silver"
        if bullionGoldORSilver in ("pd", "xpd"): bullionGoldORSilver = "palladium"
        if bullionGoldORSilver in ("cu", "hg"): bullionGoldORSilver = "copper"
        if bullionGoldORSilver not in ("gold", "silver", "palladium", "copper"):
            print("Please enter either gold, silver, palladium or copper...")
            return
        metalOunce = input("Enter number of units to add or type exit to return to menu: ").strip()
        if metalOunce == "exit":
            print("Exiting...")
            break
        try: 
            quantityBullion = float(metalOunce)
        except ValueError:
            print("Invalid Number Entered")
            return
        if quantityBullion <= 0:
            print("Please enter a non negative number.")
            continue
        if quantityBullion >= 9_999:
            print("Number of units can not exceed 9,999,999.")
            continue
        bullionKey = bullionGoldORSilver.lower()
        bullion[bullionKey] = bullion.get(bullionKey, 0.0) + max(0.0, quantityBullion)
        print(f"Updated [{bullionKey}], with {bullion[bullionKey]} ounces")
        save_data()
        return

def remove_bullion_from_positions():
    if not bullion: 
        print("No bullion position(s)")
        return
    while True: 
        print("Bullion Assets")
        for name, quantity in bullion.items():
            print(f"{name} : {quantity} oz(s)")
        bullionGoldORSilver = input("Enter metal [gold | silver | palladium | copper] or exit to return to menu: ").strip().lower()
        if bullionGoldORSilver == "exit":
            break
        if bullionGoldORSilver in ("au", "xau"): bullionGoldORSilver = "gold"
        if bullionGoldORSilver in ("ag", "xag"): bullionGoldORSilver = "silver"
        if bullionGoldORSilver in ("pd", "xpd"): bullionGoldORSilver = "palladium"
        if bullionGoldORSilver in ("cu", "hg"): bullionGoldORSilver = "copper"
        if bullionGoldORSilver not in ("gold", "silver", "palladium", "copper", "exit"):
            print("Please enter either gold, silver, palladium or copper...")
            continue
        try: 
            metalOunce = float(input("Enter number of ounces to remove or type exit to return to menu: ").strip())
        except ValueError:
            print("Invalid Number Entered")
            continue
        if metalOunce == "exit":
            break
        if metalOunce < 0: 
            print("Please enter a non negative number.")
            continue
        if not bullionGoldORSilver or bullionGoldORSilver == "exit":
            print("Exiting...")
            continue
        oldQuantityBullion = bullion.get(bullionGoldORSilver, 0.0)
        newQuantityBullion = max(0.0, oldQuantityBullion - metalOunce)
        if newQuantityBullion < 1e-12:
            del bullion[bullionGoldORSilver]
            print(f"Removed {bullionGoldORSilver}, 0 share(s)/unit(s) remaining")
            save_data()
        else: 
            bullion[bullionGoldORSilver] = newQuantityBullion
            print(f"\nUpdated {bullionGoldORSilver} to {newQuantityBullion:.2f}, (removed {metalOunce})")
            save_data()
        break





# CASH SHOW
def showCash(section="totals", quiet=False) -> float:
        section = (section or "totals").strip().lower()
        show_cash  = section in ("cash", "5", "totals") 
        if not cash: 
            print("Cash Available is $0") 
            return
        if not show_cash:
            return 0.0
        subtotal = 0.0
        for dictName, quantityDollars in cash.items():
            if quantityDollars is None: 
                if not quiet: 
                    print(f"{dictName}: no dollar amount recorded")
                continue
            subtotal += quantityDollars
            if not quiet: 
                print(f"{dictName}: ${quantityDollars}")
        return subtotal

def add_cash_to_positions():
    while True: 

        ask = input("Enter 1 to add dollars/cents or type exit to return to menu: ").strip().lower()
        if ask == "exit":
            print("Exiting...")
            return
        if ask != "1":
            print("Please enter 1 to add cash or exit to return to menu.")
        if ask == "1":
            quantityCash = input("Enter number of dollars/cents to add or type exit to return to menu: ").strip()
            if quantityCash.lower() == "exit":
                print("Exiting...")
                return
            try:
                quantityOfCash = float(quantityCash)
            except ValueError:
                print("Invalid Number Entered.")
                continue
            if quantityOfCash <= 0:
                print("Number entered needs to be larger than 0.")
                continue
            if quantityOfCash > 9_999_999_999_999:
                print("Entered amount can not exceed 9,999,999,999,999.")
                continue
            cash["cash"] = cash.get("cash", 0.0) + quantityOfCash
            print(f"\nUpdated available cash, with {cash["cash"]:.2f} dollars")
            save_data()
            return
    

def remove_cash_from_position():
    print("\nRemoving Cash")
    try: 
        ask = input("Type and press enter a number:  1) to subtract from cash, 2) to Quit: ")
        if ask == "1":
            amount = float(input("Enter an amount to subtract as an whole number with up to two decimal places "))
            oldBalance = cash["cash"]
            cash["cash"] = max(0.0, oldBalance - max(0.0, amount))
            print(f"{cash}: \nOld Balance ${oldBalance:,.2f} \nNew Balance ${cash["cash"]:,.2f}")
            save_data()
        elif ask == "2":
            print("Exiting...")
        else: 
            print("Invalid Input.")
    except ValueError:
                print("Invalid Number, please enter something valid")


        


# ITEMS SHOW
def showItems(section="totals", quiet=False) -> float:
        section = (section or "totals").strip().lower()
        show_items  = section in ("items", "4", "totals")  
        if not show_items:
            return 0.0
        if not items:
            print("No items to remove..")
            return
        subtotal = 0.0
        for itemName, amount in items.items():
            if amount is None: 
                if not quiet: 
                    print(f"{itemName}: no dollar amount recorded")
                continue
            subtotal += amount
            if not quiet: 
                print(f"{itemName}: ${amount}")
        return subtotal

def add_item_to_positions():
    while True: 
        itemAdd = input("Enter item name, e.g. mobile phone or type exit to return to menu: ").strip()
        if itemAdd == "exit":
            print("Exiting...")
            return
        if not itemAdd:
            print("Canceled")
            return
        if len(itemAdd) > 50:
            print("Length can not be longer than 50 characters.")
            continue
        priceOfItem = input("Enter price/worth of item to: ")
        if priceOfItem.lower() == "exit":
            print("Exiting...")
            return
        try:
            itemPrice = float(priceOfItem)
        except ValueError:
            print("Invalid Number Entered")
            continue
        if itemPrice <= 0:
            print("Please enter a number larger than 0.")
            continue
        if itemPrice > 9_999_999_999:
            print("Entered price can not exceed 9,999,999,999.")
            continue
        items[itemAdd] = items.get(itemAdd, 0.0) + max(0.0, itemPrice)
        print(f"\nUpdated [{itemAdd}], with ${items[itemAdd]}")
        save_data()
        return

def remove_item_from_position():
    if not items:
        print("No items to remove..")
        return
    print("\nCurrent Item(s)")
    for itemLoop in items.keys():
        print(itemLoop)
    print("\n")
    print("Please enter: \n 1) Lower value of item\n 2) Remove item completely\n 3) Exit")
    while True: 
        inputForDollarAmountRemoval = input("Select 1) Lower value of item, 2) Remove item completely or 3) Exit: ").strip()
        if inputForDollarAmountRemoval == "3":
            print("Exiting...")
            break
        if inputForDollarAmountRemoval == "1":
            for itemLoop in items.keys():
                print(itemLoop)
            itemSelection = input("Enter item name to lower dollar amount: ").strip()
            if itemSelection == "3":
                print("Exiting...")
                break
            if itemSelection not in items.keys():
                print("Please enter an item from the list.")
                return
            match = next((matches for matches in items if matches.lower() == itemSelection.lower()), None)
            try: 
                amount = float(input("\nEnter [EXIT] to exit.\nEnter an amount to subtract as  whole number with up to two decimal places\n e.g. 10.75, 10, 5.50, etc. ").strip())
                if amount == "EXIT".strip().upper():
                    return
                oldBalance = items[match]
                items[match] = max(0.0, oldBalance - max(0.0, amount))
                print(f"{match}: \nOld item price ${oldBalance:,.2f} \nNew item price ${items[match]:,.2f}")
                save_data()
                break
            except ValueError:
                    print("Exiting...")
        else:
            print("Enter a valid dollar amount.")
            for itemLoop in items.keys():
                print(itemLoop)
            print("Enter the name exactly as shown under Current Item(s), or enter 3 to exit.")
            if inputForDollarAmountRemoval == "2": 
                itemRemoval = input("Enter an item name to remove: ").strip()
                if itemRemoval == "3":
                    print("Exiting...")
                    break
                matchItemRemoval = next((matches for matches in items if matches.lower() == itemRemoval.lower()), None)
                if matchItemRemoval: 
                    del items[matchItemRemoval]
                    print(f"\nRemoved {matchItemRemoval} from items")
                    save_data()
                    return
                else: 
                    print("Item Not Found")
        break
    





# DEBT TRACKER
def debtTracker():
    while True: 
        print("\nDebt Tracker")
        print(" 1) View Debt\n 2) Add Debt\n 3) Subtract Debt\n 4) Remove Debt Account\n 5) Total Debt\n 6) Exit")
        debtInput = input("Input a number: ").strip()
        if debtInput == "1":
            if not debt:
                print("No debt(s) recorded")
            else: 
                print("\nCurrent Debts")
                for name, amount in debt.items():
                    print(f"{name}: ${amount:.2f}")
                    continue
            continue
        elif debtInput == "5":
                debtTotal = sum(debt.values())
                print(f"\nTotal debt: ${debtTotal:.2f}")
        elif debtInput == "2":
            if debt:
                print(f"\nCurrent Selectable Choices for Debt Accounts: ")
                for name in debt.keys():
                    print(f"{name}")
            print("Type [exit] and press enter to return to the menu.")
            debtSelect = input("Enter the name of a debt account: ")
            AccountMatch = next((match for match in debt if match.lower() == debtSelect.lower()), None)
            if debtSelect == "exit":
                print("Exiting...")
                continue
            if not AccountMatch:
                while True: 
                    print(f"Account [{debtSelect}] not found, would you like to add the account?")
                    yorn = input("Enter y or n: ").strip().lower()
                    if yorn in ("y"):
                        AccountMatch = debtSelect
                        debt[AccountMatch] = 0.0
                        print("--- Suggestion: Sign on for payment plans you can afford / manage. ---")
                        print(f"Created Account {AccountMatch},  Successfully!")
                        save_data()
                        break
                    elif yorn in ("n"):
                        print("The account will not be added.")
                        break
                    else: 
                        print("please enter a valid y or n")
            if not AccountMatch:
                continue
            print("Type [exit] and press enter to return to the menu.")
            try: 
                debtAddition = float(input("\nEnter a number to add to the debt: ").strip())
                if debtAddition == "exit":
                    print("Exiting...")
                    continue
                debt[AccountMatch] = debt.get(AccountMatch, 0.0) + max(0.0, debtAddition)
                print("\n--- Try not to leave unpaid balances at months end. ---")
                print(f"Debt added: {AccountMatch}: ${debt[AccountMatch]:,.2f}")
                save_data()
            except ValueError: 
                print("Invalid input, please try again.")    
                continue
        elif debtInput == "3":
             if not debt: 
                 print("\nNo debt accounts found")
                 continue
             print("--- Remember, the banks do not mind the monthly payment. ---")
             print("\nCurrent Debt Accounts:")
             for name in debt.keys():
                 print(f"{name}")
             print("Type [exit] and press enter to return to the menu.")
             removeAmount = input("Enter the account name to subtract debt from: ").strip()
             match = next((matches for matches in debt if matches.lower() == removeAmount.lower()), None)
             if removeAmount == "exit":
                print("Exiting...")
                continue
             if not match:
                print("Account Not Found")
                continue
             amount = input("Enter an amount to subtract as a whole number with up to two decimal places: ").strip()
             if amount == "quit":
                print("Exiting...")
                continue    
             try: 
                amountCheck = float(amount)
             except ValueError:
                 print("Invalid Number, please enter something valid")
                 continue
             if amountCheck < 0:
                print("Please enter a positive Number")
                continue
             oldBalance = debt[match]
             newBalance = max(0.0, oldBalance - amountCheck)
             debt[match] = newBalance
             print(f"{match}: \nOld Balance ${oldBalance:,.2f} \nNew Balance ${newBalance:,.2f}")
             save_data()
        elif debtInput == "4":
            print("Type [exit] and press enter to return to the menu.")
            name = input("\nEnter the name of the debt account to remove: ").strip()
            if name.lower() == "exit":
                print("Exiting...")
                continue
            if name in debt: 
                del debt[name]
                print(f"Removed {name} from debts")
                save_data()
            else: 
                print("Account Not Found")
            continue
        elif debtInput == "6":
            print("Exiting...")
            break
        else: 
            print("Please enter a valid choice")
            continue







# MAIN MENU
def _main_menu_():
    while True: 
        print("\nWelcome to the asset, debt and item price tracker!")
        print("1) positions")
        print("2) debt")
        print("3) Exit")
        choice = input("Enter a choice of 1, 2 or 3: ")
        if choice == "1":
            while True: 
                print("\nPositions")
                print("  1) Stocks")
                print("  2) Crypto")
                print("  3) Bullion")
                print("  4) Totals")
                print("  5) Cash ")
                print("  6) Items")
                print("  7) Add/Update Position")
                print("  8) Remove/Delete Position")
                print("  9) Exit")
                entry = input("Choose 1/2/3/4/5/6/7/8 or 9: ").strip().lower()
                section = {"1": "stocks", "2": "crypto", "3": "bullion", "4": "totals", "5": "cash", "6": "items", "7": "add", "8": "remove", "9": "exit"}
                if entry in ("9", "exit"):
                    break 
                if entry not in section:
                    print("Invalid Selection, please enter a different choice. ")
                    continue
                else: 
                    section = section[entry]
                if section in ("stocks", "stock", "1"):
                    parse_positions(section="stocks", quiet=False)
                elif section in ("crypto", "cryptos", "2"):
                    showCrypto(section="crypto")
                elif section in ("bullion", "3"):
                    showBullion(section="bullion")
                elif section in ("4", "totals"):
                    print("\n Totals:  ")
                    stockTotal = parse_positions(section="stocks", quiet=True) or 0.0
                    print(f"\nStock Dollar Total: \n ${stockTotal:.2f}")
                    cryptoTotal = showCrypto(section="crypto", quiet=True) or 0.0
                    print(f"\nCrypto Dollar Total: \n ${cryptoTotal:.2f}")
                    bullionTotal = showBullion(section="bullion", quiet=True) or 0.0
                    print(f"\nBullion Dollar Total: \n ${bullionTotal:.2f}")
                    print("\nCash Dollar Total: ")
                    if not cash: 
                        print("Cash Available is $0")
                    else: 
                        cashTotal = cash["cash"]
                        print(f" ${cashTotal:.2f}")
                    print("\nItem(s) Dollar Total: ")
                    cashTotal = sum(cash.values())
                    itemTotal = sum(items.values())
                    print(f" ${itemTotal}")
                    StockCryptoBullionTotals = stockTotal + cryptoTotal + bullionTotal
                    print("\nStock, Cryptocurrency and Bullion Totals: ")
                    print(f" ${StockCryptoBullionTotals:.2f}")
                    print(f"\nStock, Cryptocurreny, Bullion and Cash Totals")
                    StockCryptoBullionCashTotals = StockCryptoBullionTotals + cashTotal
                    print(f" ${StockCryptoBullionCashTotals:.2f}")
                    GrandTotals = stockTotal + cryptoTotal + bullionTotal + cashTotal + itemTotal
                    print(f"\nGrand Total of Stock, Cryptocurrency, Bullion, Cash and Item(s): \n ${GrandTotals:,.2f}")
                    debtTotal = sum(debt.values())
                    print(f"\nTotals for Stock, Cryptocurrency, Bullion, Cash minus the debt accounts")
                    AssetSubtractionMinusItems = StockCryptoBullionCashTotals - debtTotal
                    print(f" ${AssetSubtractionMinusItems:.2f}")
                    print(f"\nTotals after Stock, Cryptocurrency, Bullion, Cash and Item(s) minus the debt accounts")
                    TotalAssetSubtraction = GrandTotals - debtTotal
                    print(f" ${TotalAssetSubtraction:.2f}")
                    print("\n")
                elif section in ("5", "cash"):
                    print("\nCash")
                    showCash(section="cash", quiet=False)
                elif section in ("6", "items"):
                    print("\nItem(s)")
                    showItems(section="items", quiet=False)
                elif section in ("7", "add"):
                    print("\nAdd/Update A Position")
                    print("  1) Stock")
                    print("  2) Crypto (CoinGecko ID)")
                    print("  3) Bullion (gold|silver|palladium|copper)")
                    print("  4) Cash")
                    print("  5) Item")
                    print("  6) Exit")
                    selectionUpdate = input("Please Choose 1/2/3/4/5 or 6: ").strip()
                    if selectionUpdate == "1":
                        add_stock_to_positions()
                    if selectionUpdate == "2":
                        add_crypto_to_positions()
                    if selectionUpdate == "3":
                        add_bullion_to_positions()
                    if selectionUpdate == "4":
                        add_cash_to_positions()
                    if selectionUpdate == "5":
                        add_item_to_positions()
                    if selectionUpdate == "6":
                        print("Exiting...")
                        continue
                    if selectionUpdate not in ["1", "2", "3", "4", "5", "6"]:
                        print("\nPlease enter a number being 1, 2, 3, 4, 5 or 6")
                    else:
                        continue
                elif section in ("8", "remove"):
                    print("Select something to lower position size")
                    print("\nLower/Remove A Position")
                    print("  1) Stock")
                    print("  2) Crypto (CoinGecko ID)")
                    print("  3) Bullion (gold|silver|palladium|copper)")
                    print("  4) Cash")
                    print("  5) Item")
                    print("  6) Exit")
                    removeInput = input("\nPlease select either 1, 2, 3, 4, 5 or 6: ").strip()
                    if removeInput == "1":
                        remove_stock_from_positions()
                    if removeInput == "2":
                        remove_crypto_from_positions()
                    if removeInput == "3":
                        remove_bullion_from_positions()
                    if removeInput == "4": 
                        remove_cash_from_position()
                    if removeInput == "5": 
                        remove_item_from_position()
                elif entry not in section:
                    print("Please enter one of the number choices")
                else: 
                    print("Invalid Selection, Please Enter 1/2/3/4/5/6/7/8 or 9")
        elif choice == "2":
            debtTracker()
        elif choice == "3":
            print("Exiting...")
            break

if __name__ == "__main__":
    load_data()
    _main_menu_()

