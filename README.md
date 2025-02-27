# DAILY-PENNSYLVANIAN-SCRAPER

This is a modified version of the original scraper.

## Changes Made

1. **Updated URL**  
   The scraper now requests data from [https://www.thedp.com/section/academics](https://www.thedp.com/section/academics) instead of [https://www.thedp.com](https://www.thedp.com). This focuses our data collection on academic content.

2. **Scrape the Section Description**  
   The scraper extracts the Academics section description by selecting the `<p>` element immediately following the `<h1 class="section-title">`. This paragraph provides a brief overview of the Academics section content.

3. **Scrape the Top Headline**  
   The scraper uses a CSS selector to capture the top article headline from the Academics section. The headline is extracted from the `<a>` tag within the first `<h3 class="standard-link">` element in the section.

4. **Combine the Data**  
   The section description and the top headline are concatenated into a single string and saved to a JSON file. This allows us to track both pieces of information over time.

## GitHub Actions Schedule
I modified the schedule to run twice a day using the expression `0 8,20 * * *`, which triggers the workflow at both 8 AM and 8 PM UTC. This change helps us collect data more frequently, ensuring our scraper remains robust and up-to-date throughout the semester.
