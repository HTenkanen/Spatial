__author__ = 'tenkahen'
# -*- coding: utf-8 -*-
import geocoder, webbrowser, warnings, time
from shapely.geometry import Point
import pandas as pd
import geopandas as gpd

def geocode(location, provider, display_map=False):

    # Try to find the location 10 times before raising the warning and returning coordinates (0.0, 0.0)
    i = 0
    while True:
        if provider == 'google':
            geo = geocoder.google(location)
        elif provider == 'nokia':
            geo = geocoder.nokia(location)
        elif provider == 'osm':
            geo = geocoder.osm(location)
        elif provider == 'bing':
            geo = geocoder.bing(location)
        elif provider == 'tomtom':
            geo = geocoder.tomtom(location)

        if geo.json['status'] == 'OK' or i == 10:
            break
        i+=1

    print geo.json

    if display_map == True:
        #Check if address is a coordinate pair
        if location.replace(',', '').replace('.', '').replace('-', '').isdigit():
            url = "http://maps.google.com/?q=%s" % geo.address
        else:
            url = "http://www.google.com/maps/place/%s,%s" % (geo.lat, geo.lng)
        webbrowser.open(url)

    if geo.json['status'] == 'OK':
        #time.sleep(0.5) # Try to avoid the rate limit
        return geo.json
    else:
        warn = 'WARNING: %s was not found! Coordinates (0.0, 0.0) was returned instead.' % location
        warnings.warn(warn)
        #time.sleep(0.5) # Try to avoid the rate limit
        return {'lat': 0.0, 'lng': 0.0}

def geomPoint(lat, lon):
    return Point(lon, lat)

def addressToPoint(address, display_map, provider):
    location = geocode(address, provider=provider)
    return geomPoint(location['lat'], location['lng'])

def coordToAddress(coordinates, display_map, provider):
    location = geocode(coordinates, provider=provider)
    return location['address']

def iterator(row, column, type, provider):
    if type == 'address':
        return addressToPoint(row[column], display_map=False, provider=provider)
    elif type == 'coordinates':
        return coordToAddress(row[column], display_map=False, provider=provider)
    else:
        raise ValueError("Invalid input column type! Need to be either 'address' or 'coordinates'.")

def geolocator(dataFrame, inputType, locCol, destCol, provider='google'): #Default provider is 'google'
    data = dataFrame
    data[destCol] = data.apply(iterator, axis=1, column=locCol, type=inputType, provider=provider)
    return data


def main ():

    # Get coordinates of an address or address of a 'lat, lon' (e.g. '60.1726, 24.9510') --> only 'google' for now
    # If display_map parameter is True, it opens the geocoded location in a web browser using google maps

    # Geocode individual address and show the result on map
    result = geocode("Kokkosaarenkatu 6, Helsinki", display_map=True)

    # Geocode a coordinate pair and print out the address
    result = geocode("64.12443,25.23245", display_map=True)

    # Print out all of the information (result is a Python dictionary)
    print result

    # Print out only specific attribute from the dictionary
    print result['address']

    # Read data in
    fp = r"...\OsoitteetKarttaan.xls"
    data = pd.read_excel(fp)

    # Set prevailing zeros to fill ZIP-codes, e.g. 530 --> 00530
    data['Postinumero'] = data['Postinumero'].apply(lambda x: str(x).zfill(5))

    #Rename too long attribute names
    data.columns = [u'Omistaja', u'Lahiosoite', u'Postinum', u'Postitoim', u'KoiraNimi', u'KoiraRotu']

    #Create as good as possible address name: e.g. ExampleStreet 22, 00150 Helsinki, Finland
    data['address'] = data['Lahiosoite'] + ', ' + data['Postinum'] + ' ' + data['Postitoim']

    #Geolocate addresses
    data = geolocator(data, inputType='address', locCol='address', destCol='geometry', provider='google')  # Available providers: 'google', 'nokia', 'tomtom', 'osm', 'bing' --> same as 'nokia'

    #Create geodataframe from results
    geo = gpd.GeoDataFrame(data, geometry='geometry')

    out = r"...\GeocodedLocations.shp"
    geo.to_file(out, driver="ESRI Shapefile")

if __name__ == "__main__":
    main()
