import requests
import lxml.html
import json
import logging
from datetime import datetime, timedelta

import urllib3

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)

# Define headers for HTTP requests
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Referer': 'https://www.booking.com',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

def save_to_json(data_list, json_path):
    """Save the provided data list to a JSON file."""
    if not data_list:
        logging.warning("No data to save to JSON.")
        return

    try:
        with open(json_path, 'w', encoding='utf-8') as output_file:
            json.dump(data_list, output_file, ensure_ascii=False, indent=4)
        logging.info(f"Data successfully saved to {json_path}.")
    except Exception as e:
        logging.error(f"Failed to save data to JSON: {e}")


def get_lowest_price(price_list):
    """Return the lowest price from a list of prices."""
    lowest = price_list[0]

    if not price_list:
        logging.warning("Price list is empty.")
        return None
    for num in price_list:
        if num < lowest:
            lowest = num
    return lowest


def parse_room_details(response):
    """Parse room details from the response."""
    try:
        response_data = response.text.split("b_rooms_available_and_soldout: ")[1].split(",\nb_cheapest_price_that_fits_search_eur")[0]
        room_data = json.loads(response_data)
    except Exception as e:
        logging.error(f"Failed to parse room details: {e}")
        return [], []

    room_details_list = []
    price_list = []

    for room in room_data:
        room_type = room.get("b_name", "Unknown")
        room_pricing_details = []

        for block in room.get("b_blocks", []):
            price = block.get("b_price", 0)
            max_persons = block.get("b_max_persons", 0)
            raw_price = round(float(block.get("b_raw_price", 0)))
            price_list.append(raw_price)

            raw_price_tax = round(float(block.get("b_price_breakdown_simplified", {}).get("b_excluded_charges_amount", 0)))
            total_price = raw_price + raw_price_tax

            room_pricing_details.append({
                "price": price,
                "max_persons": max_persons,
                "raw_price": raw_price,
                "raw_price_tax": raw_price_tax,
                "total_price": total_price
            })

        room_details_list.append({
            "room_type": room_type,
            "pricing_details": room_pricing_details
        })

    return room_details_list, price_list

def scrape_booking_data():
    """Scrape data from Booking.com."""
    today = datetime.today()
    checkin_date = today.strftime("%Y-%m-%d")
    checkout_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")

    url = f"https://www.booking.com/searchresults.html?lang=en-us&sb=1&src_elem=sb&src=searchresults&dest_id=20016097&dest_type=city&selected_currency=USD&checkin={checkin_date}&checkout={checkout_date}&group_adults=2&no_rooms=1&group_children=0"

    scraped_data = []

    try:
        response = requests.get(url, headers=HEADERS, verify=False)
        response.raise_for_status()
        page_dom = lxml.html.fromstring(response.text)

        hotel_links = page_dom.xpath("//div[@class='d6767e681c']//@href")
        logging.info(f"Found {len(hotel_links)} hotel links.")

        for link in hotel_links:
            hotel_url = link + "&selected_currency=USD"
            try:
                hotel_response = requests.get(hotel_url, headers=HEADERS, verify=False)
                hotel_response.raise_for_status()
                hotel_dom = lxml.html.fromstring(hotel_response.text)

                hotel_name = hotel_dom.xpath("//h2[contains(@class,'pp-header__title')]/text()")
                hotel_name = hotel_name[0] if hotel_name else "Unknown"

                hotel_id = hotel_dom.xpath("//input[contains(@name,'hotel_id')]/@value")
                hotel_id = hotel_id[0] if hotel_id else "Unknown"

                try:
                    json_ld = hotel_dom.xpath('//script[@type="application/ld+json" and contains(., "hasMap")]/text()')

                    if json_ld:
                        data = json.loads(json_ld[0])
                        has_map_url = data.get('hasMap', None)
                    lat = has_map_url.split('center=')[1].split('&')[0].split(',')[0]
                    lon = has_map_url.split('center=')[1].split('&')[0].split(',')[1]
                except:
                    lat = ""
                    lon = ""

                try:
                    add = data.get('address', None)
                    if add:
                        postal_code = add.get('postalCode', '')
                        address = add.get('streetAddress', '')
                        country = add.get('addressCountry', '')
                        region = add.get('addressRegion', '')
                except:
                    address = ""

                try:
                    Images = hotel_dom.xpath("//picture//img[contains(@src, 'jpg')]/@src")[0]
                except:
                    Images = ""

                try:
                    Currency = hotel_dom.xpath("//nav[contains(@class,'Header_bar')]//button//text()")[0]
                except:
                    Currency = ""

                room_details, price_list = parse_room_details(hotel_response)
                lowest_price = get_lowest_price(price_list)

                scraped_data.append({
                    "source_url": hotel_url,
                    "hotel_name": hotel_name,
                    "hotel_id": hotel_id,
                    "latitude": lat,
                    "longitude": lon,
                    "address": address,
                    "postal_code": postal_code,
                    "country": country,
                    "region": region,
                    "images": Images,
                    "currency": Currency,
                    "room_details": room_details,
                    "lowest_price": lowest_price
                })

                logging.info(f"Scraped data for hotel: {hotel_name}. and the lowest price is ${lowest_price}")

            except Exception as e:
                logging.error(f"Failed to scrape hotel data from {hotel_url}: {e}")

    except Exception as e:
        logging.error(f"Failed to fetch booking data: {e}")

    return scraped_data

if __name__ == "__main__":

    data = scrape_booking_data()
    save_to_json(data, "booking_output.json")

    logging.info("Scraping process completed.")
