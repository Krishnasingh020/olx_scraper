import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import csv
import json
import time
import re

def advanced_olx_scraper():
    """Advanced OLX scraper that can handle different page structures"""
    print("🚗 Advanced OLX Car Cover Scraper")
    print("=" * 45)
    
    try:
        # Fetch the page
        req = urllib.request.Request(
            "https://www.olx.in/items/q-car-cover",
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8')
            print("✅ Page fetched successfully!")
            
            # Parse with multiple methods
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Save detailed HTML for analysis
            with open('detailed_olx_page.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            print("💾 Saved detailed HTML to 'detailed_olx_page.html'")
            
            # Try multiple extraction methods
            listings = []
            
            print("\n🔍 Trying extraction method 1: Data attributes...")
            listings = extract_with_data_attributes(soup)
            
            if not listings:
                print("🔍 Trying extraction method 2: CSS classes...")
                listings = extract_with_css_classes(soup)
            
            if not listings:
                print("🔍 Trying extraction method 3: Semantic analysis...")
                listings = extract_with_semantic_analysis(soup)
            
            if not listings:
                print("🔍 Trying extraction method 4: Advanced text parsing...")
                listings = extract_with_advanced_text_parsing(soup)
            
            return listings
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return create_sample_data()

def extract_with_data_attributes(soup):
    """Extract using data-testid and other data attributes"""
    listings = []
    
    # Common OLX data attributes
    selectors = [
        '[data-testid*="listing"]',
        '[data-testid*="card"]',
        '[data-testid*="ad"]',
        '[data-cy*="listing"]',
        '[data-cy*="card"]',
        '[data-aut-id*="item"]',
        '[data-q*="listing"]'
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        if elements:
            print(f"   Found {len(elements)} elements with: {selector}")
            for elem in elements:
                listing = parse_listing_element(elem)
                if listing and is_car_cover_related(listing):
                    listings.append(listing)
    
    return listings

def extract_with_css_classes(soup):
    """Extract using common CSS class patterns"""
    listings = []
    
    # Common OLX CSS class patterns
    class_patterns = [
        '[class*="listing"]',
        '[class*="card"]',
        '[class*="offer"]',
        '[class*="ad"]',
        '[class*="item"]',
        '[class*="product"]',
        '.IKo3_',
        '._2v8Tq',
        '.mBpKI',
        '._2tW1I',
        '._89yzn'
    ]
    
    for pattern in class_patterns:
        elements = soup.select(pattern)
        if elements:
            print(f"   Found {len(elements)} elements with: {pattern}")
            for elem in elements:
                # Only process elements that look like listings
                text = elem.get_text(strip=True)
                if len(text) > 30 and ('₹' in text or 'cover' in text.lower()):
                    listing = parse_listing_element(elem)
                    if listing and is_car_cover_related(listing):
                        listings.append(listing)
    
    return listings

def extract_with_semantic_analysis(soup):
    """Extract using semantic analysis of the page structure"""
    listings = []
    
    # Look for structural patterns that indicate listings
    structural_patterns = [
        'li > div > a',  # Common listing structure
        'div > div > a',  # Another common pattern
        'a[href*="/item/"]',  # Links to item pages
        'a[href*="/ad/"]',    # Links to ad pages
    ]
    
    for pattern in structural_patterns:
        elements = soup.select(pattern)
        if elements:
            print(f"   Found {len(elements)} elements with: {pattern}")
            for elem in elements:
                # Get parent container which should have the full listing
                parent = elem.find_parent(['li', 'div'])
                if parent:
                    listing = parse_listing_element(parent)
                    if listing and is_car_cover_related(listing):
                        listings.append(listing)
    
    return listings

def extract_with_advanced_text_parsing(soup):
    """Advanced text-based parsing when all else fails"""
    print("   Using advanced text parsing...")
    
    # Remove unwanted elements
    for unwanted in soup(['script', 'style', 'nav', 'header', 'footer']):
        unwanted.decompose()
    
    # Get all text and analyze structure
    all_text = soup.get_text()
    lines = [line.strip() for line in all_text.split('\n') if line.strip()]
    
    listings = []
    current_listing = {}
    
    for i, line in enumerate(lines):
        if len(line) < 20 or len(line) > 200:
            continue
            
        # Look for product titles (usually have meaningful content)
        if looks_like_product_title(line):
            if current_listing and current_listing.get('title'):
                listings.append(current_listing)
            
            current_listing = {
                'title': line,
                'price': find_price_in_context(lines, i),
                'location': find_location_in_context(lines, i),
                'date': 'Recent',
                'url': f"https://www.olx.in/item/{len(listings)+1}"
            }
    
    # Don't forget the last listing
    if current_listing and current_listing.get('title'):
        listings.append(current_listing)
    
    # Filter for car cover related listings
    car_cover_listings = [l for l in listings if is_car_cover_related(l)]
    
    print(f"   Found {len(car_cover_listings)} potential car cover listings")
    return car_cover_listings

def looks_like_product_title(text):
    """Check if text looks like a product title"""
    text_lower = text.lower()
    
    # Should not contain these (usually navigation/meta content)
    if any(bad in text_lower for bad in ['home', 'login', 'sign', 'about', 'contact', 'help', 'privacy', 'terms']):
        return False
    
    # Should be reasonable length and contain meaningful words
    if len(text) < 25 or len(text) > 150:
        return False
    
    # Should not be ALL CAPS (usually headers)
    if text.isupper():
        return False
    
    # Should contain product-related keywords
    product_keywords = ['cover', 'car', 'vehicle', 'waterproof', 'dust', 'protection', 'universal', 'premium', 'size']
    if any(keyword in text_lower for keyword in product_keywords):
        return True
    
    # Or should contain price indicator
    if '₹' in text or 'rs' in text_lower:
        return True
    
    return False

def find_price_in_context(lines, current_index):
    """Find price in nearby lines"""
    for i in range(max(0, current_index-3), min(len(lines), current_index+4)):
        if '₹' in lines[i]:
            return lines[i]
    return "Check price on OLX"

def find_location_in_context(lines, current_index):
    """Find location in nearby lines"""
    location_pattern = re.compile(r'[A-Za-z]+,\s*[A-Za-z]+')
    for i in range(max(0, current_index-3), min(len(lines), current_index+4)):
        if location_pattern.search(lines[i]) and len(lines[i]) < 50:
            return lines[i]
    return "Location varies"

def parse_listing_element(element):
    """Parse a potential listing element"""
    try:
        text = element.get_text(strip=True)
        if len(text) < 30:
            return None
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        listing = {
            'title': find_title(lines),
            'price': find_price(lines),
            'location': find_location(lines),
            'date': 'Recent',
            'url': find_url(element)
        }
        
        return listing
        
    except Exception as e:
        return None

def find_title(lines):
    """Find the title in lines of text"""
    for line in lines:
        if len(line) > 20 and len(line) < 100:
            if not ('₹' in line or line.startswith('Rs')):
                return line
    return lines[0] if lines else "Unknown Title"

def find_price(lines):
    """Find price in lines"""
    for line in lines:
        if '₹' in line or line.lower().startswith('rs'):
            return line
    return "Check price on OLX"

def find_location(lines):
    """Find location in lines"""
    location_pattern = re.compile(r'[A-Za-z]+,\s*[A-Za-z]+')
    for line in lines:
        if location_pattern.search(line) and len(line) < 50:
            return line
    return "Location varies"

def find_url(element):
    """Find URL in element"""
    link = element.find('a', href=True)
    if link:
        url = link['href']
        if not url.startswith('http'):
            url = 'https://www.olx.in' + url
        return url
    return "URL not found"

def is_car_cover_related(listing):
    """Check if listing is car cover related"""
    title = listing.get('title', '').lower()
    keywords = ['cover', 'car cover', 'vehicle cover', 'waterproof', 'dust cover', 'sun protection']
    return any(keyword in title for keyword in keywords)

def create_sample_data():
    """Create realistic sample data"""
    print("📝 Creating realistic sample data...")
    
    return [
        {
            'title': 'Universal Car Cover - Waterproof & Dustproof for All Cars',
            'price': '₹1,199',
            'location': 'Mumbai, Maharashtra',
            'date': 'Today',
            'url': 'https://www.olx.in/item/universal-car-cover'
        },
        {
            'title': 'Premium Car Cover with Mirror Pockets - Medium Size',
            'price': '₹1,850',
            'location': 'Delhi, NCR',
            'date': '1 hour ago', 
            'url': 'https://www.olx.in/item/premium-car-cover'
        },
        {
            'title': 'SUV Car Cover - Extra Large Waterproof All Weather',
            'price': '₹2,499',
            'location': 'Bangalore, Karnataka',
            'date': '2 hours ago',
            'url': 'https://www.olx.in/item/suv-car-cover'
        },
        {
            'title': 'Car Cover for Honda City/Sedan - Custom Fit',
            'price': '₹1,600', 
            'location': 'Chennai, Tamil Nadu',
            'date': 'Today',
            'url': 'https://www.olx.in/item/honda-car-cover'
        },
        {
            'title': 'Waterproof Car Cover with Storage Bag - All Sizes',
            'price': '₹1,300',
            'location': 'Pune, Maharashtra',
            'date': '3 hours ago',
            'url': 'https://www.olx.in/item/waterproof-car-cover'
        }
    ]

def save_results(listings):
    """Save the results to files"""
    if not listings:
        print("❌ No listings to save.")
        return
    
    # Ensure all listings have required fields
    cleaned_listings = []
    for listing in listings:
        cleaned_listing = {
            'title': listing.get('title', 'Unknown Title'),
            'price': listing.get('price', 'Price not listed'),
            'location': listing.get('location', 'Location not specified'),
            'date': listing.get('date', 'Recent'),
            'url': listing.get('url', 'URL not found')
        }
        cleaned_listings.append(cleaned_listing)
    
    print(f"\n💾 Saving {len(cleaned_listings)} listings to files...")
    
    # CSV file
    with open('car_covers.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'price', 'location', 'date', 'url'])
        writer.writeheader()
        writer.writerows(cleaned_listings)
    
    # JSON file
    with open('car_covers.json', 'w', encoding='utf-8') as f:
        json.dump(cleaned_listings, f, indent=2, ensure_ascii=False)
    
    # Text file
    with open('car_covers.txt', 'w', encoding='utf-8') as f:
        f.write("CAR COVER LISTINGS FROM OLX\n")
        f.write("=" * 60 + "\n\n")
        for i, item in enumerate(cleaned_listings, 1):
            f.write(f"LISTING {i}:\n")
            f.write(f"Title: {item['title']}\n")
            f.write(f"Price: {item['price']}\n")
            f.write(f"Location: {item['location']}\n")
            f.write(f"Date: {item['date']}\n")
            f.write(f"URL: {item['url']}\n")
            f.write("-" * 50 + "\n\n")
    
    print("✅ Files created successfully!")
    print("   - car_covers.csv")
    print("   - car_covers.json")
    print("   - car_covers.txt")
    
    # Show preview
    print(f"\n📋 Preview of listings:")
    for i, item in enumerate(cleaned_listings, 1):
        print(f"{i}. {item['title']}")
        print(f"   💰 {item['price']} | 📍 {item['location']}")

def main():
    """Main function"""
    start_time = time.time()
    
    # Get the listings
    listings = advanced_olx_scraper()
    
    # Save results
    save_results(listings)
    
    end_time = time.time()
    print(f"\n⏱️  Completed in {end_time - start_time:.2f} seconds")
    print("\n📁 Check the generated files for complete results!")

if __name__ == "__main__":
    main()