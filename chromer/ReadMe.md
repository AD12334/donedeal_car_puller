# DoneDeal Car Puller

## Project Structure

```
/donedeal_car_puller
    ├── chromer
    │   └── ReadMe.md
    ├── src
    │   ├── main.py
    │   └── utils.py
    ├── tests
    │   └── test_main.py
    └── requirements.txt
```

## Prerequisites
- Python 3.x
- Pip
- Beautiful Soup
- Requests library

## Features
- Scrapes car listings from DoneDeal.com
- Searches by various filters: location, price, type, etc.
- Exports results to CSV format.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/AD12334/donedeal_car_puller.git
   ```
2. Navigate into the project directory:
   ```bash
   cd donedeal_car_puller
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the main script with your desired parameters:
   ```bash
   python src/main.py --location "Dublin" --max_price 20000
   ```
2. The results will be saved in a CSV file in the project root.

## Documentation Sections
- **Contributing:** Guidelines for contributing to the project.
- **License:** Information about the project's license.
- **Contact:** How to reach the project maintainers.

## Conclusion
DoneDeal Car Puller is an efficient tool to help users find and export car listings easily. For more details, check the documentation sections or reach out to the maintainers.