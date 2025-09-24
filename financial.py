try: 
    import certifi
    os.environ["SSL_CERT_FILE"] = certifi.where()
except Exception:
    pass
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
os.environ.setdefault("LLAMA_LOG_LEVEL", "ERROR")
os.environ.setdefault("GGML_LOG_LEVEL",  "ERROR")
os.environ.setdefault("GGML_METAL", "0")
try: 
    import re
except Exception:
    re = None
try: 
    import sys
except Exception:
    sys = None
from typing import Any, Dict
try: 
    from LLM_Helper import ask_ai, ai_snapshot
    AIAvailable = True
except Exception:
    LLM_Helper = None
    AIAvailable = False
    def ask_ai(question: str, **kwargs):
        return "AI feature not available in this build."
    def ai_snapshot(*args, **kwargs):
        return {}
try: 
    from importlib import import_module
except Exception:
    importlib = None
    import_module = None
import platform
# variable setting of current holdings
Stocks = {}
crypto = {}
bullion = {}
cash = {}
items = {}
debt = {}
budget = { 
    "total": 0.0,
    "food": 0.0,
    "entertainment": 0.0,
    "housing": 0.0,
    "utilities": 0.0,
    "clothing": 0.0
}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_file = os.path.join(BASE_DIR, "data", "data_save.json")
APP_NAME = "Asset and Debt Tracker"
def _user_data_dir():
    sysname = platform.system()
    if sysname == "Darwin":
        base = os.path.expanduser(f"~/Library/Application Support")
    elif sysname == "Windows":
        base = os.environ.get("APPDATA") or os.path.expanduser("~\\AppData\\Roaming")
    else:
        base = os.path.expanduser(f"~/.local/share")
    return os.path.join(base, APP_NAME)
                                                               
if getattr(sys, "frozen", False):
    userDirectory = os.path.join(_user_data_dir(), "data")
    os.makedirs(userDirectory, exist_ok=True)
    data_file = os.path.join(userDirectory, "data_save.json")




MODEL_PATH = os.path.join(BASE_DIR, "models", "qwen2.5-0.5b-instruct-q2_k.gguf")  
MAX_TOKENS = 512
TEMPERATURE = 0.2
Llama   = None
BACKEND = None
def save_data():
    data = {"stocks": Stocks, "crypto": crypto, "bullion": bullion, "cash": cash, "items": items, "debt": debt, "budget": budget}
    with open(data_file, "w") as f:
        json.dump(data, f, indent=4)
def load_data(): 
    global Stocks, crypto, bullion, cash, items, debt, budget
    if os.path.exists(data_file): 
        with open(data_file, "r") as f: 
            data = json.load(f)
            Stocks.clear()
            stocks_raw = data.get("stocks", {})
            normalized_stocks = {}
            for ticker, payload in stocks_raw.items():
                if isinstance(payload, dict) and "cost_basis" in payload:
                    # Handles the correct cost_basis format
                    normalized_stocks[ticker] = { "shares": float(payload.get("shares", 0.0)), "cost_basis": float(payload.get("cost_basis", 0.0)), }
                else:
                    # Fallback for older formats or incomplete data
                    normalized_stocks[ticker] = { "shares": float(payload), "cost_basis": 0.0 }
            Stocks.update(normalized_stocks)

            crypto.clear()
            crypto_raw = data.get("crypto", {})
            normalized_crypto = {}
            for cid, payload in crypto_raw.items():
                if isinstance(payload, dict) and "cost_basis" in payload:
                    # Handles the correct cost_basis format
                    normalized_crypto[cid] = { "units": float(payload.get("units", 0.0)), "cost_basis": float(payload.get("cost_basis", 0.0)), }
                else:
                    # Fallback for older formats (just quantity)
                    normalized_crypto[cid] = { "units": float(payload), "cost_basis": 0.0 }
            crypto.update(normalized_crypto)
            bullion.clear()
            bullion_raw = data.get("bullion", {})
            normalized_bullion = {}
            for metal, payload in bullion_raw.items():
                if isinstance(payload, dict) and "cost_basis" in payload:
                    # Handles the correct cost_basis format
                    normalized_bullion[metal] = { "units": float(payload.get("units", 0.0)), "cost_basis": float(payload.get("cost_basis", 0.0)), }
                else:
                    # Fallback for older formats (just quantity)
                    normalized_bullion[metal] = { "units": float(payload), "cost_basis": 0.0 }
            bullion.update(normalized_bullion)
            cash.clear()
            cash.update(data.get("cash", {}))
            items.clear()
            items.update(data.get("items", {}))
            debt.clear()
            debt.update(data.get("debt", {}))
            budget.clear()
            budget.update(data.get("budget", {}))
        print("Data loaded successfully.")
    else: 
        print("No save file found. Starting with a new file. ")
#helper file for asking for deletion
def safe_subtract_and_maybe_delete(dictionaryList: dict, item: str, quantity: float) -> bool:
    if item not in dictionaryList:
        print("Item not found.")
        return False
    current = float(dictionaryList.get(item, 0.0))
    if quantity <= 0:
        print("Enter a positive removal amount.")
        return False
    if quantity >= current:
        print(f"Requested removal ({quantity}) >= holding ({current}).")
        confirm = input("Remove entire position and delete it? (y/N): ").strip().lower()
        if confirm == "y":
            del dictionaryList[item]
            print(f"Removed {item}.")
            return True
        print("Canceled.")
        return False
    dictionaryList[item] = current - quantity
    print(f"Updated {item}: {dictionaryList[item]} (removed {quantity})")
    return True

def profit_loss_stock():
    #stockProfit = 
   # stockLoss = 
   pass

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
def parse_positions(s= "AMZN: 1.0", section="totals", quiet=True) -> float:
    section = (section or "totals").strip().lower()
    show_stocks  = section in ("stocks", "stock", "1", "totals")    
    tickerANDAmounts = s.split(",")
    extraRemoved = [strippedParts.strip() for strippedParts in tickerANDAmounts]
    outputDictionary = {}
    for splitParts in extraRemoved: 
        ticker, position_data = splitParts.split(":", 1)
        outputDictionary[ticker] = float(position_data)
    subtotal = 0.0
    try:   
        if show_stocks: 
            if not Stocks:
                if not quiet: print("No stock(s) in positions.")
                return 0.0
            for ticker, position_data in Stocks.items():
                shares = position_data["shares"] if isinstance(position_data, dict) else float(position_data)
                cost_basis = position_data.get("cost_basis", 0.0) if isinstance(position_data, dict) else 0.0
                avg_buy_price = (cost_basis / shares) if shares > 0 else 0.0
                tickerPrice = getPrice(ticker)
                if tickerPrice is None:
                    if not quiet:
                        print(f"Could not retrieve price for ticker: {ticker} with {shares} share(s).")
                    continue
                TotalValue = tickerPrice * shares
                subtotal += TotalValue
                if show_stocks: 
                    if section in ("stocks", "stock", "1", "totals"):
                        if not quiet:
                            current_value = tickerPrice * shares
                            profit_loss = current_value - cost_basis
                            pnl_string = f"P/L: ${profit_loss:,.2f}"
                            print(f"\n{ticker}: {shares} shares @ avg buy price of ${avg_buy_price:,.2f}. Total Purchase(s) Cost: ${cost_basis:,.2f}\nCurrent Stock Price: ${tickerPrice:,.2f} | Current Stock Total: ${current_value:,.2f} | ({pnl_string})")
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
        print("Current Crypto Positions: ")
        keysSorted = sorted(Stocks.keys())
        for name, keys in enumerate(keysSorted, 1):
            print(f"{name} : {keys} unit(s)/share(s)")
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
        buyInStockInput = input("Enter price that you bought the stock at or type exit to return to menu: ").strip()
        if buyInStockInput.lower() == "exit":
            print("Exiting...")
            break
        try: 
            priceWhenPurchased = float(buyInStockInput)
        except ValueError:
            print("Invalid Number Entered")
            continue
        if priceWhenPurchased >= 9_999_999:
            print("Number of shares can not exceed 9,999,999.")
            continue
        if quantityStock <= 0:
            print("Please enter a non negative number.")
            continue

        tickerSymbol = StockTicker.upper()
        stockPosition = Stocks.get(tickerSymbol, {"shares": 0.0, "cost_basis": 0.0})

        current_shares = float(stockPosition.get("shares", 0.0))
        current_cost_basis = float(stockPosition.get("cost_basis", 0.0))

        stockPosition["shares"] = current_shares + quantityStock # This was duplicated, removing one
        stockPosition["cost_basis"] = current_cost_basis + (quantityStock * priceWhenPurchased)

        Stocks[tickerSymbol] = stockPosition
        new_avg_price = (stockPosition['cost_basis'] / stockPosition['shares']) if stockPosition['shares'] > 0 else 0.0
        print(f"Updated [{tickerSymbol}], now holding {stockPosition['shares']} shares. New average price is ${new_avg_price:,.2f}/share.")
        save_data()
        break
def remove_stock_from_positions():
    while True: 
        print("Stock List")
        if not Stocks:
            print("No stock position(s)")
            break
        keysSorted = sorted(Stocks.keys())
        for number, key in enumerate(keysSorted, 1):
            print(f"{number}) {key},  {Stocks[key]} shares")
        StockTickerRemove = input("Enter stock ticker symbol, e.g. AAPL or exit to return to menu: ").strip()
        if StockTickerRemove.lower() == "exit":
            print("Exiting...")
            break
        if not StockTickerRemove:
            print("Cancelled")
            continue
        ticker = None   
        # allows selecting by numeric index
        if StockTickerRemove.isdigit():
            ids = int(StockTickerRemove)
            if 1 <= ids <= len(keysSorted):
                ticker = keysSorted[ids - 1]     
        # if ticker not a numeric selection, interperet as a non-numeric ticker symbol
        if ticker is None: 
            ticker = StockTickerRemove.upper()
        # if ticker is not found, allow 
        if ticker not in Stocks:
            print("Please enter a stock from the list.")
            continue
        # ask user for number of shares to remove

        # takes the old quantity before any removal, current quantity, and prints 
       # oldQuantity = float(Stocks.get(ticker, 0.0))
        dictGrab = Stocks.get(ticker, {"shares": 0.0, "cost_basis": 0.0})
        oldQuantity = float(dictGrab.get("shares", 0.0))
        print(f"Current holdings for {ticker}: {oldQuantity} shares")
        
        # checks for user input
        quantityStock = input("Enter number of shares to remove or exit to return to menu: ").strip()
        # checks for user input exit
        if quantityStock == "exit":
            print("Exiting...")
            break

        # pase input as a float, saved to a new variable, on error allow retry of entry
        try: 
            quantityStocks = float(quantityStock)
        except ValueError:
            print("Invalid Number Entered")
            continue
        # checks for input maximum and minimum
        if quantityStocks <= 0:
            print("Please enter a positive number or non zero.")
            continue
        if quantityStocks >= 9_999_999:
            print("The maximum number that can be entered is 9,999,999.")
            continue
        
        if quantityStocks > oldQuantity:
            print(f"Requested removal of {quantityStocks} shares, that amount exceeds current holdings of {oldQuantity}.")
            confirmDeletion = input("Remove entire position for the selected stock (y/n): ").strip().lower()
            if confirmDeletion == "y":
                del Stocks[ticker]
                print(f"Removed {ticker}, 0 shares remaining.")
                save_data()
                continue
            else: 
                print("Exiting...")
                continue
        
        # Reduce cost basis proportionally
        old_cost_basis = dictGrab.get("cost_basis", 0.0)
        cost_basis_to_remove = (old_cost_basis / oldQuantity) * quantityStocks if oldQuantity > 0 else 0

        newQuantity = max(0.0, oldQuantity - quantityStocks)
        if newQuantity <= 1e-12:
            del Stocks[ticker]
            print(f"Removed {ticker}, 0 shares remaining.")
        else: 
            dictGrab["shares"] = newQuantity
            dictGrab["cost_basis"] = max(0.0, old_cost_basis - cost_basis_to_remove)
            Stocks[ticker] = dictGrab
            print(f"Updated {ticker}, {newQuantity} shares, (removed {quantityStocks})")
        save_data()
        return
            
def getGUICryptoPrices(ids, quiet=False):
    if CoinGeckoAPI is None:
        if not quiet:
            print("CoinGecko is not available.")
        return {}
    valid_ids = [cid for cid in ids if isinstance(cid, str) and cid]
    if not valid_ids:
        return {}
    try:
        data = CoinGeckoAPI().get_price(ids=valid_ids, vs_currencies="usd") or {}
    except Exception:
        if not quiet:
            print("Crypto prices are unavailable right now.")
        return {}
    prices = {}
    for cid_key in valid_ids:
        price_data = data.get(cid_key)
        if isinstance(price_data, dict) and isinstance(price_data.get("usd"), (int, float)):
            prices[cid_key] = float(price_data["usd"])
    return prices 

# CRYPTO PRICE
def showCrypto(section="totals", quiet=False) -> float:
        if not crypto:
            if not quiet: 
                print("No crypto position(s)")
            return
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
        for cid, position_data in crypto.items():
            units = position_data.get("units", 0.0) if isinstance(position_data, dict) else float(position_data)
            cost_basis = position_data.get("cost_basis", 0.0) if isinstance(position_data, dict) else 0.0
            avg_buy_price = (cost_basis / units) if units > 0 else 0.0
            
            price_info = data.get(cid)
            price = price_info.get("usd") if isinstance(price_info, dict) else None
            if price is None:
                if not quiet: 
                    print(f"Could not fetch price for {cid} with {units} units.")
                continue
            current_value = units * price
            profitLoss = current_value - cost_basis
            profitLoss_string = f"P/L: ${profitLoss:,.2f}"
            CryptoWorth = units * price
            subtotal += CryptoWorth
            if not quiet: 
                print(f"\n{cid}: {units} units @ avg buy price of ${avg_buy_price:,.2f}. Total Purchase(s) Cost: ${cost_basis:,.2f}\nCurrent Crypto Price: ${price:,.2f}, Current Value: ${current_value:,.2f} | ({profitLoss_string})")
        return subtotal
def is_valid_coingeckoid(cid: str) -> bool:
    cid = (cid or "").strip()
    if not cid or len(cid) > 50:
        return False
    return bool(re.match(r'^[a-z\-]+$', cid))
def add_crypto_to_positions():
    while True: 
        print("Current Crypto Positions: ")
        keysSorted = sorted(crypto.keys())
        for name, keys in enumerate(keysSorted, 1):
            print(f"{keys}")
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
           # get current crypto holdings and print the selected crypto with the number of held units
              #  print(f"Current holding for {quantityInput}) {currentQuantityCrypto} unit(s).")
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
        
        buyInCryptoInput = input("Enter price that you bought the crypto at or type exit to return to menu: ").strip()
        if buyInCryptoInput.lower() == "exit":
            print("Exiting...")
            break
        try:
            priceWhenPurchased = float(buyInCryptoInput)
        except ValueError:
            print("Invalid Number Entered")
            continue
        if priceWhenPurchased <= 0:
            print("Please enter a non-negative number.")
            continue
        if priceWhenPurchased >= 9_999_999_999:
            print("Please enter a number leass than 9_999_999_999")
            continue
        
        coingeckoIDKey = coinGeckoID.lower()
        position = crypto.get(coingeckoIDKey, {"units": 0.0, "cost_basis": 0.0})
        position["units"] += quantityCrypto
        position["cost_basis"] += quantityCrypto * priceWhenPurchased
        crypto[coingeckoIDKey] = position
        new_avg_price = (position['cost_basis'] / position['units']) if position['units'] > 0 else 0.0
        print(f"\nUpdated [{coingeckoIDKey}], now holding {position['units']} units. New average price is ${new_avg_price:,.2f}/unit.")
        save_data()
        return
def remove_crypto_from_positions():
    # if there is no crypto saved, exit the function early
    if not crypto:
        print("No crypto position(s)")
        return
    # show the crypto positions from the crypto dictionary
    print("Current Crypto Positions: ")
    keysSorted = sorted(crypto.keys())
    for name, keys in enumerate(keysSorted, 1):
        units = keys.get("units") if isinstance(keys, dict) else keys
        print(f"{name}) {units} unit(s)/share(s)")
    # input for the coingeckoid 
    coinGeckoID = input("Enter CoinGecko ID, e.g. bitcoin or exit to return to menu: ").strip()

    #checks for exit input
    if coinGeckoID.lower() == "exit":
        print("Exiting...")
        return
    
    # if a coingecko ID is not entered, cancel and break out of the function.
    if not coinGeckoID:
        print("Canceled")
        return
    # allow numeric selection of crypto by index
    selected_ID = None
    if coinGeckoID.isdigit():
        select = int(coinGeckoID)
        if 1 <= select <= len(keysSorted):
            selected_ID = keysSorted[select - 1]
    # if not a numeric number, normalize to a lowercase coingecko id
    if selected_ID is None:
        selected_ID = coinGeckoID.lower()
    # validate the selection exists
    if selected_ID not in crypto:
        print("Please enter a crypto from a list, entry not found.")
        return
    
    # get current crypto holdings and print the selected crypto with the number of held units
    position = crypto.get(selected_ID, {"units": 0.0, "cost_basis": 0.0})
    current_units = float(position.get("units", 0.0))
    print(f"Current holding for {selected_ID}: {current_units} unit(s).")

    # Get removal amount with exit choice optional
    quantityCrypto = input("Enter number of units to remove or exit to return to menu: ").strip()
    if quantityCrypto.lower() == "exit":
        print("Exiting...")
        return
    try: 
        units_to_remove = float(quantityCrypto)        
    except ValueError:
        print("Invalid Number Entered")
        return
    
    if units_to_remove <= 0:
        print("Enter a positive removal amount.")
        return

    if units_to_remove >= current_units:
        del crypto[selected_ID]
        print(f"Removed {selected_ID}.")
    else:
        old_cost_basis = position.get("cost_basis", 0.0)
        cost_basis_to_remove = (old_cost_basis / current_units) * units_to_remove if current_units > 0 else 0
        
        position["units"] = current_units - units_to_remove
        position["cost_basis"] = max(0.0, old_cost_basis - cost_basis_to_remove)
        crypto[selected_ID] = position
        print(f"Updated {selected_ID}, {position['units']} units remaining.")

    save_data()
    return
#BULLION PRICE
def get_GUI_bullion_prices() -> dict[str, float | None]:
    url = "https://api.gold-api.com"
    symbols = {
        "gold": "XAU",
        "silver": "XAG",
        "palladium": "XPD",
        "copper": "HG",
    }
    if requests is None:
        return {}

    prices: dict[str, float | None] = {}
    for metal, code in symbols.items():
        try:
            response = requests.get(f"{url}/price/{code}", timeout=10)
            response.raise_for_status()
            prices[metal] = float(response.json().get("price"))
        except Exception:
            prices[metal] = None
    return prices
def showBullion(section="totals", quiet=False) -> float:
    if not bullion:
            if not quiet: 
                print("No bullion position(s)")
                return
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
    
    prices = get_GUI_bullion_prices()
    if not prices:
        if not quiet: 
            print("\nBullion prices are unavailable right now...\n")
        return 0.0

    for metal, position_data in bullion.items():
        units = position_data.get("units", 0.0)
        cost_basis = position_data.get("cost_basis", 0.0)
        avg_buy_price = (cost_basis / units) if units > 0 else 0.0
        price = prices.get(metal)

        if price is None:
            if not quiet: print(f"Could not fetch price for {metal} with {units} units.")
            continue

        current_value = units * price
        profit_loss = current_value - cost_basis
        pnl_string = f"P/L: ${profit_loss:,.2f}"
        subtotal += current_value
        if not quiet:
            print(f"\n{metal.capitalize()}: {units} units @ avg buy price of ${avg_buy_price:,.2f}. Total Purchase(s) Cost: ${cost_basis:,.2f}\nCurrent Price: ${price:,.2f}, Current Value: ${current_value:,.2f} | ({pnl_string})")
    return subtotal
def add_bullion_to_positions():
    
    while True: 
        print("Current Bullion Positions: ")
        keysSorted = sorted(bullion.keys())
        for name, keys in enumerate(keysSorted, 1):
            print(f"{keys}")

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
        
        keysSorted = sorted(bullion.keys())
        # for number, name in enumerate(keysSorted, 1):
        #     print(f"{name} : {bullion.get(name, 0.0)} unit(s)")
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

        buy_in_price_input = input("Enter price that you bought the bullion at or type exit to return to menu: ").strip()
        if buy_in_price_input.lower() == "exit":
            print("Exiting...")
            break
        try:
            price_when_purchased = float(buy_in_price_input)
        except ValueError:
            print("Invalid Number Entered")
            continue
        if price_when_purchased <= 0:
            print("Please enter a non-negative number.")
            continue

        bullionKey = bullionGoldORSilver.lower()
        position = bullion.get(bullionKey, {"units": 0.0, "cost_basis": 0.0})
        position["units"] += quantityBullion
        position["cost_basis"] += quantityBullion * price_when_purchased
        bullion[bullionKey] = position
        new_avg_price = (position['cost_basis'] / position['units']) if position['units'] > 0 else 0.0
        print(f"Updated [{bullionKey}], now holding {position['units']} units. New average price is ${new_avg_price:,.2f}/unit.")
        save_data()
        return
def remove_bullion_from_positions():
    if not bullion: 
        print("No bullion position(s)")
        return
    while True: 
        print("Bullion Assets")
        for name, quantity in bullion.items():
            units = quantity.get("units", 0.0) if isinstance(quantity, dict) else float(quantity)
            print(f"{name}: {units} units")
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
        
        position = bullion.get(bullionGoldORSilver, {"units": 0.0, "cost_basis": 0.0})
        current_units = float(position.get("units", 0.0))
        print(f"{bullionGoldORSilver} : {current_units} unit(s)")

        metalOunce = input("Enter number of ounces to remove or type exit to return to menu: ").strip()
        if metalOunce.lower() == "exit":
            print("Exiting...")
            break
        try: 
            metalOunceFloat = float(metalOunce)
        except ValueError:
            print("Invalid Number Entered")
            continue
        if metalOunceFloat <= 0: 
            print("Please enter a non negative number, non zero number.")
            continue
        if metalOunceFloat >= 9_999_999:
            print("Maximum number that can be entered is 9,999,999.")
            continue
        
        if metalOunceFloat >= current_units:
            del bullion[bullionGoldORSilver]
            print(f"Removed {bullionGoldORSilver}.")
        else:
            old_cost_basis = position.get("cost_basis", 0.0)
            cost_basis_to_remove = (old_cost_basis / current_units) * metalOunceFloat if current_units > 0 else 0
            
            position["units"] = current_units - metalOunceFloat
            position["cost_basis"] = max(0.0, old_cost_basis - cost_basis_to_remove)
            bullion[bullionGoldORSilver] = position
            print(f"Updated {bullionGoldORSilver}, {position['units']} units remaining.")

        save_data()
        return
# CASH SHOW
def showCash(section="totals", quiet=False) -> float:
        section = (section or "totals").strip().lower()
        show_cash  = section in ("cash", "5", "totals") 
        if not cash: 
            print("No Cash Position(s)") 
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
        print("Current Cash Positions: ")
        for account, quantity in cash.items():
            print(f"{account}: ${quantity}")
        cashAdd = input("Enter cash account name, e.g. savings account or type exit to return to menu: ").strip()
        if cashAdd == "exit":
            print("Exiting...")
            return
        if not cashAdd:
            print("Canceled")
            return
        if len(cashAdd) > 50:
            print("Length can not be longer than 50 characters.")
            continue
        ask = input("Enter 1) to add dollars/cents or type exit to return to menu: ").strip().lower()
        if ask == "exit":
            print("Exiting...")
            return
        if ask != "1":
            print("Enter 1) to add cash or exit to return to menu.")
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
            cash[cashAdd] = cash.get(cashAdd, 0.0) + max(0.0, quantityOfCash)
            print(f"\nUpdated [{cashAdd}], with ${cash[cashAdd]}")
          #  cash["cash"] = cash.get("cash", 0.0) + quantityOfCash
           # print(f"\nUpdated available cash, with {cash["cash"]:.2f} dollars")
            save_data()
            return
def remove_cash_from_position():
    Max_Removal = 9_999_999_999_999
    while True: 
        if not cash:
            print("No cash position(s)")
            return
        print("\nCurrent Cash Account(s)")
        for cashAccount, quantity in cash.items():
            print(f"{cashAccount}  ${quantity}")
        print("Please enter: \n 1) Lower value of cash account\n 2) Remove account completely\n exit to return to menu")

        inputForDollarCashRemoval = input("Select 1, 2 or exit to return to menu: ").strip()
        if inputForDollarCashRemoval.lower() == "exit":
            print("Exiting...")
            break
        if inputForDollarCashRemoval == "1":
                print("\nItems List")
                for cashAccount in cash.keys():
                    print(cashAccount)
                accountSelection = input("Enter account name to lower dollar amount or exit to return to menu: ").strip()
                if accountSelection == "exit":
                    print("Exiting...")
                    break
                match = next((matches for matches in cash if matches.lower() == accountSelection.lower()), None)
                if not match:
                    print("Please enter an account from the list.")
                    continue
                currentAccount = float(cash.get(match, 0.0))
                print(f"Selection {match}, current value ${currentAccount:,.2f}")
                amount = input("\nEnter [exit] to return to menu.\nEnter an amount to subtract as  whole number with up to two decimal places\n e.g. 10.75, 10, 5.50, etc. ").strip()
                if amount == "exit".strip().lower:
                    print("Exiting...")
                    return
                try: 
                    accountWorth = float(amount)
                except ValueError:
                    print("Invalid number entered.")
                    continue

                if accountWorth <= 0:
                    print("Please enter a positive number larger than 0.")
                    continue
                if accountWorth > Max_Removal:
                    print(f"Please enter a number less than {Max_Removal}.")
                    continue
                
                if accountWorth >= currentAccount:
                    confirmation = input(f"Requested removal of ${accountWorth:,.2f}, that amount exceeds current account value of ${currentAccount:,.2f}. Remove entire account (y/n): ").strip().lower()
                    if confirmation == "y":
                        del cash[match]
                        print(f"Removed {match} from accounts")
                        save_data()
                        return
                    else:
                        print("Operation Cancelled.")
                        continue

                # subtraction code
                oldBalance = currentAccount
                cash[match] = max(0.0, oldBalance - accountWorth)
                print(f"{match}: \nOld account value ${oldBalance:,.2f} \nNew account value ${cash[match]:,.2f}")
                save_data()
                return
        elif inputForDollarCashRemoval == "2": 
                for name in cash.keys():
                    print(f"{name}")
                #remove item completely
                cashAccountRemoval = input("Enter an account name to remove or exit to return to menu: ").strip()
                if cashAccountRemoval == "exit":
                    print("Exiting...")
                    break
                matchItemRemoval = next((matches for matches in cash if matches.lower() == cashAccountRemoval.lower()), None)
                if not matchItemRemoval:
                    print("Item not found.")
                    continue

                confirmationRemoval = input(f"Are you sure you want to remove {matchItemRemoval} from accounts? (y/n): ").strip().lower()
                if confirmationRemoval == "y": 
                    del cash[matchItemRemoval]
                    print(f"\nRemoved {matchItemRemoval} from accounts")
                    save_data()
                    return
                else: 
                    print("Item Not Found")
                    continue
        else:
                print("Please enter a valid choice of 1, 2 or exit to return to menu.")
                continue
        
    
    # ITEMS SHOW
def showItems(section="totals", quiet=False) -> float:
        section = (section or "totals").strip().lower()
        show_items  = section in ("items", "4", "totals")  
        if not show_items:
            return 0.0
        if not items:
            print("No item position(s)")
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
    Max_Removal = 9_999_999_999
    while True: 
        print("\nCurrent Item(s)")
        for itemLoop, value in items.items():
            print(f"{itemLoop}  ${value}")
        print("\n")
        print("Please enter: \n 1) Lower value of item\n 2) Remove item completely\n exit to return to menu")

        inputForDollarAmountRemoval = input("Select 1, 2 or exit to return to menu: ").strip()
        if inputForDollarAmountRemoval == "exit":
            print("Exiting...")
            break
        if inputForDollarAmountRemoval == "1":
            print("\nItems List")
            for itemLoop in items.keys():
                print(itemLoop)
            itemSelection = input("Enter item name to lower dollar amount or exit to return to menu: ").strip()
            if itemSelection == "exit":
                print("Exiting...")
                break
            match = next((matches for matches in items if matches.lower() == itemSelection.lower()), None)
            if not match:
                print("Please enter an item from the list.")
                continue
            currentItem = float(items.get(match, 0.0))
            print(f"Selection {match}, current value ${currentItem:,.2f}")
            amount = input("\nEnter [exit] to return to menu.\nEnter an amount to subtract as  whole number with up to two decimal places\n e.g. 10.75, 10, 5.50, etc. ").strip()
            if amount == "exit".strip().lower:
                print("Exiting...")
                return
            try: 
                amountWorth = float(amount)
            except ValueError:
                print("Invalid number entered.")
                continue

            if amountWorth <= 0:
                print("Please enter a positive number larger than 0.")
                continue
            if amountWorth > Max_Removal:
                print(f"Please enter a number less than {Max_Removal}.")
                continue
            
            if amountWorth >= currentItem:
                confirmation = input(f"Requested removal of ${amountWorth:,.2f}, that amount exceeds current item value of ${currentItem:,.2f}. Remove entire item (y/n): ").strip().lower()
                if confirmation == "y":
                    del items[match]
                    print(f"Removed {match} from items")
                    save_data()
                    return
                else:
                    print("Operation Cancelled.")
                    continue

            # subtraction code
            oldBalance = currentItem
            items[match] = max(0.0, oldBalance - amountWorth)
            print(f"{match}: \nOld item price ${oldBalance:,.2f} \nNew item price ${items[match]:,.2f}")
            save_data()
            return
        elif inputForDollarAmountRemoval == "2": 
            for name in items.keys():
                print(f"{name}")
            #remove item completely
            itemRemoval = input("Enter an item name to remove or exit to return to menu: ").strip()
            if itemRemoval == "exit":
                print("Exiting...")
                break
            matchItemRemoval = next((matches for matches in items if matches.lower() == itemRemoval.lower()), None)
            if not matchItemRemoval:
                print("Item not found.")
                continue

            confirmationRemoval = input(f"Are you sure you want to remove {matchItemRemoval} from items? (y/n): ").strip().lower()
            if confirmationRemoval == "y": 
                del items[matchItemRemoval]
                print(f"\nRemoved {matchItemRemoval} from items")
                save_data()
                return
            else: 
                print("Item Not Found")
                continue
        else:
            print("Please enter a valid choice of 1, 2 or exit to return to menu.")
            continue
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
                if debtAddition <= 0:
                    print("Please enter a positive number larger than 0.")
                    continue
                if debtAddition > 9_999_999_999:
                    print("The maximum number that can be entered is 9,999,999,999.")
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
             for name, value in debt.items():
                 print(f"{name} : {value}")
             print("Type [exit] and press enter to return to the menu.")
             removeAmount = input("Enter the account name to subtract debt from: ").strip()
             match = next((matches for matches in debt if matches.lower() == removeAmount.lower()), None)
             if removeAmount == "exit":
                print("Exiting...")
                continue
             if not match:
                print("Account Not Found")
                continue
             amount = input("Enter an amount to subtract as a whole number with up to two decimal places \nType exit and press enter, to return to menu: ").strip()
             if amount == "exit":
                print("Exiting...")
                continue    
             try: 
                amountCheck = float(amount)
             except ValueError:
                 print("Invalid Number, please enter something valid")
                 continue
             if amountCheck <= 0:
                print("Please enter a positive or non zero number")
                continue
             if amountCheck > 9_999_999_999:
                print("The maximum number that can be entered is 9,999,999,999.")
                continue
             helperCall = safe_subtract_and_maybe_delete(debt, match, amountCheck)
             if helperCall:
                save_data()
                continue
             else: 
                print("No changes made.")
                continue
        elif debtInput == "4":
            if not debt:
                print("No debt accounts found")
                break
            print("\nType [exit] and press enter to return to the menu.")
            name = input("Enter the name of the debt account to remove: ").strip()
            if name.lower() == "exit":
                print("Exiting...")
                return
            matches = next((match for match in debt if match.lower() == name.lower()), None)
            if matches:
                del debt[matches]
                print(f"Removed {matches} from debts")
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
def chatBotMoneyAssistant():
    if not ask_ai:
        print("AI assistant not available.")
    else:
        print("\n Entering AI Chatbot type exit and press enter, to return to menu.")
        while True:
            question = input("Ask A Question or type exit and press enter to return to menu: ").strip()
            if question.lower() == "exit":
                print("Exiting...")
                break

            # Prepare data with prices for the AI
            priced_stocks = {}
            for ticker, quantity in Stocks.items():
                price = getPrice(ticker)
                priced_stocks[ticker] = {"quantity": quantity, "last_price": price or 0.0}

            priced_crypto = {}
            if crypto:
                prices = getGUICryptoPrices(list(crypto.keys()), quiet=True)
                for cid, quantity in crypto.items():
                    priced_crypto[cid] = {"quantity": quantity, "last_price": prices.get(cid, 0.0)}

            priced_bullion = {}
            if bullion:
                prices = get_GUI_bullion_prices()
                for metal, quantity in bullion.items():
                    priced_bullion[metal] = {"quantity": quantity, "last_price": prices.get(metal) or 0.0}

            answer = ask_ai(
                question, stocks=priced_stocks, crypto=priced_crypto, 
                bullion=priced_bullion, cash=cash, items=items, debt=debt
            )
            print(f"AI Answer: \n{answer}")

def budgeting():
    global budget
   
    while True:
        
        print("\nWelcome to Budgeting")
        
        initial_input = input("Type and press enter \n1) Show Budget \n2) Add Budget \n3) Lower Budget \n4) Spending Tracker \n5) Show Spending \n6) Over or Under Budget \n7) to return to menu: ").strip()
        if initial_input == "7":
            print("Exiting...")
            break
        if initial_input == "1":
            if not budget:
                print("No budget recorded")
                continue
            if budget: 
                print(f"Budget : ${budget["total"]:,.2f}")
                continue

        elif initial_input == "2":
            budgetInput = input("Type the value and press enter for the amount you would like to add to the budget or exit to return to menu: ")
            if budgetInput == "exit":
                print("Exiting...")
                continue
            try: 
                budgetFloat = float(budgetInput)
            except ValueError:
                print("Invalid Number")
                continue

            budget["total"] += budgetFloat
            print(f"Budget added ${budgetFloat:,.2f}, current budget total is ${budget["total"]:,.2f}")
            save_data()


        elif initial_input == "3":
            # lower budget here
            print("How much would you like to subtract?")
            budgetSubtract = input("Type budget amount and press enter to subtract or exit to return to menu: ")
            if budgetSubtract == "exit":
                print("Exiting...")
                continue
            try: 
                budgetSubtractFloat = float(budgetSubtract)
            except ValueError:
                print("Invalid Number")
                continue
            budget["total"] -= budgetSubtractFloat
            print(f"Budget updated with ${budgetSubtractFloat:,.2f}, budget total now is ${budget["total"]:,.2f}")
            save_data()

        if initial_input == "4":
            while True: 
                print("\nSpending Tracker")
                secondInput = input("Type and press enter: \n1) Food \n2) Entertainment \n3) Housing \n4) Utilities \n5) Clothing \n6) Clear Spending\n7) to return to menu: ").strip()
                if secondInput == "1":
                    print("Food Selected")
                    while True: 
                        print(f"food spending: ${budget["food"]:,.2f}")
                        questionInput = input("1) Add Food Budget\n2) Lower/Remove Food Budget\n3) Exit\n")
                        if questionInput == "1":
                            addfoodInput = input("Type the food budget and press enter or exit to return to menu: ")
                            try:
                                foodFloat = float(addfoodInput)
                            except ValueError:
                                print("Invalid Number")
                                continue
                            budget["food"] += foodFloat
                            save_data()
                        if questionInput == "2":
                            print(f"food spending: ${budget["food"]:,.2f}")
                            subtractFoodInput = input("Type the food budget to lower/remove and press enter or exit to return to menu: ")
                            if subtractFoodInput == "exit":
                                print("Exiting...")
                                return
                            try: 
                                subtractFoodFloat = float(subtractFoodInput)
                            except ValueError:
                                print("Invalid Number")
                                continue
                            budget["food"] -= subtractFoodFloat
                            save_data()
                        if questionInput == "3":
                            print("Exiting...")
                            break
                if secondInput == "2":
                    print("Entertainment Selected")
                    while True: 
                        print(f"entertainment spending: ${budget["entertainment"]:,.2f}")
                        questionInput = input("1) Add Entertainment Budget\n2) Lower/Remove Entertainment Budget\n3) Exit\n")
                        if questionInput == "1":
                            addEntertainmentInput = input("Type the Entertainment budget and press enter or exit to return to menu: ")
                            try:
                                entertainmentFloat = float(addEntertainmentInput)
                            except ValueError:
                                print("Invalid Number")
                                continue
                            budget["entertainment"] += entertainmentFloat
                            save_data()
                        if questionInput == "2":
                            print(f"entertainment spending: ${budget["entertainment"]:,.2f}")
                            subtractEntertainmentInput = input("Type the Entertainment budget to lower/remove and press enter or exit to return to menu: ")
                            if subtractEntertainmentInput == "exit":
                                print("Exiting...")
                                return
                            try: 
                                subtractEntertainmentFloat = float(subtractEntertainmentInput)
                            except ValueError:
                                print("Invalid Number")
                                continue
                            budget["entertainment"] -= subtractEntertainmentFloat 
                            save_data()
                        if questionInput == "3":
                            print("Exiting...")
                            break
                if secondInput == "3":
                    print("Housing Selected")
                    while True: 
                        print(f"housing spending: ${budget["housing"]:,.2f}")
                        questionInput = input("1) Add Housing Budget\n2) Lower/Remove Housing Budget\n3) Exit\n")
                        if questionInput == "1":
                            addHousingInput = input("Type the housing budget and press enter or exit to return to menu: ")
                            try:
                                housingFloat = float(addHousingInput)
                            except ValueError:
                                print("Invalid Number")
                                continue
                            budget["housing"] += housingFloat
                            save_data()
                        if questionInput == "2":
                            print(f"housing spending: ${budget["housing"]:,.2f}")
                            subtractHousingInput = input("Type the housing budget to lower/remove and press enter or exit to return to menu: ")
                            if subtractHousingInput == "exit":
                                print("Exiting...")
                                return
                            try: 
                                subtractHousingFloat = float(subtractHousingInput)
                            except ValueError:
                                print("Invalid Number")
                                continue
                            budget["housing"] -= subtractHousingFloat 
                            save_data()
                        if questionInput == "3":
                            print("Exiting...")
                            break
                if secondInput == "4":
                    print("Utilities Selected")
                    while True: 
                        print(f"utilities spending: ${budget["utilities"]:,.2f}")
                        questionInput = input("1) Add Utilities Budget\n2) Lower/Remove Food Budget\n3) Exit\n")
                        if questionInput == "1":
                            addUtilitiesInput = input("Type the utilities budget and press enter or exit to return to menu: ")
                            try:
                                utilitiesFloat = float(addUtilitiesInput)
                            except ValueError:
                                print("Invalid Number")
                                continue
                            budget["utilities"] += utilitiesFloat
                            save_data()
                        if questionInput == "2":
                            print(f"utilities spending: ${budget["utilities"]:,.2f}")
                            subtractUtilitiesInput = input("Type the utilities budget to lower/remove and press enter or exit to return to menu: ")
                            if subtractUtilitiesInput == "exit":
                                print("Exiting...")
                                return
                            try: 
                                subtractUtilitiesFloat = float(subtractUtilitiesInput)
                            except ValueError:
                                print("Invalid Number")
                                continue
                            budget["utilities"] -= subtractUtilitiesFloat
                            save_data()
                        if questionInput == "3":
                            print("Exiting...")
                            break
                if secondInput == "5":
                    print("Clothing Selected")
                    while True: 
                        print(f"clothing spending: ${budget["clothing"]:,.2f}")
                        questionInput = input("1) Add Clothing Budget\n2) Lower/Remove Food Budget\n3) Exit\n")
                        if questionInput == "1":
                            addClothingInput = input("Type the clothing budget and press enter or exit to return to menu: ")
                            try:
                                clothingFloat = float(addClothingInput)
                            except ValueError:
                                print("Invalid Number")
                                continue
                            budget["clothing"] += clothingFloat
                            save_data()
                        if questionInput == "2":
                            print(f"clothing spending: ${budget["clothing"]:,.2f}")
                            subtractClothingInput = input("Type the clothing budget to lower/remove and press enter or exit to return to menu: ")
                            if subtractClothingInput == "exit":
                                print("Exiting...")
                                return
                            try: 
                                subtractClothingFloat = float(subtractClothingInput)
                            except ValueError:
                                print("Invalid Number")
                                continue
                            budget["clothing"] -= subtractClothingFloat
                            save_data()
                        if questionInput == "3":
                            print("Exiting...")
                            break
                if secondInput == "6":
                    budget == 0.0
                    save_data()
                if secondInput == "7":
                    print("Exiting...")
                    break
        if initial_input == "5":
            totalSpending = budget["clothing"] + budget["entertainment"] + budget["food"] + budget["housing"] + budget["utilities"]
            clothing = budget["clothing"]
            entertainment = budget["entertainment"]
            food = budget["food"]
            housing = budget["housing"]
            utilities = budget["utilities"]
            print(f"Total Spending: ${totalSpending:,.2f}\nClothing: ${clothing:,.2f}\nEntertainment: ${entertainment:,.2f}\nFood: ${food:,.2f}\nHousing: ${housing:,.2f}\nUtilities: ${utilities:,.2f}")

        if initial_input == "6":
            totalSpending = budget["clothing"] + budget["entertainment"] + budget["food"] + budget["housing"] + budget["utilities"]
            budgetTotal = budget["total"]
            print("Over or Under Budget")
            while True:
                if totalSpending > budgetTotal:
                    print("Over Budget")
                elif totalSpending < budgetTotal:
                    print("Under Budget")
                else: 
                    print("On Budget")
                break
        
    
# MAIN MENU
def _main_menu_():
    while True: 
        print("\nWelcome to the Asset, Debt and Budget Tracker")
        print("1) positions")
        print("2) debt")
        print("3) AI Chat (AI SLOP)")
        print("4) Budgeting")
        print("5) Exit")
        choice = input("Enter a choice of 1, 2, 3, 4 or 5: ")
        if choice == "1":
            while True: 
                print("\nPositions")
                print("  1) Stocks")
                print("  2) Crypto")
                print("  3) Bullion")
                print("  4) Cash ")
                print("  5) Items")
                print("  6) Totals")
                print("  7) Add/Update Position")
                print("  8) Remove/Delete Position")
                print("  9) Exit")
                entry = input("Choose 1/2/3/4/5/6/7/8 or 9: ").strip().lower()
                section = {"1": "stocks", "2": "crypto", "3": "bullion", "6": "totals", "4": "cash", "5": "items", "7": "add", "8": "remove", "9": "exit"}
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
                elif section in ("6", "totals"):
                    print("\n Totals:  ")
                    stockTotal = parse_positions(section="stocks", quiet=True) or 0.0
                    print(f"\nStock Dollar Total: \n ${stockTotal:,.2f}")
                    cryptoTotal = showCrypto(section="crypto", quiet=True) or 0.0
                    print(f"\nCrypto Dollar Total: \n ${cryptoTotal:,.2f}")
                    bullionTotal = showBullion(section="bullion", quiet=True) or 0.0
                    print(f"\nBullion Dollar Total: \n ${bullionTotal:,.2f}")
                    print("\nCash Dollar Total: ")
                    total = 0.0
                    if isinstance(cash, dict):
                        for name, amount in cash.items():
                            try: 
                                amount += float(amount)
                            except (TypeError, ValueError):
                                continue
                    if total <= 0.0:
                        pass
                        #print("Cash available is $0")
                    else: 
                        print(f"{total:,.2f}")
                    print(f" ${total:,.2f}")
                    print("\nItem(s) Dollar Total: ")
                    cashTotal = sum(cash.values())
                    itemTotal = sum(items.values())
                    print(f" ${itemTotal}")
                    StockCryptoBullionTotals = stockTotal + cryptoTotal + bullionTotal
                    print(f"\nStock, Cryptocurrency and Bullion Totals: \n ${StockCryptoBullionTotals:,.2f}")
                    StockCryptoBullionCashTotals = StockCryptoBullionTotals + cashTotal
                    print(f"\nStock, Cryptocurreny, Bullion and Cash Totals \n ${StockCryptoBullionCashTotals:,.2f}")
                    GrandTotals = stockTotal + cryptoTotal + bullionTotal + cashTotal + itemTotal
                    print(f"\nGrand Total of Stock, Cryptocurrency, Bullion, Cash and Item(s): \n ${GrandTotals:,.2f}")
                    debtTotal = sum(debt.values())
                    AssetSubtractionMinusItems = StockCryptoBullionCashTotals - debtTotal
                    print(f"\nTotals for Stock, Cryptocurrency, Bullion, Cash minus the debt accounts \n ${AssetSubtractionMinusItems:,.2f}")
                    TotalAssetSubtraction = GrandTotals - debtTotal
                    print(f"\nTotals after Stock, Cryptocurrency, Bullion, Cash and Item(s) minus the debt accounts \n ${TotalAssetSubtraction:,.2f}")
                    print("\n")
                elif section in ("4", "cash"):
                    print("\nCash")
                    showCash(section="cash", quiet=False)
                elif section in ("5", "items"):
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
            chatBotMoneyAssistant()
        elif choice == "4":
            budgeting()
        elif choice == "5":
            print("Exiting...")
            break
if __name__ == "__main__":
    load_data()
    _main_menu_() 
    