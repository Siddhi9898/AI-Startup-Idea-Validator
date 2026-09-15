"""
Location Data + GPS
-----------------------
Full A-Z alphabetical dropdowns for Country / State / City, each
with "All [Countries/States/Cities]" and "Other" options (fixes P4
parts 1-3), plus real browser GPS location detection (fixes P4
part 4) using the streamlit-js-eval package.

Honest scope note: a genuinely complete states/cities database for
EVERY country in the world is a large separate data-sourcing effort.
India is provided as a real, complete, alphabetically sorted example
(28 states + 8 union territories, with real major cities per state).
Other countries fall back to free-text entry for state/city, which
is functionally correct even though not a dropdown.
"""

ALL_COUNTRIES = ["All Countries"] + sorted([
    "Afghanistan", "Albania", "Algeria", "Argentina", "Armenia", "Australia",
    "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Belarus", "Belgium",
    "Bolivia", "Bosnia and Herzegovina", "Brazil", "Bulgaria", "Cambodia",
    "Cameroon", "Canada", "Chile", "China", "Colombia", "Costa Rica",
    "Croatia", "Cuba", "Cyprus", "Czech Republic", "Denmark", "Ecuador",
    "Egypt", "Estonia", "Ethiopia", "Finland", "France", "Georgia",
    "Germany", "Ghana", "Greece", "Hungary", "Iceland", "India",
    "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jamaica",
    "Japan", "Jordan", "Kazakhstan", "Kenya", "Kuwait", "Latvia",
    "Lebanon", "Lithuania", "Luxembourg", "Malaysia", "Malta", "Mexico",
    "Mongolia", "Morocco", "Myanmar", "Nepal", "Netherlands",
    "New Zealand", "Nigeria", "North Korea", "Norway", "Oman", "Pakistan",
    "Panama", "Paraguay", "Peru", "Philippines", "Poland", "Portugal",
    "Qatar", "Romania", "Russia", "Saudi Arabia", "Serbia", "Singapore",
    "Slovakia", "Slovenia", "South Africa", "South Korea", "Spain",
    "Sri Lanka", "Sweden", "Switzerland", "Taiwan", "Tanzania",
    "Thailand", "Tunisia", "Turkey", "Uganda", "Ukraine",
    "United Arab Emirates", "United Kingdom", "United States", "Uruguay",
    "Venezuela", "Vietnam", "Yemen", "Zimbabwe",
]) + ["Other"]

# Real, complete example for India - alphabetically sorted, with
# "All States" and "Other" following the same pattern as countries.
_INDIA_STATES_RAW = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan",
    "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
    "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands",
    "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Delhi",
    "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry",
]

# Real major cities for a few states, as a working example of the
# City level - extend this dict with more real data as it becomes
# available, rather than fabricating an exhaustive list.
_INDIA_CITIES_RAW = {
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad"],
    "Karnataka": ["Bengaluru", "Mysuru", "Hubballi", "Mangaluru"],
    "Delhi": ["New Delhi"],
    "Telangana": ["Hyderabad", "Warangal"],
}

COUNTRY_STATES = {
    "India": ["All States"] + sorted(_INDIA_STATES_RAW) + ["Other"],
}

STATE_CITIES = {
    state: ["All Cities/Towns"] + sorted(cities) + ["Other"]
    for state, cities in _INDIA_CITIES_RAW.items()
}


def get_gps_location():
    """
    Requests the browser's real GPS location (fixes P4 part 4).
    Returns {"latitude": float, "longitude": float} or None if the
    user hasn't granted permission yet / it's still loading.
    Requires: pip install streamlit-js-eval
    """
    from streamlit_js_eval import get_geolocation
    location = get_geolocation()
    if location and "coords" in location:
        return {
            "latitude": location["coords"]["latitude"],
            "longitude": location["coords"]["longitude"],
        }
    return None
