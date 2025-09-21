import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Any, Dict
from financial import (
    load_data,
    save_data,
    getPrice,
    getGUICryptoPrices,
    get_GUI_bullion_prices,
    showCash,
    showItems,
    is_valid_ticker,
    is_valid_coingeckoid,
    Stocks,
    crypto,
    bullion,
    cash,
    items,
    debt,
    yfinance,
    CoinGeckoAPI,
    safe_subtract_and_maybe_delete,
    ask_ai, 

)

# --- GUI Application ---

class AssetTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Asset, Debt and Budget Tracker")
        self.geometry("900x450")

        load_data()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        self.stocks_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stocks_frame, text="Stocks")

        # Add placeholder tabs
        
        self.crypto_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.crypto_frame, text="Crypto")

        self.bullion_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.bullion_frame, text="Bullion")

        self.cash_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cash_frame, text="Cash")
        
        self.items_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.items_frame, text="Item(s)")
        
        self.debt_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.debt_frame, text="Debt")

        self.budget_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.budget_frame, text="Budget")
        
        #self.ai_frame = ttk.Frame(self.notebook)
        #self.notebook.add(self.ai_frame, text="AI Chat")


        self.create_stocks_tab()
        self.create_crypto_tab()
        self.create_bullion_tab()
        self.create_cash_tab()
        self.create_item_tab()
        self.create_debt_tab()
        #self.create_ai_tab()




    def create_stocks_tab(self):
        controls_frame = ttk.LabelFrame(self.stocks_frame, text="Manage Stocks")
        controls_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(controls_frame, text="Ticker:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.stock_ticker_entry = ttk.Entry(controls_frame)
        self.stock_ticker_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(controls_frame, text="Quantity:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.stock_quantity_entry = ttk.Entry(controls_frame)
        self.stock_quantity_entry.grid(row=0, column=3, padx=5, pady=5)

        add_button = ttk.Button(controls_frame, text="Add Stock", command=self.add_stock)
        add_button.grid(row=0, column=4, padx=10, pady=5)

        self.stocks_tree = ttk.Treeview(self.stocks_frame, columns=("Ticker", "Quantity", "Price", "Value"), show="headings")
        self.stocks_tree.heading("Ticker", text="Ticker")
        self.stocks_tree.heading("Quantity", text="Quantity")
        self.stocks_tree.heading("Price", text="Price")
        self.stocks_tree.heading("Value", text="Value")
        self.stocks_tree.pack(fill="both", expand=True, padx=10, pady=5)

        tree_buttons_frame = ttk.Frame(self.stocks_frame)
        tree_buttons_frame.pack(fill="x", padx=10, pady=5)

        refresh_button = ttk.Button(tree_buttons_frame, text="Refresh Prices", command=self.refresh_stocks)
        refresh_button.pack(side="left", padx=5)
        if yfinance is None:
            refresh_button.config(state="disabled")

        remove_button = ttk.Button(tree_buttons_frame, text="Remove Selected", command=self.remove_stock)
        remove_button.pack(side="left", padx=5)

        self.refresh_stocks()

    def refresh_stocks(self):
        for item in self.stocks_tree.get_children():
            self.stocks_tree.delete(item)

        for ticker, quantity in sorted(Stocks.items()):
            price = getPrice(ticker)
            if price is not None:
                value = quantity * price
                self.stocks_tree.insert("", "end", values=(ticker, f"{quantity:.4f}", f"${price:,.2f}", f"${value:,.2f}"))
            else:
                self.stocks_tree.insert("", "end", values=(ticker, f"{quantity:.4f}", "N/A", "N/A"))

    def add_stock(self):
        ticker = self.stock_ticker_entry.get().strip().upper()
        quantity_str = self.stock_quantity_entry.get().strip()

        if not is_valid_ticker(ticker):
            messagebox.showerror("Error", "Invalid ticker format. Use letters only.")
            return

        try:
            quantity = float(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be positive.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid quantity: {e}")
            return

        Stocks[ticker] = Stocks.get(ticker, 0.0) + quantity
        save_data()
        messagebox.showinfo("Success", f"Added {quantity} shares of {ticker}.")

        self.stock_ticker_entry.delete(0, "end")
        self.stock_quantity_entry.delete(0, "end")
        self.refresh_stocks()

    def remove_stock(self):
        selected_item = self.stocks_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a stock to remove.")
            return

        ticker = self.stocks_tree.item(selected_item[0])['values'][0]
        current_quantity = Stocks.get(ticker, 0.0)

        quantity_to_remove_str = simpledialog.askstring("Remove Stock", f"How many shares of {ticker} to remove?\nCurrent holding: {current_quantity}\n(Leave blank to remove all)")

        if quantity_to_remove_str is None:
            return

        if quantity_to_remove_str.strip() == "":
            if messagebox.askyesno("Confirm", f"Are you sure you want to remove all shares of {ticker}?"):
                del Stocks[ticker]
                save_data()
                self.refresh_stocks()
        else:
            try:
                quantity_to_remove = float(quantity_to_remove_str)
                if quantity_to_remove <= 0:
                    raise ValueError("Quantity must be positive.")
                if quantity_to_remove > current_quantity:
                    messagebox.showerror("Error", f"Cannot remove {quantity_to_remove} shares. You only have {current_quantity}.")
                    return
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid quantity: {e}")
                return

            new_quantity = current_quantity - quantity_to_remove
            if new_quantity < 1e-9:
                del Stocks[ticker]
            else:
                Stocks[ticker] = new_quantity

            save_data()
            self.refresh_stocks()

    def create_crypto_tab(self):
        controls_frame = ttk.LabelFrame(self.crypto_frame, text="Manage Crypto")
        controls_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(controls_frame, text="CoinGecko ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.crypto_id_entry = ttk.Entry(controls_frame)
        self.crypto_id_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(controls_frame, text="Quantity:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.crypto_quantity_entry = ttk.Entry(controls_frame)
        self.crypto_quantity_entry.grid(row=0, column=3, padx=5, pady=5)

        add_button = ttk.Button(controls_frame, text="Add Crypto", command=self.add_crypto)
        add_button.grid(row=0, column=4, padx=10, pady=5)

        self.crypto_tree = ttk.Treeview(self.crypto_frame, columns=("Name", "Quantity", "Price", "Value"), show="headings")
        self.crypto_tree.heading("Name", text="Crypto Name")
        self.crypto_tree.heading("Quantity", text="Quantity")
        self.crypto_tree.heading("Price", text="Price")
        self.crypto_tree.heading("Value", text="Value")
        self.crypto_tree.pack(fill="both", expand=True, padx=10, pady=5)

        tree_buttons_frame = ttk.Frame(self.crypto_frame)
        tree_buttons_frame.pack(fill="x", padx=10, pady=5)

        refresh_button = ttk.Button(tree_buttons_frame, text="Refresh Prices", command=self.refresh_crypto)
        refresh_button.pack(side="left", padx=5)
        if CoinGeckoAPI is None:
            refresh_button.config(state="disabled")

        remove_button = ttk.Button(tree_buttons_frame, text="Remove Selected", command=self.remove_crypto)
        remove_button.pack(side="left", padx=5)

        self.refresh_crypto()

    def refresh_crypto(self):
        for item in self.crypto_tree.get_children():
            self.crypto_tree.delete(item)

        if not crypto:
            return
        crypto_ids = list(crypto.keys())
        prices = getGUICryptoPrices(crypto_ids, quiet=True)

        for coinGeckoPrice, quantity in sorted(crypto.items()):
            price = prices.get(coinGeckoPrice)
            if price is not None:
                value = quantity * price
                self.crypto_tree.insert("", "end", values=(coinGeckoPrice, f"{quantity:,.4f}", f"${price:,.2f}", f"${value:,.2f}"))
            else:
                self.crypto_tree.insert("", "end", values=(coinGeckoPrice, f"{quantity:.4f}", "N/A", "N/A"))

        

    def add_crypto(self):
        cryptoName = self.crypto_id_entry.get().strip().lower()
        quantity_str = self.crypto_quantity_entry.get().strip()

        if not is_valid_coingeckoid(cryptoName):
            messagebox.showerror("Error", "Invalid Crypto format. Use coingecko IDs only.")
            return

        try:
            quantity = float(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be positive.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid quantity: {e}")
            return

        crypto[cryptoName] = crypto.get(cryptoName, 0.0) + quantity
        save_data()
        messagebox.showinfo("Success", f"Added {quantity} shares of {cryptoName}.")

        self.crypto_id_entry.delete(0, "end")
        self.crypto_quantity_entry.delete(0, "end")
        self.refresh_crypto()

    def remove_crypto(self):
        selected_item = self.crypto_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a cryptocurrency to remove.")
            return

        cryptoID = self.crypto_tree.item(selected_item[0])['values'][0]
        current_quantity = crypto.get(cryptoID, 0.0)

        quantity_to_remove_str = simpledialog.askstring("Remove Cryptocurrency", f"How many shares of {cryptoID} to remove?\nCurrent holding: {current_quantity}\n(Leave blank to remove all)")

        if quantity_to_remove_str is None:
            return

        if quantity_to_remove_str.strip() == "":
            if messagebox.askyesno("Confirm", f"Are you sure you want to remove all shares of {cryptoID}?"):
                del crypto[cryptoID]
                save_data()
                self.refresh_crypto()
        else:
            try:
                quantity_to_remove = float(quantity_to_remove_str)
                if quantity_to_remove <= 0:
                    raise ValueError("Quantity must be positive.")
                if quantity_to_remove > current_quantity:
                    messagebox.showerror("Error", f"Cannot remove {quantity_to_remove} units. You only have {current_quantity}.")
                    return
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid quantity: {e}")
                return

            new_quantity = current_quantity - quantity_to_remove
            if new_quantity < 1e-9:
                del crypto[cryptoID]
            else:
                crypto[cryptoID] = new_quantity

            save_data()
            self.refresh_crypto()


    def create_bullion_tab(self):
        controls_frame = ttk.LabelFrame(self.bullion_frame, text="Manage Bullion |  usable bullions are [gold|silver|palladium|copper]:")
        controls_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(controls_frame, text="Bullion: ").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.bullion_name_entry = ttk.Entry(controls_frame)
        self.bullion_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(controls_frame, text="Quantity:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.bullion_quantity_entry = ttk.Entry(controls_frame)
        self.bullion_quantity_entry.grid(row=0, column=3, padx=5, pady=5)

        add_button = ttk.Button(controls_frame, text="Add Bullion", command=self.add_bullion)
        add_button.grid(row=0, column=4, padx=10, pady=5)

        self.bullion_tree = ttk.Treeview(self.bullion_frame, columns=("Name", "Quantity", "Price", "Value"), show="headings")
        self.bullion_tree.heading("Name", text="Bullion Name")
        self.bullion_tree.heading("Quantity", text="Quantity")
        self.bullion_tree.heading("Price", text="Price")
        self.bullion_tree.heading("Value", text="Value")
        self.bullion_tree.pack(fill="both", expand=True, padx=10, pady=5)

        tree_buttons_frame = ttk.Frame(self.bullion_frame)
        tree_buttons_frame.pack(fill="x", padx=10, pady=5)

        refresh_button = ttk.Button(tree_buttons_frame, text="Refresh Prices", command=self.refresh_bullion)
        refresh_button.pack(side="left", padx=5)
        if bullion is None:
            refresh_button.config(state="disabled")

        remove_button = ttk.Button(tree_buttons_frame, text="Remove Selected", command=self.remove_bullion)
        remove_button.pack(side="left", padx=5)

        self.refresh_bullion()

    def refresh_bullion(self):
        for item in self.bullion_tree.get_children():
            self.bullion_tree.delete(item)

        if not bullion:
            return
       # bullion_name = list(bullion.keys())
        prices = get_GUI_bullion_prices()

        for bullionName, quantity in sorted(bullion.items()):
            price = prices.get(bullionName)
            if price is not None:
                value = quantity * price
                self.bullion_tree.insert("", "end", values=(bullionName, f"{quantity:,.4f}", f"${price:,.2f}", f"${value:,.2f}"))
            else:
                self.bullion_tree.insert("", "end", values=(bullionName, f"{quantity:.4f}", "N/A", "N/A"))

    def add_bullion(self):
        bullionName = self.bullion_name_entry.get().strip().lower()
        quantity_str = self.bullion_quantity_entry.get().strip()
        try:
            quantity = float(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be positive.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid quantity: {e}")
            return

        bullion[bullionName] = bullion.get(bullionName, 0.0) + quantity
        save_data()
        messagebox.showinfo("Success", f"Added {quantity} shares of {bullionName}.")

        self.bullion_name_entry.delete(0, "end")
        self.bullion_quantity_entry.delete(0, "end")
        self.refresh_bullion()

    def remove_bullion(self):
        selected_item = self.bullion_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a bullion to remove.")
            return

        bullionType = self.bullion_tree.item(selected_item[0])['values'][0]
        current_quantity = bullion.get(bullionType, 0.0)

        quantity_to_remove_str = simpledialog.askstring("Remove Bullion", f"How many oz of {bullionType} to remove?\nCurrent holding: {current_quantity}\n(Leave blank to remove all)")

        if quantity_to_remove_str is None:
            return

        if quantity_to_remove_str.strip() == "":
            if messagebox.askyesno("Confirm", f"Are you sure you want to remove all shares of {bullionType}?"):
                del bullion[bullionType]
                save_data()
                self.refresh_bullion()
        else:
            try:
                quantity_to_remove = float(quantity_to_remove_str)
                if quantity_to_remove <= 0:
                    raise ValueError("Quantity must be positive.")
                if quantity_to_remove > current_quantity:
                    messagebox.showerror("Error", f"Cannot remove {quantity_to_remove} units. You only have {current_quantity}.")
                    return
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid quantity: {e}")
                return

            new_quantity = current_quantity - quantity_to_remove
            if new_quantity < 1e-9:
                del bullion[bullionType]
            else:
                bullion[bullionType] = new_quantity

            save_data()
            self.refresh_bullion()


    def create_cash_tab(self):
        controls_frame = ttk.LabelFrame(self.cash_frame, text="Manage Cash:")
        controls_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(controls_frame, text="Account: ").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.cash_name_entry = ttk.Entry(controls_frame)
        self.cash_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(controls_frame, text="Quantity:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.cash_quantity_entry = ttk.Entry(controls_frame)
        self.cash_quantity_entry.grid(row=0, column=3, padx=5, pady=5)

        add_button = ttk.Button(controls_frame, text="Add Cash", command=self.add_cash)
        add_button.grid(row=0, column=4, padx=10, pady=5)

        self.cash_tree = ttk.Treeview(self.cash_frame, columns=("Account", "Value"), show="headings")
        self.cash_tree.heading("Account", text="Account")
        self.cash_tree.heading("Value", text="Value")
        self.cash_tree.pack(fill="both", expand=True, padx=7, pady=5)

        tree_buttons_frame = ttk.Frame(self.cash_frame)
        tree_buttons_frame.pack(fill="x", padx=10, pady=5)


        remove_button = ttk.Button(tree_buttons_frame, text="Remove Selected", command=self.remove_cash)
        remove_button.pack(side="left", padx=5)

        self.refresh_cash()

    def refresh_cash(self):
        for item in self.cash_tree.get_children():
            self.cash_tree.delete(item)
        if not cash:
            return
        total = sum(float(v) for v in cash.values())
        for account_key, balance in sorted(cash.items()):
            self.cash_tree.insert("", "end", values=(account_key, f"${balance:,.2f}"))

        
    def add_cash(self):
        quantity_str = self.cash_quantity_entry.get().strip()
        account_name = self.cash_name_entry.get().strip()
        if not account_name:
            messagebox.showerror("Error", "Please enter an account name.")
            return
        try:
            quantity = float(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be positive.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid quantity: {e}")
            return
        cash[account_name] = cash.get(account_name, 0.0) + quantity
        save_data()
        messagebox.showinfo("Success", f"Added ${quantity:,.2f} to {account_name}. \nNew cash balance for {account_name}: ${cash[account_name]:,.2f}")
        self.cash_quantity_entry.delete(0, "end")
        self.cash_name_entry.delete(0, "end")
        self.refresh_cash()



    def remove_cash(self):
        selected_item = self.cash_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a cash account to remove.")
            return

        cashAccount = self.cash_tree.item(selected_item[0])['values'][0]
        current_quantity = cash.get(cashAccount, 0.0)

        quantity_to_remove_str = simpledialog.askstring("Remove Cash Account", f"How many dollar(s)/cent(s) of {cashAccount} to remove?\nCurrent holding: {current_quantity}\n(Leave blank to remove all)")

        if quantity_to_remove_str is None:
            return

        if quantity_to_remove_str.strip() == "":
            if messagebox.askyesno("Confirm", f"Are you sure you want to remove all cash of {cashAccount}?"):
                del cash[cashAccount]
                save_data()
                self.refresh_cash()
        else:
            try:
                quantity_to_remove = float(quantity_to_remove_str)
                if quantity_to_remove <= 0:
                    raise ValueError("Quantity must be positive.")
                if quantity_to_remove > current_quantity:
                    messagebox.showerror("Error", f"Cannot remove {quantity_to_remove} units. You only have {current_quantity}.")
                    return
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid quantity: {e}")
                return

            new_quantity = current_quantity - quantity_to_remove
            if new_quantity < 1e-9:
                del cash[cashAccount]
            else:
                cash[cashAccount] = new_quantity

            save_data()
            self.refresh_cash()



    def create_item_tab(self):
        controls_frame = ttk.LabelFrame(self.items_frame, text="Manage Item(s):")
        controls_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(controls_frame, text="Item(s): ").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.item_name_entry = ttk.Entry(controls_frame)
        self.item_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(controls_frame, text="Quantity:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.item_quantity_entry = ttk.Entry(controls_frame)
        self.item_quantity_entry.grid(row=0, column=3, padx=5, pady=5)

        add_button = ttk.Button(controls_frame, text="Add Item", command=self.add_item)
        add_button.grid(row=0, column=4, padx=10, pady=5)

        self.item_tree = ttk.Treeview(self.items_frame, columns=("Name", "Value"), show="headings")
        self.item_tree.heading("Name", text="Name")
        self.item_tree.heading("Value", text="Value")
        self.item_tree.pack(fill="both", expand=True, padx=10, pady=5)
        tree_buttons_frame = ttk.Frame(self.items_frame)
        tree_buttons_frame.pack(fill="x", padx=10, pady=5)
        remove_button = ttk.Button(tree_buttons_frame, text="Remove Selected", command=self.remove_item)
        remove_button.pack(side="left", padx=5)

        self.refresh_item()

    def refresh_item(self):
        for item in self.item_tree.get_children():
            self.item_tree.delete(item)
        if not items:
            return
        for account_key, balance in sorted(items.items()):
            self.item_tree.insert("", "end", values=(account_key, f"${balance:,.2f}"))

    def add_item(self):
        quantity_str = self.item_quantity_entry.get().strip()
        account_name = self.item_name_entry.get().strip()
        if not account_name:
            messagebox.showerror("Error", "Please enter an item name.")
            return
        try:
            quantity = float(quantity_str)
            if quantity <= 0:
                raise ValueError("Value must be positive.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid value input: {e}")
            return
        items[account_name] = items.get(account_name, 0.0) + quantity
        save_data()
        messagebox.showinfo("Success", f"Added ${quantity:,.2f} to {account_name}. \nNew cash balance for {account_name}: ${items[account_name]:,.2f}")
        self.item_quantity_entry.delete(0, "end")
        self.item_name_entry.delete(0, "end")
        self.refresh_item()

    def remove_item(self):
        selected_item = self.item_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a cash account to remove.")
            return

        itemAccount = self.item_tree.item(selected_item[0])['values'][0]
        current_quantity = items.get(itemAccount, 0.0)

        quantity_to_remove_str = simpledialog.askstring("Remove Cash Account", f"How many dollar(s)/cent(s) of {itemAccount} to remove?\nCurrent holding: {current_quantity}\n(Leave blank to remove all)")

        if quantity_to_remove_str is None:
            return

        if quantity_to_remove_str.strip() == "":
            if messagebox.askyesno("Confirm", f"Are you sure you want to remove all cash of {itemAccount}?"):
                del items[itemAccount]
                save_data()
                self.refresh_item()
        else:
            try:
                quantity_to_remove = float(quantity_to_remove_str)
                if quantity_to_remove <= 0:
                    raise ValueError("Quantity must be positive.")
                if quantity_to_remove > current_quantity:
                    messagebox.showerror("Error", f"Cannot remove {quantity_to_remove} units. You only have {current_quantity}.")
                    return
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid quantity: {e}")
                return

            new_quantity = current_quantity - quantity_to_remove
            if new_quantity < 1e-9:
                del items[itemAccount]
            else:
                items[itemAccount] = new_quantity

            save_data()
            self.refresh_item()


    def create_debt_tab(self):
        controls_frame = ttk.LabelFrame(self.debt_frame, text="Manage Debt(s):")
        controls_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(controls_frame, text="Debt(s): ").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.debt_name_entry = ttk.Entry(controls_frame)
        self.debt_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(controls_frame, text="Quantity:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.debt_quantity_entry = ttk.Entry(controls_frame)
        self.debt_quantity_entry.grid(row=0, column=3, padx=5, pady=5)

        add_button = ttk.Button(controls_frame, text="Add Debt", command=self.add_debt)
        add_button.grid(row=0, column=4, padx=10, pady=5)

        self.debt_tree = ttk.Treeview(self.debt_frame, columns=("Name", "Balance"), show="headings")
        self.debt_tree.heading("Name", text="Name")
        self.debt_tree.heading("Balance", text="Balance")
        self.debt_tree.pack(fill="both", expand=True, padx=10, pady=5)
        tree_buttons_frame = ttk.Frame(self.debt_frame)
        tree_buttons_frame.pack(fill="x", padx=10, pady=5)
        remove_button = ttk.Button(tree_buttons_frame, text="Remove Selected", command=self.remove_debt)
        remove_button.pack(side="left", padx=5)

        self.refresh_debt()

    def refresh_debt(self):
        for item in self.debt_tree.get_children():
            self.debt_tree.delete(item)
        if not debt:
            return
        for name, balance in sorted(debt.items()):
            self.debt_tree.insert("", "end", values=(name, f"${float(balance):,.2f}"))
    def add_debt(self):
        name = self.debt_name_entry.get().strip()
        amountAdd = self.debt_quantity_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a name for the debt.")
            return
        try: 
            amount = float(amountAdd)
            if amount <= 0:
                raise ValueError("Amount must be positive.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid amount: {e}")
            return
        debt[name] = debt.get(name, 0.0) + amount
        save_data()
        messagebox.showinfo("Success", f"Added ${amount:,.2f} to {name}. \nNew debt balance for {name}: ${debt[name]:,.2f}")
        self.debt_name_entry.delete(0, "end")
        self.debt_quantity_entry.delete(0, "end")
        self.refresh_debt()


    def remove_debt(self):
        select = self.debt_tree.selection()
        if not select:
            messagebox.showwarning("Warning", "Please select a debt to modify/remove.")
            return
        account = self.debt_tree.item(select[0])['values'][0]
        currentQuantity = float(debt.get(account, 0.0))
        quantity = simpledialog.askstring("Remove Debt", f"Enter amount to subtract from '{account}' Current: ${currentQuantity:,.2f}, (Leave blank to remove the account)")
        if quantity is None:
            return
        if quantity.strip() == "":
            if messagebox.askyesno("Confirm", f"Are you sure you want to remove all debt of {account}?"):
                if account in debt:
                    del debt[account]
                save_data()
                self.refresh_debt()
            return
        
        try: 
            amount = float(quantity)
            if amount <= 0:
                raise ValueError("Amount must be positive.")
        except ValueError:
            messagebox.showerror("Error", "Invalid number entered.")
            return
        changed = safe_subtract_and_maybe_delete(debt, account, amount)
        if changed:
            save_data()
            self.refresh_debt()
        else: 
            messagebox.showinfo("No Change", "No changes made to the account")
        return
    
    def create_ai_tab(self):
        controls_frame = ttk.LabelFrame(self.ai_frame, text="AI Chat:")
        controls_frame.pack(fill="x", padx=10, pady=5)

        controls_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(controls_frame, text="Ask Question: ").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.ai_question_entry = ttk.Entry(controls_frame)
        self.ai_question_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        add_button = ttk.Button(controls_frame, text="Ask", command=self.on_ai_ask)
        add_button.grid(row=0, column=2, padx=10, pady=5)

        response_frame = ttk.Frame(self.ai_frame)
        response_frame.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(response_frame)
        scrollbar.pack(side="right", fill="y")

        self.ai_response_text = tk.Text(response_frame, wrap="word", yscrollcommand=scrollbar.set, state="disabled")
        self.ai_response_text.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=self.ai_response_text.yview)

        buttons_frame = ttk.Frame(self.ai_frame)
        buttons_frame.pack(fill="x", padx=10, pady=5)

        clear_button = ttk.Button(buttons_frame, text="Clear Chat", command=self.clear_ai_chat)
        clear_button.pack(side="left", padx=5)

    def on_ai_ask(self):
        question = self.ai_question_entry.get().strip()
        if not question:
            messagebox.showerror("Error", "Please enter a question.")
            return

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

        try: 
            response = ask_ai(
                question,
                stocks=priced_stocks,
                crypto=priced_crypto,
                bullion=priced_bullion,
                cash=cash,
                items=items,
                debt=debt,
            )
        except Exception as exc:
            messagebox.showerror("AI Error", f"Assistant Error: {exc}")
            return
        self.ai_response_text.config(state="normal")
        if self.ai_response_text.get("1.0", "end-1c"):
            self.ai_response_text.insert("end", "\n\n")
        self.ai_response_text.insert("end", f"You: {question}\n")
        self.ai_response_text.insert("end", f"AI: {response}")
        self.ai_response_text.config(state="disabled")
        self.ai_response_text.see("end")
        self.ai_question_entry.delete(0, "end")

    def clear_ai_chat(self):
        self.ai_response_text.config(state="normal")
        self.ai_response_text.delete("1.0", "end")
        self.ai_response_text.config(state="disabled")

if __name__ == "__main__":
    app = AssetTrackerApp()
    app.mainloop()
