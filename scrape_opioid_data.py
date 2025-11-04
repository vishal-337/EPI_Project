import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

state_fips = {
    'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06',
    'CO': '08', 'CT': '09', 'DE': '10', 'DC': '11', 'FL': '12',
    'GA': '13', 'HI': '15', 'ID': '16', 'IL': '17', 'IN': '18',
    'IA': '19', 'KS': '20', 'KY': '21', 'LA': '22', 'ME': '23',
    'MD': '24', 'MA': '25', 'MI': '26', 'MN': '27', 'MS': '28',
    'MO': '29', 'MT': '30', 'NE': '31', 'NV': '32', 'NH': '33',
    'NJ': '34', 'NM': '35', 'NY': '36', 'NC': '37', 'ND': '38',
    'OH': '39', 'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44',
    'SC': '45', 'SD': '46', 'TN': '47', 'TX': '48', 'UT': '49',
    'VT': '50', 'VA': '51', 'WA': '53', 'WV': '54', 'WI': '55',
    'WY': '56'
}

all_data = []

for year in range(2006, 2019):
    url = f"https://archive.cdc.gov/www_cdc_gov/drugoverdose/rxrate-maps/state{year}.html"
    print(f"Scraping data for year {year}...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        table = soup.find('table')
        
        if table:
            rows = table.find_all('tr')[1:]
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    state_name = cols[0].text.strip()
                    state_abbrev = cols[1].text.strip()
                    rate = cols[2].text.strip()
                    
                    fips = state_fips.get(state_abbrev, '')
                    
                    all_data.append({
                        'YEAR': year,
                        'STATE_NAME': state_name,
                        'STATE_ABBREV': state_abbrev,
                        'STATE_FIPS': fips,
                        'opioid_dispensing_rate': rate,
                        'Opioid Dispensing Rate (per 100 persons)': rate
                    })
            
            print(f"  ✓ Successfully scraped {len(rows)} states for {year}")
        else:
            print(f"  ✗ No table found for {year}")
    
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error fetching data for {year}: {e}")
    
    time.sleep(1)

df = pd.DataFrame(all_data)

output_path = '/Users/vishal/Desktop/EPI_Project/data/State_Opioid_Dispensing_Rates_2006_2018.csv'
df.to_csv(output_path, index=False)

print(f"\n✓ Data saved to: {output_path}")
print(f"Total records: {len(df)}")
print(f"Years covered: {df['YEAR'].min()} - {df['YEAR'].max()}")
print(f"\nFirst few rows:")
print(df.head())

