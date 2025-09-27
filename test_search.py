from app import app, geocode_address_free

with app.app_context():
    # Test geocoding for 'hubli'
    result = geocode_address_free('hubli')
    print("Geocoding result for 'hubli':")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Latitude: {result['latitude']}")
        print(f"Longitude: {result['longitude']}")
    else:
        print("Geocoding failed - would use text search")
    
    print("\n" + "="*50)
    
    # Test the text matching logic
    location = "hubli"
    donor_location = "prashant nagar hubli "
    
    location_lower = location.lower().strip()
    donor_location_lower = donor_location.lower().strip()
    
    print(f"Search location: '{location_lower}'")
    print(f"Donor location: '{donor_location_lower}'")
    print(f"'{location_lower}' in '{donor_location_lower}': {location_lower in donor_location_lower}")
    print(f"'{donor_location_lower}' in '{location_lower}': {donor_location_lower in location_lower}")
    
    words = location_lower.split()
    print(f"Words from search: {words}")
    word_matches = [word in donor_location_lower for word in words if len(word) > 2]
    print(f"Word matches: {word_matches}")
    print(f"Any word match: {any(word_matches)}")