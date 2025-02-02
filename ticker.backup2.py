import csv
import tkinter as tk
import yfinance as yf
from tkinter import ttk

# Function to fetch real-time stock data from Yahoo Finance
def fetch_stock_data(ticker):
    stock = yf.Ticker(ticker)
    try:
        # Fetch historical data (1 day)
        hist = stock.history(period="1d")
        if hist.empty:
            return None  # No data found, return None

        # Calculate the percentage change
        change_percent = (hist['Close'].iloc[0] - hist['Open'].iloc[0]) / hist['Open'].iloc[0] * 100
        return change_percent
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

# Function to determine box color based on percentage change
def get_color(change):
    if change is None:
        return "#D3D3D3", "black"  # Light grey for missing data
    if change > 3:
        return "#FFD700", "black"  # Gold border for over 3%
    elif change > 2:
        return "#006400", "white" if change > 0 else "#8B0000"  # Dark green/red
    elif change > 1:
        return "#32CD32", "black" if change > 0 else "#FF6347"  # Light green/red
    elif change < -2:
        return "#8B0000", "white"  # Dark red
    elif change < -1:
        return "#FF6347", "black"  # Light red
    else:
        return "white", "black"  # Neutral box if under 1%

# Create the main window
root = tk.Tk()
root.title("Stock Holdings")

# Set window size (1920x1080)
root.geometry("1920x1080")

# Create a frame to hold the boxes and a canvas for scrollbars
canvas = tk.Canvas(root)
frame = tk.Frame(canvas)

# Create vertical and horizontal scrollbars
vsb = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
hsb = ttk.Scrollbar(root, orient="horizontal", command=canvas.xview)

canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

# Place canvas and scrollbars using grid layout to position them at the edges
canvas.grid(row=0, column=0, sticky="nsew")
vsb.grid(row=0, column=1, sticky="ns")
hsb.grid(row=1, column=0, sticky="ew")

# Create window inside canvas for scrolling
canvas.create_window((0, 0), window=frame, anchor="nw")

# Make the grid layout expand to take up the full window size
root.grid_rowconfigure(0, weight=1, minsize=800)
root.grid_columnconfigure(0, weight=1, minsize=1200)

# Read data from the CSV file ("VOO.csv") without pandas
with open('VOO.csv', mode='r', newline='', encoding='utf-8-sig') as file:
    reader = csv.DictReader(file)
    
    # Clean up column names to remove any unwanted BOM characters or extra spaces
    reader.fieldnames = [field.strip() for field in reader.fieldnames]

    # Check and print column names after cleaning
    print("CSV Column Names:", reader.fieldnames)

    # Create a small box for each holding
    box_width = 120
    box_height = 60
    columns = 16  # Adjust this based on your screen width and box size
    rows = 33  # Adjust this based on your screen height and box size

    # Variable to track row count for placing boxes
    row_count = 0

    # Iterate over the rows of the CSV
    for i, row in enumerate(reader):
        ticker = row['Ticker'].strip()  # Strip any extra spaces
        name = row['Holdings'].strip()  # Strip any extra spaces
        # Remove commas and dollar signs from Shares and Market value
        shares = row['Shares'].replace(',', '').strip()
        market_value = row['Market value'].replace('$', '').replace(',', '').strip()

        # Replace periods with dashes in ticker symbols
        ticker = ticker.replace('.', '-')

        # Fetch the real-time percentage change for the stock ticker
        change_percent = fetch_stock_data(ticker)

        # Determine color based on the percentage change
        color, border_color = get_color(change_percent)

        # Create a label for each box with the stock ticker and percentage change
        label = tk.Label(
            frame,
            text=f"{ticker}\n{change_percent:.2f}%" if change_percent is not None else f"{ticker}\nNo Data",
            width=15,
            height=3,
            bg=color,
            fg=border_color,
            relief="solid",
            font=("Helvetica", 10),
        )

        # Calculate row and column in the grid
        row_pos = (i // columns) * box_height
        col_pos = (i % columns) * box_width

        # Position the box
        label.grid(row=row_count // columns, column=row_count % columns, padx=5, pady=5)
        
        # Increment row_count to keep track of placement
        row_count += 1

        # Output status text (in green or red)
        status_color = "green" if change_percent is not None else "red"
        status_text = f"{ticker}: {'Success' if change_percent is not None else 'Failed'}"
        status_label = tk.Label(frame, text=status_text, fg=status_color, font=("Helvetica", 10))
        status_label.grid(row=row_count // columns, column=row_count % columns, padx=5, pady=5)

# Update scroll region after all widgets are placed
frame.update_idletasks()
canvas.config(scrollregion=canvas.bbox("all"))

# Run the Tkinter event loop
root.mainloop()
