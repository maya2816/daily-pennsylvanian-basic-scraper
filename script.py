"""
Scrapes a headline from The Daily Pennsylvanian website and saves it to a 
JSON file that tracks headlines over time.
"""

import json
import os
import sys

import daily_event_monitor

import bs4
import requests
import loguru


def scrape_data_point():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/88.0.4324.96 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }
    req = requests.get("https://www.thedp.com", headers=headers)
    loguru.logger.info(f"Request URL: {req.url}")
    loguru.logger.info(f"Request status code: {req.status_code}")

    if req.ok:
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        # Modified rule: look for the 'Most Read' section
        most_read_section = soup.find("ul", class_="most-read")
        if most_read_section:
            target_element = most_read_section.find("a")
        else:
            target_element = None

        data_point = "" if target_element is None else target_element.text.strip()
        loguru.logger.info(f"Data point: {data_point}")
        return data_point
    else:
        loguru.logger.error("Request failed; returning empty string.")
        return ""


if __name__ == "__main__":

    # Setup logger to track runtime
    loguru.logger.add("scrape.log", rotation="1 day")

    # Create data dir if needed
    loguru.logger.info("Creating data directory if it does not exist")
    try:
        os.makedirs("data", exist_ok=True)
    except Exception as e:
        loguru.logger.error(f"Failed to create data directory: {e}")
        sys.exit(1)

    # Ensure the data file exists BEFORE loading the event monitor
    data_file = "data/daily_pennsylvanian_headlines.json"
    if not os.path.exists(data_file):
        loguru.logger.info(f"Data file {data_file} not found. Creating an empty JSON file.")
        with open(data_file, "w") as f:
            json.dump({}, f)

    # Load daily event monitor
    loguru.logger.info("Loading daily event monitor")
    dem = daily_event_monitor.DailyEventMonitor(data_file)

    # Run scrape
    loguru.logger.info("Starting scrape")
    try:
        data_point = scrape_data_point()
    except Exception as e:
        loguru.logger.error(f"Failed to scrape data point: {e}")
        data_point = None

    # Save data
    if data_point is not None and data_point != "":
        dem.add_today(data_point)
        dem.save()
        loguru.logger.info("Saved daily event monitor")
    else:
        loguru.logger.warning("No data scraped; nothing to save.")

    def print_tree(directory, ignore_dirs=[".git", "__pycache__"]):
        loguru.logger.info(f"Printing tree of files/dirs at {directory}")
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            level = root.replace(directory, "").count(os.sep)
            indent = " " * 4 * (level)
            loguru.logger.info(f"{indent}+--{os.path.basename(root)}/")
            sub_indent = " " * 4 * (level + 1)
            for file in files:
                loguru.logger.info(f"{sub_indent}+--{file}")

    print_tree(os.getcwd())

    loguru.logger.info(f"Printing contents of data file {dem.file_path}")
    with open(dem.file_path, "r") as f:
        loguru.logger.info(f.read())

    # Finish
    loguru.logger.info("Scrape complete")
    loguru.logger.info("Exiting")