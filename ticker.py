import csv
import tkinter as tk
import yfinance as yf
from tkinter import ttk

# Function to fetch stock data from Yahoo Finance
def fetch_stock_data(ticker):
    stock = yf.Ticker(ticker)
    try:
        hist = stock.history(period="1d")
        if hist.empty:
            return None, None  # No data found
        change_percent = (hist['Close'].iloc[0] - hist['Open'].iloc[0]) / hist['Open'].iloc[0] * 100
        return change_percent, stock
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None, None

# Function to determine background color based on percentage change
def get_color(change):
    if change is None:
        return "#D3D3D3", "black"  # Light gray for missing data
    if change > 3:
        return "#FFD700", "black"  # Gold for big gains
    elif change > 2:
        return "#006400", "white"  # Dark green
    elif change > 1:
        return "#32CD32", "black"  # Light green
    elif 0 < change <= 1:
        return "#E0FFE0", "black"  # Very light green for small gains
    elif -1 <= change < 0:
        return "#FFE0E0", "black"  # Very light red for small losses
    elif change < -2:
        return "#8B0000", "white"  # Dark red
    elif change < -1:
        return "#FF6347", "black"  # Light red
    else:
        return "white", "black"  # Neutral box

# Function to display detailed stock information in a popup
def show_stock_details(ticker, stock):
    top = tk.Toplevel(root)
    top.title(f"Stock Details: {ticker}")
    top.geometry("400x300")
    
    # Fetch stock information
    stock_info = stock.info
    stock_name = stock_info.get("longName", "Unknown Name")
    price = stock_info.get("previousClose", "No Data")

    tk.Label(top, text=f"Ticker: {ticker}", font=("Helvetica", 14, "bold")).pack(pady=5)
    tk.Label(top, text=f"Full Name: {stock_name}", font=("Helvetica", 12)).pack(pady=5)
    tk.Label(top, text=f"Last Close Price: ${price}", font=("Helvetica", 12)).pack(pady=5)

    # Fetch price history (last 5 days)
    hist = stock.history(period="5d")
    if not hist.empty:
        prices_text = "\n".join([f"{date.date()}: ${round(price, 2)}" for date, price in hist['Close'].items()])
    else:
        prices_text = "No price history available."

    tk.Label(top, text="Price History (Last 5 Days):", font=("Helvetica", 12, "bold")).pack(pady=5)
    tk.Label(top, text=prices_text, font=("Helvetica", 10), justify="left").pack(pady=5)

# Create the main window
root = tk.Tk()
root.title("Stock Holdings")
root.geometry("1920x1080")

# Create a frame with a canvas for scrollbars
canvas = tk.Canvas(root)
frame = tk.Frame(canvas)

vsb = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
hsb = ttk.Scrollbar(root, orient="horizontal", command=canvas.xview)

canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

canvas.grid(row=0, column=0, sticky="nsew")
vsb.grid(row=0, column=1, sticky="ns")
hsb.grid(row=1, column=0, sticky="ew")

canvas.create_window((0, 0), window=frame, anchor="nw")

root.grid_rowconfigure(0, weight=1, minsize=800)
root.grid_columnconfigure(0, weight=1, minsize=1200)

# Read stock data from CSV
with open('VOO.csv', mode='r', newline='', encoding='utf-8-sig') as file:
    reader = csv.DictReader(file)
    reader.fieldnames = [field.strip() for field in reader.fieldnames]

    print("CSV Column Names:", reader.fieldnames)

    box_width = 120
    box_height = 60
    columns = 16
    row_count = 0

    for i, row in enumerate(reader):
        ticker = row['Ticker'].strip()
        name = row['Holdings'].strip()
        shares = row['Shares'].replace(',', '').strip()
        market_value = row['Market value'].replace('$', '').replace(',', '').strip()

        # Replace periods with dashes in ticker symbols
        ticker = ticker.replace('.', '-')

        # Fetch real-time data
        change_percent, stock_obj = fetch_stock_data(ticker)

        # Determine color
        color, text_color = get_color(change_percent)

        # Create label for each stock
        label = tk.Label(
            frame,
            text=f"{ticker}\n{change_percent:.2f}%" if change_percent is not None else f"{ticker}\nNo Data",
            width=15,
            height=3,
            bg=color,
            fg=text_color,
            relief="solid",
            font=("Helvetica", 10),
        )

        # Attach click event to open details
        if stock_obj:
            label.bind("<Button-1>", lambda event, t=ticker, s=stock_obj: show_stock_details(t, s))

        # Position box in grid
        label.grid(row=row_count // columns, column=row_count % columns, padx=5, pady=5)

        row_count += 1

frame.update_idletasks()
canvas.config(scrollregion=canvas.bbox("all"))

root.mainloop()
