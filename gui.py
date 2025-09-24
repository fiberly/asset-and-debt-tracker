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
    budget,
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
        self.geometry("1100x410")
        load_data()
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)
        self.stocks_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stocks_frame, text="Stocks")
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
        self.budget_frame = ttk.Frame(self.notebook, padding=(10, 10))
        self.notebook.add(self.budget_frame, text="Budget")
        self.total_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.total_frame, text="Totals")
        self.create_stocks_tab()
        self.create_crypto_tab()
        self.create_bullion_tab()
        self.create_cash_tab()
        self.create_item_tab()
        self.create_debt_tab()
        self.create_budget_tab()
        self.create_total_tab()
    def create_stocks_tab(self):
        controls_frame = ttk.LabelFrame(self.stocks_frame, text="Manage Stocks")
        controls_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(controls_frame, text="Ticker:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.stock_ticker_entry = ttk.Entry(controls_frame)
        self.stock_ticker_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(controls_frame, text="Quantity:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.stock_quantity_entry = ttk.Entry(controls_frame, width=10)
        self.stock_quantity_entry.grid(row=0, column=3, padx=5, pady=5)
        add_button = ttk.Button(controls_frame, text="Add Stock", command=self.add_stock)
        add_button.grid(row=0, column=6, padx=10, pady=5)
        ttk.Label(controls_frame, text="Price (per):").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.stock_price_entry = ttk.Entry(controls_frame)
        self.stock_price_entry.grid(row=0, column=5, padx=5, pady=5)
        self.stocks_tree = ttk.Treeview(self.stocks_frame, columns=("Ticker", "Quantity", "Avg. Buy", "Total Purchase(s) Cost", "Price", "Value", "P/L"), show="headings")
        self.stocks_tree.heading("Ticker", text="Ticker", anchor='w')
        self.stocks_tree.heading("Quantity", text="Quantity", anchor='e')
        self.stocks_tree.heading("Avg. Buy", text="Avg. Buy Price", anchor='e')
        self.stocks_tree.heading("Total Purchase(s) Cost", text="Total Purchase(s) Cost", anchor='e')
        self.stocks_tree.heading("Price", text="Current Price", anchor='e')
        self.stocks_tree.heading("Value", text="Current Value", anchor='e')
        self.stocks_tree.heading("P/L", text="P/L", anchor='e')
        self.stocks_tree.column("Ticker", width=80, anchor='w')
        self.stocks_tree.column("Quantity", width=100, anchor='e')
        self.stocks_tree.column("Avg. Buy", width=100, anchor='e')
        self.stocks_tree.column("Total Purchase(s) Cost", width=130, anchor='e')
        self.stocks_tree.column("Price", width=100, anchor='e')
        self.stocks_tree.column("Value", width=120, anchor='e')
        self.stocks_tree.column("P/L", width=100, anchor='e')
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
        for ticker, position_data in sorted(Stocks.items()):
            shares = position_data.get("shares", 0.0)
            cost_basis = position_data.get("cost_basis", 0.0)
            avg_buy_price = (cost_basis / shares) if shares > 0 else 0.0
            price = getPrice(ticker)
            if price is not None:
                value = shares * price
                profitLoss = value - cost_basis
                profitLoss_str = f"${profitLoss:,.2f}"
                self.stocks_tree.insert("", "end", values=(ticker, f"{shares:.4f}", f"${avg_buy_price:,.2f}", f"${cost_basis:,.2f}", f"${price:,.2f}", f"${value:,.2f}", profitLoss_str))
            else:
                self.stocks_tree.insert("", "end", values=(ticker, f"{shares:.4f}", f"${avg_buy_price:,.2f}", f"${cost_basis:,.2f}", "N/A", "N/A", "N/A"))

    def add_stock(self):
        ticker = self.stock_ticker_entry.get().strip().upper()
        quantity_str = self.stock_quantity_entry.get().strip()
        price_str = self.stock_price_entry.get().strip()

        if not ticker:
            messagebox.showerror("Error", "Ticker cannot be empty.")
            return
        if not is_valid_ticker(ticker) and not messagebox.askyesno("Warning", f"Ticker '{ticker}' looks invalid. Continue anyway?"):
            messagebox.showerror("Error", "Invalid ticker format. Use letters only.")
            return

        try:
            quantity = float(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be positive.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid quantity: {e}")
            return

        try:
            price = float(price_str)
            if price < 0:
                raise ValueError("Price cannot be negative.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid price: {e}")
            return

        position = Stocks.get(ticker, {"shares": 0.0, "cost_basis": 0.0})
        position["shares"] += quantity
        position["cost_basis"] += quantity * price
        Stocks[ticker] = position
        save_data()
        avg_price = position['cost_basis'] / position['shares']
        messagebox.showinfo("Success", f"Added {quantity} shares of {ticker} at ${price:,.2f} each.\nNew average price: ${avg_price:,.2f}")

        self.stock_ticker_entry.delete(0, "end")
        self.stock_quantity_entry.delete(0, "end")
        self.stock_price_entry.delete(0, "end")
        self.refresh_stocks()

    def remove_stock(self):
        selected_item = self.stocks_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a stock to remove.")
            return

        ticker = self.stocks_tree.item(selected_item[0])['values'][0]
        position = Stocks.get(ticker, {"shares": 0.0, "cost_basis": 0.0})
        current_shares = position.get("shares", 0.0)

        quantity_to_remove_str = simpledialog.askstring("Remove Stock", f"How many shares of {ticker} to remove?\nCurrent holding: {current_shares}\n(Leave blank to remove all)")

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
                if quantity_to_remove > current_shares:
                    messagebox.showerror("Error", f"Cannot remove {quantity_to_remove} shares. You only have {current_shares}.")
                    return
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid quantity: {e}")
                return

            new_shares = current_shares - quantity_to_remove
            if new_shares < 1e-9:
                del Stocks[ticker]
            else:
                old_cost_basis = position.get("cost_basis", 0.0)
                cost_basis_to_remove = (old_cost_basis / current_shares) * quantity_to_remove if current_shares > 0 else 0
                
                position["shares"] = new_shares
                position["cost_basis"] = max(0.0, old_cost_basis - cost_basis_to_remove)
                Stocks[ticker] = position
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

        ttk.Label(controls_frame, text="Price (per):").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.crypto_price_entry = ttk.Entry(controls_frame)
        self.crypto_price_entry.grid(row=0, column=5, padx=5, pady=5)

        add_button = ttk.Button(controls_frame, text="Add Crypto", command=self.add_crypto)
        add_button.grid(row=0, column=6, padx=10, pady=5)

        self.crypto_tree = ttk.Treeview(self.crypto_frame, columns=("Name", "Quantity", "Avg. Buy", "Total Purchase(s) Cost", "Price", "Value", "P/L"), show="headings")
        self.crypto_tree.heading("Name", text="Crypto Name", anchor='w')
        self.crypto_tree.heading("Quantity", text="Quantity", anchor='e')
        self.crypto_tree.heading("Avg. Buy", text="Avg. Buy Price", anchor='e')
        self.crypto_tree.heading("Total Purchase(s) Cost", text="Total Purchase(s) Cost", anchor='e')
        self.crypto_tree.heading("Price", text="Current Price", anchor='e')
        self.crypto_tree.heading("Value", text="Current Value", anchor='e')
        self.crypto_tree.heading("P/L", text="P/L", anchor='e')
        self.crypto_tree.column("Name", width=100, anchor='w')
        self.crypto_tree.column("Quantity", width=100, anchor='e')
        self.crypto_tree.column("Avg. Buy", width=100, anchor='e')
        self.crypto_tree.column("Total Purchase(s) Cost", width=130, anchor='e')
        self.crypto_tree.column("Price", width=100, anchor='e')
        self.crypto_tree.column("Value", width=120, anchor='e')
        self.crypto_tree.column("P/L", width=100, anchor='e')
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

        for cid, position_data in sorted(crypto.items()):
            units = position_data.get("units", 0.0)
            cost_basis = position_data.get("cost_basis", 0.0)
            avg_buy_price = (cost_basis / units) if units > 0 else 0.0
            price = prices.get(cid)

            if price is not None:
                value = units * price
                profitLoss = value - cost_basis
                profitLoss_str = f"${profitLoss:,.2f}"
                self.crypto_tree.insert("", "end", values=(cid, f"{units:,.4f}", f"${avg_buy_price:,.2f}", f"${cost_basis:,.2f}", f"${price:,.2f}", f"${value:,.2f}", profitLoss_str))
            else:
                self.crypto_tree.insert("", "end", values=(cid, f"{units:,.4f}", f"${avg_buy_price:,.2f}", f"${cost_basis:,.2f}", "N/A", "N/A", "N/A"))

        

    def add_crypto(self):
        cryptoName = self.crypto_id_entry.get().strip().lower()
        quantity_str = self.crypto_quantity_entry.get().strip()
        price_str = self.crypto_price_entry.get().strip()

        # ... (validation for cryptoName, quantity_str, price_str)
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

        try:
            price = float(price_str)
            if price < 0:
                raise ValueError("Price cannot be negative.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid price: {e}")
            return

        position = crypto.get(cryptoName, {"units": 0.0, "cost_basis": 0.0})
        position["units"] += quantity
        position["cost_basis"] += quantity * price
        crypto[cryptoName] = position
        save_data()
        avg_price = position['cost_basis'] / position['units']
        messagebox.showinfo("Success", f"Added {quantity} of {cryptoName} at ${price:,.2f} each.\nNew average price: ${avg_price:,.2f}")

        self.crypto_id_entry.delete(0, "end")
        self.crypto_quantity_entry.delete(0, "end")
        self.crypto_price_entry.delete(0, "end")
        self.refresh_crypto()

    def remove_crypto(self):
        selected_item = self.crypto_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a cryptocurrency to remove.")
            return

        cryptoID = self.crypto_tree.item(selected_item[0])['values'][0]
        position = crypto.get(cryptoID, {"units": 0.0, "cost_basis": 0.0})
        current_units = position.get("units", 0.0)

        quantity_to_remove_str = simpledialog.askstring("Remove Cryptocurrency", f"How many units of {cryptoID} to remove?\nCurrent holding: {current_units}\n(Leave blank to remove all)")

        if quantity_to_remove_str is None:
            return

        if quantity_to_remove_str.strip() == "":
            if messagebox.askyesno("Confirm", f"Are you sure you want to remove all units of {cryptoID}?"):
                del crypto[cryptoID]
                save_data()
                self.refresh_crypto()
        else:
            try:
                quantity_to_remove = float(quantity_to_remove_str)
                if quantity_to_remove <= 0:
                    raise ValueError("Quantity must be positive.")
                if quantity_to_remove > current_units:
                    messagebox.showerror("Error", f"Cannot remove {quantity_to_remove} units. You only have {current_units}.")
                    return
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid quantity: {e}")
                return

            new_units = current_units - quantity_to_remove
            if new_units < 1e-9:
                del crypto[cryptoID]
            else:
                old_cost_basis = position.get("cost_basis", 0.0)
                cost_basis_to_remove = (old_cost_basis / current_units) * quantity_to_remove if current_units > 0 else 0
                
                position["units"] = new_units
                position["cost_basis"] = max(0.0, old_cost_basis - cost_basis_to_remove)
                crypto[cryptoID] = position
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

        ttk.Label(controls_frame, text="Price (per):").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.bullion_price_entry = ttk.Entry(controls_frame)
        self.bullion_price_entry.grid(row=0, column=5, padx=5, pady=5)

        add_button = ttk.Button(controls_frame, text="Add Bullion", command=self.add_bullion)
        add_button.grid(row=0, column=6, padx=10, pady=5)

        self.bullion_tree = ttk.Treeview(self.bullion_frame, columns=("Name", "Quantity", "Avg. Buy", "Total Purchase(s) Cost", "Price", "Value", "P/L"), show="headings")
        self.bullion_tree.heading("Name", text="Bullion Name", anchor='w')
        self.bullion_tree.heading("Quantity", text="Quantity", anchor='e')
        self.bullion_tree.heading("Avg. Buy", text="Avg. Buy Price", anchor='e')
        self.bullion_tree.heading("Total Purchase(s) Cost", text="Total Purchase(s) Cost", anchor='e')
        self.bullion_tree.heading("Price", text="Current Price", anchor='e')
        self.bullion_tree.heading("Value", text="Current Value", anchor='e')
        self.bullion_tree.heading("P/L", text="P/L", anchor='e')
        self.bullion_tree.column("Name", width=120, anchor='w')
        self.bullion_tree.column("Quantity", width=120, anchor='e')
        self.bullion_tree.column("Avg. Buy", width=100, anchor='e')
        self.bullion_tree.column("Total Purchase(s) Cost", width=130, anchor='e')
        self.bullion_tree.column("Price", width=100, anchor='e')
        self.bullion_tree.column("Value", width=120, anchor='e')
        self.bullion_tree.column("P/L", width=100, anchor='e')
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

        for metal, position_data in sorted(bullion.items()):
            units = position_data.get("units", 0.0)
            cost_basis = position_data.get("cost_basis", 0.0)
            avg_buy_price = (cost_basis / units) if units > 0 else 0.0
            price = prices.get(metal)

            if price is not None:
                value = units * price
                profitLoss = value - cost_basis
                profitLoss_str = f"${profitLoss:,.2f}"
                self.bullion_tree.insert("", "end", values=(metal, f"{units:,.4f}", f"${avg_buy_price:,.2f}", f"${cost_basis:,.2f}", f"${price:,.2f}", f"${value:,.2f}", profitLoss_str))
            else:
                self.bullion_tree.insert("", "end", values=(metal, f"{units:,.4f}", f"${avg_buy_price:,.2f}", f"${cost_basis:,.2f}", "N/A", "N/A", "N/A"))

    def add_bullion(self):
        bullionName = self.bullion_name_entry.get().strip().lower()
        quantity_str = self.bullion_quantity_entry.get().strip()
        price_str = self.bullion_price_entry.get().strip()

        if bullionName not in ("gold", "silver", "palladium", "copper"):
            messagebox.showerror("Error", "Invalid bullion type. Use 'gold', 'silver', 'palladium', or 'copper'.")
            return

        try:
            quantity = float(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be positive.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid quantity: {e}")
            return
        
        try:
            price = float(price_str)
            if price < 0:
                raise ValueError("Price cannot be negative.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid price: {e}")
            return

        position = bullion.get(bullionName, {"units": 0.0, "cost_basis": 0.0})
        position["units"] += quantity
        position["cost_basis"] += quantity * price
        bullion[bullionName] = position
        save_data()
        avg_price = position['cost_basis'] / position['units']
        messagebox.showinfo("Success", f"Added {quantity} of {bullionName} at ${price:,.2f} each.\nNew average price: ${avg_price:,.2f}")

        self.bullion_name_entry.delete(0, "end")
        self.bullion_quantity_entry.delete(0, "end")
        self.bullion_price_entry.delete(0, "end")
        self.refresh_bullion()

    def remove_bullion(self):
        selected_item = self.bullion_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a bullion to remove.")
            return

        bullionType = self.bullion_tree.item(selected_item[0])['values'][0]
        position = bullion.get(bullionType, {"units": 0.0, "cost_basis": 0.0})
        current_quantity = position.get("units", 0.0)

        quantity_to_remove_str = simpledialog.askstring("Remove Bullion", f"How many oz of {bullionType} to remove?\nCurrent holding: {current_quantity}\n(Leave blank to remove all)")

        if quantity_to_remove_str is None:
            return

        if quantity_to_remove_str.strip() == "":
            if messagebox.askyesno("Confirm", f"Are you sure you want to remove all units of {bullionType}?"):
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
                old_cost_basis = position.get("cost_basis", 0.0)
                cost_basis_to_remove = (old_cost_basis / current_quantity) * quantity_to_remove if current_quantity > 0 else 0
                
                position["units"] = new_quantity
                position["cost_basis"] = max(0.0, old_cost_basis - cost_basis_to_remove)
                bullion[bullionType] = position
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
        self.cash_tree.column("Account", width=200, anchor='w')
        self.cash_tree.column("Value", width=150, anchor='e')
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
        self.item_tree.column("Name", width=200, anchor='w')
        self.item_tree.column("Value", width=150, anchor='e')
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
        self.debt_tree.column("Name", width=200, anchor='w')
        self.debt_tree.column("Balance", width=150, anchor='e')
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
        for ticker, position in Stocks.items():
            price = getPrice(ticker)
            priced_stocks[ticker] = {"quantity": position.get('shares', 0.0), "last_price": price or 0.0}

        priced_crypto = {}
        if crypto:
            prices = getGUICryptoPrices(list(crypto.keys()), quiet=True)
            for cid, position in crypto.items():
                priced_crypto[cid] = {"quantity": position.get('units', 0.0), "last_price": prices.get(cid, 0.0)}

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

    def create_budget_tab(self):
        # --- Total Budget Frame ---
        total_frame = ttk.LabelFrame(self.budget_frame, text="Total Budget")
        total_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.total_budget_label = ttk.Label(total_frame, text=f"Current: ${budget.get('total', 0.0):,.2f}", font=("", 10, "bold"))
        self.total_budget_label.grid(row=0, column=0, padx=5, pady=5)

        self.budget_entry = ttk.Entry(total_frame, width=12)
        self.budget_entry.grid(row=0, column=1, padx=5, pady=5)

        set_button = ttk.Button(total_frame, text="Set/Add Budget", command=self.set_budget)
        set_button.grid(row=0, column=2, padx=5, pady=5)

        remove_button = ttk.Button(total_frame, text="Remove Budget", command=self.remove_budget)
        remove_button.grid(row=0, column=3, padx=5, pady=5)

        # --- Spending Tracker Frame ---
        spending_frame = ttk.LabelFrame(self.budget_frame, text="Add Spending")
        spending_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        ttk.Label(spending_frame, text="Category:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.budget_category_combo = ttk.Combobox(spending_frame, values=["food", "entertainment", "housing", "utilities", "clothing"], state="readonly")
        self.budget_category_combo.grid(row=0, column=1, padx=5, pady=5)
        self.budget_category_combo.set("food")

        ttk.Label(spending_frame, text="Amount:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.spending_amount_entry = ttk.Entry(spending_frame, width=12)
        self.spending_amount_entry.grid(row=0, column=3, padx=5, pady=5)

        add_spending_button = ttk.Button(spending_frame, text="Add Expense", command=self.add_expense)
        add_spending_button.grid(row=0, column=4, padx=5, pady=(5, 2), sticky="ew")

        remove_spending_button = ttk.Button(spending_frame, text="Remove Expense", command=self.remove_expense)
        remove_spending_button.grid(row=1, column=4, padx=5, pady=(2, 5), sticky="ew")

        # --- Budget Summary Frame ---
        summary_frame = ttk.LabelFrame(self.budget_frame, text="Budget Summary")
        summary_frame.grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky="nsew")

        self.budget_summary_tree = ttk.Treeview(summary_frame, columns=("Category", "Spent"), show="headings")
        self.budget_summary_tree.heading("Category", text="Category")
        self.budget_summary_tree.heading("Spent", text="Amount Spent")
        self.budget_summary_tree.column("Category", width=120, anchor='w')
        self.budget_summary_tree.column("Spent", width=120, anchor='e')
        self.budget_summary_tree.pack(fill="both", expand=True, padx=5, pady=5)

        self.budget_status_label = ttk.Label(summary_frame, text="", font=("", 10, "bold"))
        self.budget_status_label.pack(pady=5)

        self.budget_frame.grid_columnconfigure(1, weight=1)
        self.refresh_budget()

    def refresh_budget(self):
        # Update total budget label
        self.total_budget_label.config(text=f"Current: ${budget.get('total', 0.0):,.2f}")

        # Clear and repopulate the summary tree
        for item in self.budget_summary_tree.get_children():
            self.budget_summary_tree.delete(item)

        total_spent = 0.0
        for category, spent in budget.items():
            if category != "total":
                self.budget_summary_tree.insert("", "end", values=(category.capitalize(), f"${spent:,.2f}"))
                total_spent += spent

        # Add total spending row
        self.budget_summary_tree.insert("", "end", values=("Total Spent", f"${total_spent:,.2f}"), tags=('total_row',))
        self.budget_summary_tree.tag_configure('total_row', font=('TkDefaultFont', 9, 'bold'))

        # Update over/under status
        total_budget = budget.get("total", 0.0)
        remaining = total_budget - total_spent
        if remaining >= 0:
            status_text = f"Under Budget by ${remaining:,.2f}"
            self.budget_status_label.config(text=status_text, foreground="green")
        else:
            status_text = f"Over Budget by ${abs(remaining):,.2f}"
            self.budget_status_label.config(text=status_text, foreground="red")

    def set_budget(self):
        amount_str = self.budget_entry.get().strip()
        if not amount_str:
            messagebox.showerror("Error", "Please enter an amount to set/add to the budget.")
            return
        try:
            amount = float(amount_str)
            if amount < 0:
                raise ValueError("Budget amount cannot be negative.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid amount: {e}")
            return

        budget["total"] += amount
        save_data()
        self.budget_entry.delete(0, "end")
        self.refresh_budget()

    def remove_budget(self):
        amount_str = self.budget_entry.get().strip()
        if not amount_str:
            messagebox.showerror("Error", "Please enter an amount to remove from the budget.")
            return
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Removal amount must be positive.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid amount: {e}")
            return

        current_budget = budget.get("total", 0.0)
        if amount > current_budget:
            if messagebox.askyesno("Confirm", f"This will reduce the budget by ${amount:,.2f}, which is more than the current total of ${current_budget:,.2f}. Set budget to $0?"):
                budget["total"] = 0.0
            else:
                return # User cancelled
        else:
            budget["total"] -= amount
        save_data()
        self.budget_entry.delete(0, "end")
        self.refresh_budget()

    def add_expense(self):
        category = self.budget_category_combo.get()
        amount_str = self.spending_amount_entry.get().strip()
        try:
            amount = float(amount_str)
            if amount <= 0: raise ValueError("Amount must be positive.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid amount: {e}")
            return
        budget[category] = budget.get(category, 0.0) + amount
        save_data()
        self.spending_amount_entry.delete(0, "end")
        self.refresh_budget()

    def remove_expense(self):
        category = self.budget_category_combo.get()
        amount_str = self.spending_amount_entry.get().strip()
        try:
            amount_to_remove = float(amount_str)
            if amount_to_remove <= 0:
                raise ValueError("Amount must be positive.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid amount: {e}")
            return

        current_spent = budget.get(category, 0.0)
        if amount_to_remove > current_spent:
            if messagebox.askyesno("Confirm", f"This will reduce spending for '{category.capitalize()}' by ${amount_to_remove:,.2f}, which is more than the current spent amount of ${current_spent:,.2f}. Set spending for this category to $0?"):
                budget[category] = 0.0
            else:
                return # User cancelled
        else:
            budget[category] -= amount_to_remove
        
        # Ensure we don't end up with a tiny negative number due to float precision
        if budget[category] < 1e-9:
            budget[category] = 0.0

        save_data()
        self.spending_amount_entry.delete(0, "end")
        self.refresh_budget()

    def create_total_tab(self):
        # --- Main Frame ---
        main_frame = ttk.Frame(self.total_frame, padding=(10, 10))
        main_frame.pack(fill="both", expand=True)

        # --- Treeview for Summary ---
        self.totals_tree = ttk.Treeview(main_frame, columns=("Category", "Value", "Profit/Loss"), show="headings")
        self.totals_tree.heading("Category", text="Category")
        self.totals_tree.heading("Value", text="Current Value")
        self.totals_tree.heading("Profit/Loss", text="Profit/Loss")

        self.totals_tree.column("Category", width=200, anchor='w')
        self.totals_tree.column("Value", width=150, anchor='e')
        self.totals_tree.column("Profit/Loss", width=150, anchor='e')

        self.totals_tree.pack(fill="both", expand=True)

        # --- Refresh Button ---
        refresh_button = ttk.Button(main_frame, text="Refresh Totals", command=self.refresh_totals)
        refresh_button.pack(pady=10)

        # --- Style for summary rows ---
        self.totals_tree.tag_configure('asset_total', font=('TkDefaultFont', 9, 'bold'))
        self.totals_tree.tag_configure('net_worth', font=('TkDefaultFont', 10, 'bold'))

        self.refresh_totals()

    def refresh_totals(self):
        for item in self.totals_tree.get_children():
            self.totals_tree.delete(item)

        # --- Calculate Asset Values and P/L ---
        stock_total, stock_pl = 0.0, 0.0
        for ticker, pos in Stocks.items():
            price = getPrice(ticker) or 0.0
            value = pos.get('shares', 0.0) * price
            stock_total += value
            stock_pl += value - pos.get('cost_basis', 0.0)

        crypto_total, crypto_pl = 0.0, 0.0
        if crypto:
            prices = getGUICryptoPrices(list(crypto.keys()), quiet=True)
            for cid, pos in crypto.items():
                price = prices.get(cid, 0.0)
                value = pos.get('units', 0.0) * price
                crypto_total += value
                crypto_pl += value - pos.get('cost_basis', 0.0)

        bullion_total, bullion_pl = 0.0, 0.0
        if bullion:
            prices = get_GUI_bullion_prices()
            for metal, pos in bullion.items():
                price = prices.get(metal, 0.0)
                value = pos.get('units', 0.0) * price
                bullion_total += value
                bullion_pl += value - pos.get('cost_basis', 0.0)

        cash_total = sum(float(v) for v in cash.values())
        item_total = sum(float(v) for v in items.values())
        debt_total = sum(float(v) for v in debt.values())

        # --- Populate Treeview ---
        self.totals_tree.insert("", "end", values=("Stocks", f"${stock_total:,.2f}", f"${stock_pl:,.2f}"))
        self.totals_tree.insert("", "end", values=("Cryptocurrency", f"${crypto_total:,.2f}", f"${crypto_pl:,.2f}"))
        self.totals_tree.insert("", "end", values=("Bullion", f"${bullion_total:,.2f}", f"${bullion_pl:,.2f}"))
        self.totals_tree.insert("", "end", values=("Cash", f"${cash_total:,.2f}", "---"))
        self.totals_tree.insert("", "end", values=("Items", f"${item_total:,.2f}", "---"))
        self.totals_tree.insert("", "end", values=("", "", "")) # Separator

        total_assets = stock_total + crypto_total + bullion_total + cash_total + item_total
        self.totals_tree.insert("", "end", values=("Total Assets", f"${total_assets:,.2f}", ""), tags=('asset_total',))
        self.totals_tree.insert("", "end", values=("Total Debt", f"(${debt_total:,.2f})", ""), tags=('asset_total',))
        self.totals_tree.insert("", "end", values=("", "", "")) # Separator

        net_worth = total_assets - debt_total
        self.totals_tree.insert("", "end", values=("Net Worth", f"${net_worth:,.2f}", ""), tags=('net_worth',))

if __name__ == "__main__":
    app = AssetTrackerApp()
    app.mainloop()
