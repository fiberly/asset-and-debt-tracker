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






## TODO: long term storage -> last saved price(s)?
# TODO: GUI?
# TODO: exit functionality from within menus
# TODO: removing items with a number instead of writing out stocks has, crypto needs
# TODO: Fix breaking out of loops in menus 
 # TODO: lower() for the exit words
 # TODO: ebay item lookup
 # TODO: Value over entry of input check, such as dollar amounts...
# TODO: offline stock check error over printing information
# TODO: First time use asset additions and debt additions
# TODO: motivational moments within the app
# TODO: Caching/saving the last loaded asset price



# static setting of current holdings
Stocks = {"AMZN": 1.0}
crypto = {"pi-network": 1700.0}
bullion = {"gold": 1.1, "silver": 16.0}
cash = {"cash": 0.0}
items = {"bicycle": 1000.0, "4090 Gigabyte": 2000.0}
debt = {"Apple Card": 2144.00, "Venture One": 2501.00}





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
    except Exception:
        print(f"Error retrieving the price for {ticker}")
    return None






# STOCK
# takes the ticker symbol and and quantity and returns prices
def parse_positions(s= "AMZN: 1.0", section="totals", quiet=True) -> dict[str, float]:
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
                tickerPrice = getPrice(ticker)
                if tickerPrice is None:
                    if not quiet:
                        print(f"Could not retrieve price for ticker: {ticker}")
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

def remove_stock_from_positions():
    print("Stock List")
    if not Stocks:
        print("No stock position(s)")
        return
    keysSorted = sorted(Stocks.keys())
    for number, key in enumerate(keysSorted, 1):
        print(f"{number}, {key},  {Stocks[key]} shares")
    StockTickerRemove = input("Enter stock ticker symbol, e.g. AAPL: ").strip().upper()
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
    try: 
        quantityStock = float(input("Enter number of shares to remove: ").strip())
    except ValueError:
        print("Invalid Number Entered")
        return
    if quantityStock < 0:
        print("Please enter a positive number.")
        return
    oldQuantity = float(Stocks.get(ticker, 0.0))
    newQuantity = max(0.0, oldQuantity - quantityStock)
    if newQuantity <= 1e-12:
        del Stocks[ticker]
        print(f"Removed {ticker}, 0 shares remaining.")
    else: 
        Stocks[ticker] = newQuantity
        print(f"Updated {ticker}, {newQuantity} shares, (removed {quantityStock})")






# CRYPTO PRICE
def showCrypto(section="totals", quiet=False) -> float:
        section = (section or "totals").strip().lower()
        show_crypto  = section in ("crypto", "cryptos", "b", "totals")  
        if not crypto:
            print("No crypto was/is saved.")
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
                print(f"\n{cryptoName}: {quantityCrypto} at the current price ${price:.2f}, Total Value: ${CryptoWorth:.2f}")
        return subtotal

def add_crypto_to_positions():
    coinGeckoID = input("Enter CoinGecko ID, e.g. bitcoin: ").strip()
    if not coinGeckoID:
        print("Canceled")
        return
    try: 
        quantityCrypto = float(input("Enter number of units to add: "))
    except ValueError:
        print("Invalid Number Entered")
        return
    crypto[coinGeckoID] = crypto.get(coinGeckoID, 0.0) + max(0.0, quantityCrypto)
    print(f"\nUpdated [{coinGeckoID}], with {crypto[coinGeckoID]} shares")

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
    else: 
        crypto[coinGeckoID] = newQuantityCrypto
        print(f"Updated {coinGeckoID} to {newQuantityCrypto}, (removed {quantityCrypto})")







#BULLION PRICE
def showBullion(section="totals", quiet=False) -> float:
    url = "https://api.gold-api.com"
    if requests is not None: 
        try: 
            xau = requests.get(f"{url}/price/XAU", timeout=10).json()["price"]  # USD/oz
            xag = requests.get(f"{url}/price/XAG", timeout=10).json()["price"]
        except Exception as e:
            xau = None
            xag = None
    else: 
        xau = None
        xag = None
    section = (section or "totals").strip().lower()
    show_bullion = section in ("bullion", "c", "totals")           
    if not show_bullion: 
        return 0.0
    subtotal = 0.0
    try: 
        goldPrice = float(xau) if xau is not None else None
        silverPrice = float(xag) if xag is not None else None
    except NameError:
        goldPrice = silverPrice = None
    goldOunce = bullion.get("gold", 0.0)
    silverOunce = bullion.get("silver", 0.0)
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
        #silverOunce = bullion.get("silver", 0.0)
        silverValue = silverOunce * silverPrice
        subtotal += silverValue
        if not quiet: 
            print(f"\nSilver : {silverOunce} at ${silverPrice:.2f}\n Total Gold Value: ${silverValue:.2f}")
    else:
        if not quiet:
            print(f"\nSilver : {bullion.get("silver", 0.0)} at N/A\n Total Gold Value: N/A")
    
    if goldPrice is None and silverPrice is None:
        if not quiet: 
            print("\nBullion prices are unavailable right now...\n")
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

def remove_bullion_from_positions():
    print("Bullion Assets")
    for name, quantity in bullion.items():
        print(f"{name} : {quantity} oz(s)")
    bullionGoldORSilver = input("Enter metal [gold | silver]: ").strip().lower()
    if bullionGoldORSilver in ("au", "xau"): bullionGoldORSilver = "gold"
    if bullionGoldORSilver in ("ag", "xag"): bullionGoldORSilver = "silver"
    if bullionGoldORSilver not in ("gold", "silver"):
        print("Please enter either gold or silver...")
        return
    try: 
        metalOunce = float(input("Enter number of units to remove: ").strip())
    except ValueError:
        print("Invalid Number Entered")
        return
    oldQuantityBullion = bullion.get(bullionGoldORSilver, 0.0)
    newQuantityBullion = max(0.0, oldQuantityBullion - metalOunce)
    if newQuantityBullion < 1e-12:
        del crypto[bullionGoldORSilver]
        print(f"Removed {bullionGoldORSilver}, 0 share(s)/unit(s) remaining")
    else: 
        bullion[bullionGoldORSilver] = newQuantityBullion
        print(f"\nUpdated {bullionGoldORSilver} to {newQuantityBullion:.2f}, (removed {metalOunce})")






# CASHSHOW
def showCash(section="totals", quiet=False) -> float:
        section = (section or "totals").strip().lower()
        show_cash  = section in ("cash", "e", "totals") 
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
    try: 
        ask = input("Type and press enter a number:  1) to add dollars or cents, 2) Exit : ")
    except ValueError:
        print("Invalid Number Entered")
        return
    if ask == "1":
        try: 
            quantityCash = float(input("Enter number of dollars and or cents to add: "))
        except ValueError:
            print("Invalid Number Entered.")
            return
        cash["cash"] = cash.get("cash", 0.0) + max(0.0, quantityCash)
        print(f"\nUpdated available cash, with {cash["cash"]:.2f} dollars")
    if ask == "2":
        print("Exiting...")
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
        elif ask == "2":
            print("Exiting...")
        else: 
            print("Invalid Input.")
    except ValueError:
                print("Invalid Number, please enter something valid")


        


# ITEMS SHOW
def showItems(section="totals", quiet=False) -> float:
        section = (section or "totals").strip().lower()
        show_items  = section in ("items", "e", "totals")  
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
    itemAdd = input("Enter item name, e.g. mobile phone: ").strip()
    if not itemAdd:
        print("Canceled")
        return
    try: 
        priceOfItem = float(input("Enter price/worth of item to: "))
    except ValueError:
        print("Invalid Number Entered")
        return
    items[itemAdd] = items.get(itemAdd, 0.0) + max(0.0, priceOfItem)
    print(f"\nUpdated [{itemAdd}], with ${items[itemAdd]}")

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
            except ValueError: 
                print("Invalid input, please try again.")    
                continue
        elif debtInput == "3":
             if not debt: 
                 print("\nNo debt accounts found")
                 continue
             print("\nCurrent Debt Accounts:")
             print("--- Remember, the banks do not mind the monthly payment. ---")
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
        elif debtInput == "4":
            print("Type [exit] and press enter to return to the menu.")
            name = input("\nEnter the name of the debt account to remove: ").strip()
            if name.lower() == "exit":
                print("Exiting...")
                continue
            if name in debt: 
                del debt[name]
                print(f"Removed {name} from debts")
            else: 
                print("Account Not Found")
            continue
        elif debtInput == "6":
            print("Exiting...")
            break
        else: 
            print("Please enter a valid choice")
            continue






def itemPriceChecker():
    print("item price check coming soon")
    return





# MAIN MENU
def _main_menu_():
    while True: 
        print("\nWelcome to the asset, debt and item price tracker!")
        print("1) positions")
        print("2) debt")
        print("3) item price")
        print("4) Exit")
        choice = input("Enter a choice of 1, 2, 3 or 4: ")
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
                    print("  3) Bullion (gold|Silver)")
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
                    print("  3) Bullion (gold|Silver)")
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
            itemPriceChecker()
        elif choice == "4":
            print("Exiting...")
            break

if __name__ == "__main__":
    _main_menu_()

