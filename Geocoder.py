__author__ = 'tenkahen'
# -*- coding: utf-8 -*-
import geocoder
import webbrowser

def geocode(address, provider='google', display_map=False):
    if provider == 'google':
        geo = geocoder.google(address)

    if display_map == True:
        #Check if address is a coordinate pair
        if address.replace(',', '').replace('.', '').replace('-', '').isdigit():
            url = "http://maps.google.com/?q=%s" % geo.address
        else:
            url = "http://www.google.com/maps/place/%s,%s" % (geo.lat, geo.lng)
        webbrowser.open(url)

    return geo.json

def main ():

    # Get coordinates of an address or address of a 'lat, lon' (e.g. '60.1726, 24.9510') --> only 'google' for now
    # If display_map parameter is True, it opens the geocoded location in a web browser using google maps

    # Geocode individual address and show the result on map
    result = geocode("Kokkosaarenkatu 6, Helsinki", display_map=True)

    # Geocode a coordinate pair and print out the address
    result = geocode("64.12443,25.23245", display_map=False)

    # Print out all of the information (result is a Python dictionary)
    print result

    # Print out only specific attribute from the dictionary
    print result['address']

main()
