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
)

# --- GUI Application ---

class AssetTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Asset and Debt Tracker")
        self.geometry("900x600")

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
        

        self.notebook.add(ttk.Frame(self.notebook), text="AI Chat (TBD)")

        self.create_stocks_tab()
        self.create_crypto_tab()
        self.create_bullion_tab()

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


    def create_cash_tab():
        pass
    def refresh_cash():
        pass
    def add_cash():
        pass
    def remove_cash():
        pass

    def create_item_tab():
        pass
    def refresh_item():
        pass
    def add_item():
        pass
    def remove_item():
        pass

    def create_debt_tab():
        pass
    def refresh_debt():
        pass
    def add_debt():
        pass
    def remove_debt():
        pass



if __name__ == "__main__":
    app = AssetTrackerApp()
    app.mainloop()

