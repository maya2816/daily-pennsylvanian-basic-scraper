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
    """
    Scrapes both the Academics section description paragraph AND the top article headline.
    Returns a string that includes both.
    """
    headers = {
        "User-Agent": "cis3500-scraper"
    }
    req = requests.get("https://www.thedp.com/section/academics", headers=headers)
    loguru.logger.info(f"Request URL: {req.url}")
    loguru.logger.info(f"Request status code: {req.status_code}")

    if req.ok:
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        
        # Try primary selector:
        # Select the <p> immediately following the <h1 class="section-title">
        desc_element = soup.select_one("h1.section-title + p")
        if desc_element:
            desc_text = desc_element.get_text(strip=True)
        else:
            # Fallback: try selecting a <p> that follows a container like "subsection-list"
            desc_element = soup.select_one("div.subsection-list ~ p")
            desc_text = desc_element.get_text(strip=True) if desc_element else ""
        
        # Select the top article headline.
        # This looks inside the first "section-article" for an <h3> with class "standard-link" and then the <a> inside it.
        headline_element = soup.select_one("div.row.section-article h3.standard-link a")
        headline_text = headline_element.get_text(strip=True) if headline_element else ""
        
        # Combine the description and headline into one string.
        data_point = f"Section Description: {desc_text}\nHeadline: {headline_text}"
        loguru.logger.info(f"Data point: {data_point}")
        return data_point
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

    # Load daily event monitor
    loguru.logger.info("Loading daily event monitor")
    dem = daily_event_monitor.DailyEventMonitor(
        "data/daily_pennsylvanian_headlines.json"
    )

    # Run scrape
    loguru.logger.info("Starting scrape")
    try:
        data_point = scrape_data_point()
    except Exception as e:
        loguru.logger.error(f"Failed to scrape data point: {e}")
        data_point = None

    # Save data
    if data_point is not None:
        dem.add_today(data_point)
        dem.save()
        loguru.logger.info("Saved daily event monitor")
        
    # Method to print tree of files/dirs
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

    # Print tree of files/dirs
    print_tree(os.getcwd())

    # Print contents of data file
    loguru.logger.info("Printing contents of data file {}".format(dem.file_path))
    with open(dem.file_path, "r") as f:
        loguru.logger.info(f.read())

    # Finish
    loguru.logger.info("Scrape complete")
    loguru.logger.info("Exiting")