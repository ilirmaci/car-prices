import numpy as np
import pandas as pd
from datetime import datetime

from utils import extract, search_car

DATA_FOLDER = "./data"

today = str(datetime.today())[:10]
file_name = f"{DATA_FOLDER}/extracted{today}.csv"
print(f"Writing data to {file_name}...")

cars = [
    ("volkswagen", "golf"),
    ("volkswagen", "t-roc"),
    ("skoda", "fabia"),
    ("skoda", "octavia"),
    ("skoda", "kamiq"),
    ("toyota", "rav-4"),
]
print(f"Scraping data for {len(cars)} models...")

data = []

for car in cars:
    unparsed_pages = search_car(*car, max_km=180_000)
    parsed_records = pd.DataFrame(extract(unparsed_pages))
    print(f"Got {parsed_records.shape[0]} records for {str(car)}")
    data.append(parsed_records)

result = pd.concat(data)
result.to_csv(file_name, index=False)
print(f"Wrote {result.shape[0]} records to {file_name}.")
