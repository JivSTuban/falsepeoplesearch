# TruePeopleSearch API

A RESTful API for TruePeopleSearch.com that allows searching by name, address, or phone number. This API uses automated Chrome browser to extract contact information and returns it in a structured JSON format.

## Features

- **Multiple Search Types**:
  - Search by name (with optional city/state)
  - Search by address
  - Search by phone number
- **Detailed Results**:
  - Contact information (phones, emails)
  - Address details
  - Age information
  - Person links
- **Batch Processing**:
  - Process multiple queries in a single request

## API Usage

### Endpoint

```
POST /search
```

### Request Format

The API accepts a JSON body with the following structure:

```json
{
  "name": [
    "James E Whitsitt",
    "Amalia Castillo; Dallas, TX 75228"
  ],
  "street_citystatezip": [
    "3828 Double Oak Ln; Irving, TX 75061",
    "1171 S 2nd St; Cameron, TX 76520"
  ],
  "phone_number": [
    "(214)349-3972",
    "(956) 536-1441"
  ],
  "max_results": 1
}
```

- **name**: Array of names to search for. You can include city/state after a semicolon.
- **street_citystatezip**: Array of addresses to search for. Format as "Street; City, State ZIP".
- **phone_number**: Array of phone numbers to search for.
- **max_results**: Maximum number of results to return per query (default: 1).

### Response Format

The API returns a JSON object with results grouped by search type:

```json
{
  "name_results": [
    {
      "Search Option": "Name Search",
      "Input Given": "James E Whitsitt",
      "First Name": "James",
      "Last Name": "E Whitsitt Jr",
      "Age": "81",
      "Lives in": "Dallas, TX",
      "Street Address": "2551 Pinebluff Dr",
      "Address Locality": "Dallas",
      "Address Region": "TX",
      "Postal Code": "75xxx",
      "Country Name": "Dallas County",
      "Email 1": "xxx@yahoo.com",
      "Email 2": "qjameds.xxx@msn.com",
      "Email 3": "xxx@hotmail.com",
      "Email 4": "",
      "Email 5": "",
      "Phone 1": "(214) xxx-3972",
      "Phone 1 Type": "Landline",
      "Phone 1 Last Reported": "Last reported Jan 2025",
      "Phone 1 Provider": "Southwestern Bell Telephone Company",
      "Phone 2": "(214) xxx-3872",
      "Phone 2 Type": "Wireless",
      "Phone 2 Last Reported": "Last reported Apr 2021",
      "Phone 2 Provider": "AT&T",
      "Phone 3": "(214) xxx-5304",
      "Phone 3 Type": "Landline",
      "Phone 3 Last Reported": "Last reported Oct 2016",
      "Phone 3 Provider": "Southwestern Bell Telephone Company",
      "Phone 4": "(214) xxx-9044",
      "Phone 4 Type": "Landline",
      "Phone 4 Last Reported": "Last reported Jul 2001",
      "Phone 4 Provider": "Southwestern Bell Telephone Company",
      "Phone 5": "(214) xxx-9553",
      "Phone 5 Type": "Landline",
      "Phone 5 Last Reported": "Last reported Oct 2016",
      "Phone 5 Provider": "Southwestern Bell Telephone Company",
      "Person Link": "https://www.truepeoplesearch.com/find/person/pn8u4l0n8nuruu09l04l"
    }
  ],
  "address_results": [...],
  "phone_results": [...]
}
```

## Running Locally

1. Set up a Python environment:

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate     # Linux/macOS
venv\Scripts\activate        # Windows

# Install requirements
pip install -r requirements.txt
```

2. Run the API server:

```bash
python api.py
```

The server will start on http://localhost:5000

## Deploying to Render.com

1. Create a new Web Service on Render.com

2. Connect your GitHub repository

3. Configure the service:
   - **Name**: truepeoplesearch-api (or your preferred name)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn "api:app"`

4. Add the following environment variables:
   - `CHROME_HEADLESS`: true
   - `CHROME_TIMEOUT`: 30

5. Deploy the service

Render.com's servers are located in the US (Oregon), which means you don't need to use a VPN to access TruePeopleSearch.com.

## Notes

- The API uses Selenium with Chrome to interact with TruePeopleSearch.com
- CloudFlare protection is handled automatically
- Rate limiting is implemented to avoid being blocked
- For production use, consider adding authentication to your API

## Troubleshooting

- If you encounter CloudFlare issues, try adjusting the delay settings in the TruePeopleSearchAPI class
- Make sure Chrome is installed and up to date
- Check the logs for detailed error messages