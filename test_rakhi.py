from app import app, db, Donor, geocode_address_free, calculate_distance_free

with app.app_context():
    # Get Rakhi's donor record
    rakhi = Donor.query.filter_by(name="Rakhi Dalabanjan").first()
    
    if rakhi:
        print(f"Rakhi's location: '{rakhi.location}'")
        print(f"Geocoded before: {rakhi.geocoded}")
        print(f"Latitude: {rakhi.latitude}")
        print(f"Longitude: {rakhi.longitude}")
        
        # Test geocoding her location
        geocode_result = geocode_address_free(rakhi.location)
        print(f"\nGeocoding '{rakhi.location}':")
        print(f"Success: {geocode_result['success']}")
        if geocode_result['success']:
            print(f"Latitude: {geocode_result['latitude']}")
            print(f"Longitude: {geocode_result['longitude']}")
            
            # Test distance from 'hubli' search coordinates
            hubli_result = geocode_address_free('hubli')
            if hubli_result['success']:
                distance = calculate_distance_free(
                    hubli_result['latitude'], hubli_result['longitude'],
                    geocode_result['latitude'], geocode_result['longitude']
                )
                print(f"\nDistance from Hubli center: {distance} km")
                print(f"Within 10km radius: {distance <= 10 if distance else False}")
                print(f"Within 100km radius: {distance <= 100 if distance else False}")
        else:
            print("Failed to geocode Rakhi's location")
    else:
        print("Rakhi not found in database")