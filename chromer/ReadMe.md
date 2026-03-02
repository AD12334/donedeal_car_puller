# DoneDeal Car Puller

A web scraping tool that automatically extracts car listings from DoneDeal (an Irish online marketplace) using Selenium and Chrome WebDriver.

## Overview

This project uses Selenium WebDriver with Chrome to scrape car listing data from the DoneDeal website. It intelligently extracts car information, processes it, and stores the data in CSV files for further analysis. The tool also captures screenshots of each car listing for reference.

## Features

- **Automated Web Scraping**: Uses Selenium WebDriver to interact with DoneDeal's dynamic content
- **Car Data Extraction**: Automatically extracts:
  - Car make and model
  - Year
  - Engine size
  - Mileage
  - Price
  - Location
  - Time posted
  - Direct link to listing
- **Screenshot Capture**: Takes screenshots of each car listing container for visual reference
- **Data Processing**: Intelligently processes and cleans scraped data
- **CSV Export**: Exports scraped data to CSV files for easy analysis
- **Smart Scrolling**: Implements infinite scroll handling to capture all listings
- **Duplicate Prevention**: Tracks already-seen listings to avoid duplicates

## Project Structure

```
chromer/
├── main.py                 # Main scraping script with core logic
├── cars.csv               # Output file with scraped car data
├── Ford_cars.csv          # Brand-specific car data
├── car_screenshots/       # Directory containing screenshot captures
├── ai_prompt              # AI prompt notes for development
└── ReadMe.md              # Project documentation
```

## Prerequisites

Before running this project, ensure you have the following installed:

### System Requirements
- **Python**: 3.7 or higher
- **Chrome/Chromium**: Any recent version (matching ChromeDriver)
- **Operating System**: Windows, macOS, or Linux

### Python Dependencies
- `selenium` - For web browser automation

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/AD12334/donedeal_car_puller.git
cd donedeal_car_puller/chromer
```

### Step 2: Install Python Dependencies

```bash
pip install selenium
```

Or using requirements.txt (if available):
```bash
pip install -r requirements.txt
```

### Step 3: Download and Setup ChromeDriver

1. **Check your Chrome version**:
   - Open Chrome and go to `chrome://version/`
   - Note the version number

2. **Download ChromeDriver**:
   - Visit [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
   - Download the version matching your Chrome version

3. **Setup ChromeDriver**:
   - **Option A**: Place `chromedriver` in the same directory as `main.py`
   - **Option B**: Add ChromeDriver to your system PATH
   - **Option C**: Specify the path in the script using `Service()`

### Step 4: Verify Installation

```bash
python --version  # Should be 3.7+
pip show selenium  # Should show selenium is installed
```

## Usage

### Basic Usage

```bash
python main.py
```

### With Command-Line Arguments

```bash
python main.py [options]
```

### Running the Scraper

1. Navigate to the project directory:
   ```bash
   cd chromer
   ```

2. Run the main script:
   ```bash
   python main.py
   ```

3. The script will:
   - Launch a Chrome browser window
   - Navigate to DoneDeal listings
   - Begin scraping car data
   - Save results to CSV files
   - Create screenshots in the `car_screenshots/` directory

## How It Works

### Scraping Process

1. **Initialization**: Launches a Chrome WebDriver instance
2. **Navigation**: Navigates to DoneDeal car listings page
3. **Scrolling & Extraction**: 
   - Scrolls through listings dynamically
   - Extracts car information from each listing container
   - Takes screenshots of each car listing
4. **Data Processing**: 
   - Cleans and validates car titles
   - Processes mileage data
   - Validates extracted information
5. **Storage**: 
   - Saves data to CSV file(s)
   - Organizes screenshots in `car_screenshots/` directory

### Web Scraping Strategy

The tool uses Selenium's explicit waits to ensure content is fully loaded before extraction:
- CSS selectors target specific data fields
- Scroll delays prevent missing dynamic content
- Element IDs track processed listings to prevent duplicates

## Core Components

### `Car` Class

A data model representing a single car listing:

```python
Car(name, year, engine_size, mileage, price, location, time_posted, link)
```

**Attributes**:
- `name` (str): Car make and model
- `year` (str): Registration year
- `engine_size` (str): Engine displacement
- `mileage` (str): Mileage in km
- `price` (str): Listed price
- `location` (str): Vehicle location
- `time_posted` (str): When listing was posted
- `link` (str): URL to the listing

### `extract_car_info(container, driver)`

Extracts information from a single car listing container element.

**Parameters**:
- `container`: WebElement containing car listing HTML
- `driver`: Selenium WebDriver instance

**Returns**: `Car` object or `None` if extraction fails

**Process**:
- Uses CSS selectors to locate data fields
- Processes and validates extracted data
- Takes a screenshot of the listing
- Returns a Car object with all extracted information

### `scroll_and_extract(driver, container_selector)`

Implements infinite scroll scraping logic.

**Parameters**:
- `driver`: Selenium WebDriver instance
- `container_selector`: CSS selector for car listing containers

**Returns**: List of `Car` objects

**Features**:
- Continuously scrolls the page to load more listings
- Extracts all visible car listings
- Prevents duplicate extraction using a `seen` set
- Tracks scroll height to detect when all content is loaded

## Output Files

### CSV Files
- **cars.csv**: Main output file containing all scraped car listings with columns:
  - Year, Name, Engine Size, Mileage, Price, Location, Time Posted, Link
- **Ford_cars.csv**: Filtered data for specific car brands (example)

### Screenshots
- **car_screenshots/**: Directory containing PNG screenshots
  - Named based on listing URL for easy reference
  - Useful for visual verification and manual review

## Data Processing

The script includes intelligent processing for:

### Car Title Processing
- Validates car make and model information
- Filters out invalid or irrelevant entries
- Standardizes naming conventions

### Mileage Processing
- Extracts numeric mileage values
- Handles different mileage formats
- Converts to standardized units (km)

## Error Handling

The script includes robust error handling:

- **Try-Catch Blocks**: Graceful handling of extraction failures
- **Missing Data**: Fallback values for missing metadata fields
- **Duplicate Prevention**: Tracking mechanism to avoid re-processing listings
- **Invalid Data**: Filtering mechanism for malformed or invalid listings
- **Load Failures**: Automatic retry with explicit waits

## Configuration

### CSS Selectors (May need updates if DoneDeal changes their HTML)

The following CSS selectors are used to extract data:
```
.LineClampstyled__Container-sc-1mg7xqt-0.kZaNUJ.SearchCardstyled__Title-sc-7ibu2h-6.igUdmi  # Title
[class*='Price']                                                                               # Price
[class*='MetaInfoItem']                                                                        # Metadata
```

### Screenshot Directory

Screenshots are saved to `car_screenshots/` directory. Ensure your system has write permissions to this location.

## Troubleshooting

### Common Issues

**Issue**: `ChromeDriver not found`
- **Solution**: Ensure ChromeDriver is in the same directory as main.py or add it to PATH

**Issue**: `No module named 'selenium'`
- **Solution**: Run `pip install selenium`

**Issue**: No data is being extracted
- **Cause**: DoneDeal may have changed their HTML structure
- **Solution**: Inspect the website and update CSS selectors in the code

**Issue**: Screenshots are not being saved
- **Solution**: Check that the script has write permissions in the project directory

**Issue**: Chrome crashes or refuses to start
- **Solution**: Update ChromeDriver to match your Chrome version

## Requirements File

To create a requirements.txt file for easy dependency installation:

```bash
pip freeze > requirements.txt
```

Contents should include:
```
selenium>=4.0.0
```

## Notes

- The script uses explicit waits and scrolling delays to ensure page content loads
- CSS selectors are specific to DoneDeal's current website structure
- If DoneDeal's HTML structure changes, selectors will need updating
- Screenshots are named based on the listing URL for easy reference
- Consider adding delays to avoid overwhelming the server

## Performance Tips

- Adjust scroll delays if pages load slowly (increase) or quickly (decrease)
- Consider implementing headless mode for faster execution (no visible browser window)
- Use filtering to focus on specific car types or price ranges

## License

[Add appropriate license]

## Author

Created by AD12334

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Disclaimer

This tool is for **educational purposes only**. Please ensure you comply with:
- DoneDeal's Terms of Service
- DoneDeal's robots.txt file
- All applicable laws regarding web scraping in your jurisdiction

Unauthorized scraping may violate terms of service. Use responsibly.