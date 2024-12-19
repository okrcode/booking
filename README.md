# Booking.com Scraper

This Python script scrapes hotel data from Booking.com, specifically focusing on details such as hotel name, ID, location, room pricing, and images. The data is saved in a JSON format.

## Features

- Scrapes hotel information from Booking.com for a specific date range.
- Extracts details like hotel name, address, coordinates (latitude and longitude), room pricing, and images.
- Logs the scraping process and errors.
- Saves the scraped data to a JSON file.

## Requirements

- Python 3.x
- `requests` - To send HTTP requests and retrieve HTML content.
- `lxml` - For parsing HTML and XML documents.
- `json` - For handling JSON data.
- `logging` - To log the scraping process.
- `urllib3` - For HTTP requests with suppressed SSL warnings.

You can install the required libraries using:

```bash
pip install requests lxml
```

## Features

- Scrapes hotel data including:
  - Hotel name
  - Address (including postal code, region, country)
  - Latitude and Longitude
  - Room pricing details
  - Hotel images
  - Currency
  - Lowest room price
  - Saves scraped data to a JSON file.
  - Logs events such as successful data scraping and errors.



## Usage

- Clone or download the repository containing the script.

- Install the required dependencies:

```bash
pip install requests lxml
```

- Run the script by executing it in the command line:
```bash
python booking.py
```


- After execution, the data will be saved in a JSON file called booking_output.json in the same directory as the script.

## Example Output (booking_output.json)
```bash
[
    {
        "source_url": "https://www.booking.com/hotel/us/example-hotel",
        "hotel_name": "Example Hotel",
        "hotel_id": "12345",
        "latitude": "40.712776",
        "longitude": "-74.005974",
        "address": "123 Example St.",
        "postal_code": "10001",
        "country": "United States",
        "region": "New York",
        "images": "https://example.com/images.jpg",
        "currency": "USD",
        "room_details": [
            {
                "room_type": "Standard Room",
                "pricing_details": [
                    {
                        "price": "$150",
                        "max_persons": 2,
                        "raw_price": 120,
                        "raw_price_tax": 30,
                        "total_price": 150
                    }
                ]
            }
        ],
        "lowest_price": 120
    }
]

```

