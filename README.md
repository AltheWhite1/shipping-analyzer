# 📦 Shipping Cost Analyzer

A Streamlit dashboard to match shipping costs with Shopify orders and analyze logistics performance.

## Features

- **Auto-matching**: Joins shipping costs to Shopify orders via tracking number
- **Currency conversion**: RMB → USD at 0.139 rate
- **Country translation**: Chinese → English country names
- **Issues tracker**: Dedicated tab showing:
  - Unmatched shipments (tracking in shipping file but not Shopify)
  - Unmatched orders (4PX tracking in Shopify without shipping cost)
  - Multi-tracking orders (same order with multiple packages)
  - Country mismatches between files
- **Analytics dashboard**:
  - Shipping cost as % of net payout
  - Average cost per country
  - Outliers (highest shipping costs)
- **Export**: Download merged data as Excel

## Setup

### Option 1: Local (your computer)

```bash
# Install Python 3.10+ if not installed
# Then run:
pip install -r requirements.txt
streamlit run app.py
```

Opens in your browser at http://localhost:8501

### Option 2: Cloud hosting (access from anywhere)

Deploy to [Streamlit Cloud](https://streamlit.io/cloud) for free:
1. Push this folder to a GitHub repo
2. Connect to Streamlit Cloud
3. Deploy

## File Requirements

### Shipping Costs (Excel)
Required columns:
- `物流单号` - Tracking number
- `收货时间` - Ship date  
- `总金额` - Total cost (RMB)

Optional columns used if present:
- `国家/计费分区` - Country (Chinese)
- `计费重` - Weight (kg)

### Shopify Export (CSV)
Required columns:
- `Order` - Order number
- `Tracking number` - Tracking number
- `Net payout` - Order value (USD)
- `Shipping country` - Destination country

Optional columns:
- `Cost` - Product cost
- `Order created at date` - Order date

## Customization

### Change exchange rate
Edit `RMB_TO_USD` in `app.py`:
```python
RMB_TO_USD = 0.139  # Change this value
```

### Add more country translations
Add to the `COUNTRY_MAP` dictionary in `app.py`:
```python
COUNTRY_MAP = {
    '美国': 'United States',
    # Add more here...
}
```
