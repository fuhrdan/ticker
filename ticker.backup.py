import csv
import tkinter as tk
import yfinance as yf

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

# Create a frame to hold the boxes
frame = tk.Frame(root)
frame.place(x=10, y=10, width=1900, height=1040)

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

    # Iterate over the rows of the CSV
    for i, row in enumerate(reader):
        ticker = row['Ticker'].strip()  # Strip any extra spaces
        name = row['Holdings'].strip()  # Strip any extra spaces
        # Remove commas and dollar signs from Shares and Market value
        shares = row['Shares'].replace(',', '').strip()
        market_value = row['Market value'].replace('$', '').replace(',', '').strip()

        # Remove the $ symbol if it exists in the ticker (e.g., $BRK.B)
        ticker = ticker.lstrip('$')  # Removes any leading '$'

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
        label.place(x=col_pos, y=row_pos)

# Run the Tkinter event loop
root.mainloop()
