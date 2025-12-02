import pandas as pd
import re
from pathlib import Path

# Dictionary to map state abbreviations to full names
STATE_NAMES = {
    'AK': 'Alaska', 'AL': 'Alabama', 'AR': 'Arkansas', 'AZ': 'Arizona',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DC': 'District of Columbia',
    'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii',
    'IA': 'Iowa', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'MA': 'Massachusetts',
    'MD': 'Maryland', 'ME': 'Maine', 'MI': 'Michigan', 'MN': 'Minnesota',
    'MO': 'Missouri', 'MS': 'Mississippi', 'MT': 'Montana', 'NC': 'North Carolina',
    'ND': 'North Dakota', 'NE': 'Nebraska', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NV': 'Nevada', 'NY': 'New York', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island',
    'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas',
    'UT': 'Utah', 'VA': 'Virginia', 'VT': 'Vermont', 'WA': 'Washington',
    'WI': 'Wisconsin', 'WV': 'West Virginia', 'WY': 'Wyoming'
}

def parse_txt_file(filepath, year):
    """Parse a txt file and extract county opioid data"""
    print(f"Processing {filepath} for year {year}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the data section - look for lines with county data
    lines = content.split('\n')
    
    data_rows = []
    found_header = False
    format_type = None  # 'county_first', 'state_first', or 'county_first_no_comma'
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
            
        # Check if this is a data line with tab-separated values
        parts = line.split('\t')
        
        if len(parts) >= 4:
            # Check for header row and determine format
            # First, check if this contains "County" and "FIPS" which indicates a header
            if 'FIPS' in parts[2] or 'FIPS' in line:
                # This is a header row
                if 'County' in parts[0] and 'State' in parts[1]:
                    # Check if first column has commas in data (indicates county_first format)
                    # We'll determine this dynamically
                    found_header = True
                    format_type = 'county_first_no_comma'  # Default, will adjust if needed
                elif 'State' in parts[0] and 'County' in parts[1]:
                    # Format: State, County, FIPS, Rate (2017)
                    found_header = True
                    format_type = 'state_first'
                continue
            
            if not found_header or format_type is None:
                continue
            
            # On first data row with county_first_no_comma, check if it has comma
            if format_type == 'county_first_no_comma' and ', ' in parts[0]:
                format_type = 'county_first'
            
            # Parse based on format
            if format_type == 'county_first':
                county_state = parts[0].strip()  # e.g., "Anchorage, AK"
                state_abbrev = parts[1].strip()
                fips_code = parts[2].strip()
                rate = parts[3].strip()
                
                # Extract county name from first column
                if ', ' in county_state:
                    county_name = county_state.split(', ')[0].strip()
                else:
                    continue
                    
            elif format_type == 'state_first':
                state_abbrev = parts[0].strip()
                county_name = parts[1].strip()
                fips_code = parts[2].strip()
                rate = parts[3].strip()
                
            else:  # format_type == 'county_first_no_comma'
                county_name = parts[0].strip()
                state_abbrev = parts[1].strip()
                fips_code = parts[2].strip()
                rate = parts[3].strip()
            
            # Skip if not valid state abbreviation
            if state_abbrev not in STATE_NAMES:
                continue
            
            # Handle missing data (represented as '–' or empty)
            if rate == '–' or rate == '' or rate == 'Data unavailable':
                rate = 'Data unavailable'
            
            # Create standardized county name with proper capitalization
            county_name_parts = county_name.split()
            county_name_proper = ' '.join(word.capitalize() if word.upper() == word else word for word in county_name_parts)
            
            # Create standardized county name with suffix
            county_full = county_name_proper
            # Add "County" suffix if it doesn't have a proper suffix
            if not any(suffix in county_full for suffix in ['County', 'Census Area', 'Borough', 'Parish', 'City', 'Municipality']):
                county_full = f"{county_name_proper} County"
            
            # Ensure FIPS code is formatted correctly
            try:
                # Remove leading zeros for storage, keep as string
                fips_int = int(fips_code)
                fips_code = str(fips_int)
            except:
                continue
            
            # Create FullGeoName matching the CSV format
            full_geo_name = f"{state_abbrev}, {county_name_proper}"
            
            data_rows.append({
                'FullGeoName': full_geo_name,
                'YEAR': year,
                'STATE_NAME': STATE_NAMES[state_abbrev],
                'STATE_ABBREV': state_abbrev,
                'COUNTY_NAME': county_full,
                'STATE_COUNTY_FIP_U': fips_code,
                'opioid_dispensing_rate': rate
            })
    
    print(f"  Found {len(data_rows)} data rows")
    return data_rows

# Process all year files
all_data = []

for year in range(2006, 2019):  # 2006 to 2018
    txt_file = Path(f'{year}.txt')
    if txt_file.exists():
        year_data = parse_txt_file(txt_file, year)
        all_data.extend(year_data)
    else:
        print(f"Warning: {txt_file} not found")

# Create DataFrame from parsed data
new_df = pd.DataFrame(all_data)

print(f"\nTotal rows parsed from txt files: {len(new_df)}")

# Load existing CSV
existing_df = pd.read_csv('County Opioid Dispensing Rates.csv')
print(f"Existing CSV has {len(existing_df)} rows")

# Combine the dataframes
combined_df = pd.concat([new_df, existing_df], ignore_index=True)

# Sort by year and state
combined_df = combined_df.sort_values(['YEAR', 'STATE_ABBREV', 'COUNTY_NAME'])

print(f"Combined data has {len(combined_df)} rows")

# Save to new CSV
output_file = 'County Opioid Dispensing Rates_Complete.csv'
combined_df.to_csv(output_file, index=False)

print(f"\nData successfully merged and saved to: {output_file}")
print(f"Year range: {combined_df['YEAR'].min()} - {combined_df['YEAR'].max()}")
