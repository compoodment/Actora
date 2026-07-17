"""Canonical world geography data shared by shell and simulation startup."""


WORLD_GEOGRAPHY = [
    {
        "country_id": "us",
        "country_name": "United States",
        "metadata": {"region": "North America", "culture_group": "American", "primary_language": "English"},
        "cities": [
            {"city_id": "us_new_york", "city_name": "New York"},
            {"city_id": "us_los_angeles", "city_name": "Los Angeles"},
            {"city_id": "us_chicago", "city_name": "Chicago"},
            {"city_id": "us_houston", "city_name": "Houston"},
            {"city_id": "us_phoenix", "city_name": "Phoenix"},
        ],
    },
    {
        "country_id": "brazil",
        "country_name": "Brazil",
        "metadata": {"region": "South America", "culture_group": "Brazilian", "primary_language": "Portuguese"},
        "cities": [
            {"city_id": "brazil_sao_paulo", "city_name": "São Paulo"},
            {"city_id": "brazil_rio_de_janeiro", "city_name": "Rio de Janeiro"},
            {"city_id": "brazil_brasilia", "city_name": "Brasília"},
            {"city_id": "brazil_salvador", "city_name": "Salvador"},
        ],
    },
    {
        "country_id": "uk",
        "country_name": "United Kingdom",
        "metadata": {"region": "Europe", "culture_group": "British", "primary_language": "English"},
        "cities": [
            {"city_id": "uk_london", "city_name": "London"},
            {"city_id": "uk_manchester", "city_name": "Manchester"},
            {"city_id": "uk_birmingham", "city_name": "Birmingham"},
        ],
    },
    {
        "country_id": "netherlands",
        "country_name": "Netherlands",
        "metadata": {"region": "Europe", "culture_group": "Dutch", "primary_language": "Dutch"},
        "cities": [
            {"city_id": "netherlands_amsterdam", "city_name": "Amsterdam"},
            {"city_id": "netherlands_rotterdam", "city_name": "Rotterdam"},
            {"city_id": "netherlands_amersfoort", "city_name": "Amersfoort"},
            {"city_id": "netherlands_utrecht", "city_name": "Utrecht"},
            {"city_id": "netherlands_den_haag", "city_name": "Den Haag"},
        ],
    },
    {
        "country_id": "germany",
        "country_name": "Germany",
        "metadata": {"region": "Europe", "culture_group": "German", "primary_language": "German"},
        "cities": [
            {"city_id": "germany_berlin", "city_name": "Berlin"},
            {"city_id": "germany_munich", "city_name": "Munich"},
            {"city_id": "germany_hamburg", "city_name": "Hamburg"},
            {"city_id": "germany_frankfurt", "city_name": "Frankfurt"},
        ],
    },
    {
        "country_id": "kenya",
        "country_name": "Kenya",
        "metadata": {"region": "East Africa", "culture_group": "Kenyan", "primary_language": "Swahili/English"},
        "cities": [
            {"city_id": "kenya_nairobi", "city_name": "Nairobi"},
            {"city_id": "kenya_mombasa", "city_name": "Mombasa"},
            {"city_id": "kenya_kisumu", "city_name": "Kisumu"},
        ],
    },
    {
        "country_id": "colombia",
        "country_name": "Colombia",
        "metadata": {"region": "South America", "culture_group": "Colombian", "primary_language": "Spanish"},
        "cities": [
            {"city_id": "colombia_bogota", "city_name": "Bogotá"},
            {"city_id": "colombia_medellin", "city_name": "Medellín"},
            {"city_id": "colombia_cali", "city_name": "Cali"},
        ],
    },
    {
        "country_id": "japan",
        "country_name": "Japan",
        "metadata": {"region": "East Asia", "culture_group": "Japanese", "primary_language": "Japanese"},
        "cities": [
            {"city_id": "japan_tokyo", "city_name": "Tokyo"},
            {"city_id": "japan_osaka", "city_name": "Osaka"},
            {"city_id": "japan_kyoto", "city_name": "Kyoto"},
        ],
    },
    {
        "country_id": "india",
        "country_name": "India",
        "metadata": {"region": "South Asia", "culture_group": "Indian", "primary_language": "Hindi/English"},
        "cities": [
            {"city_id": "india_mumbai", "city_name": "Mumbai"},
            {"city_id": "india_delhi", "city_name": "Delhi"},
            {"city_id": "india_bangalore", "city_name": "Bangalore"},
            {"city_id": "india_kolkata", "city_name": "Kolkata"},
        ],
    },
    {
        "country_id": "indonesia",
        "country_name": "Indonesia",
        "metadata": {"region": "Southeast Asia", "culture_group": "Indonesian", "primary_language": "Indonesian"},
        "cities": [
            {"city_id": "indonesia_jakarta", "city_name": "Jakarta"},
            {"city_id": "indonesia_surabaya", "city_name": "Surabaya"},
            {"city_id": "indonesia_bandung", "city_name": "Bandung"},
        ],
    },
    {
        "country_id": "philippines",
        "country_name": "Philippines",
        "metadata": {"region": "Southeast Asia", "culture_group": "Filipino", "primary_language": "Filipino/English"},
        "cities": [
            {"city_id": "philippines_manila", "city_name": "Manila"},
            {"city_id": "philippines_cebu_city", "city_name": "Cebu City"},
            {"city_id": "philippines_davao_city", "city_name": "Davao City"},
        ],
    },
    {
        "country_id": "australia",
        "country_name": "Australia",
        "metadata": {"region": "Oceania", "culture_group": "Australian", "primary_language": "English"},
        "cities": [
            {"city_id": "australia_sydney", "city_name": "Sydney"},
            {"city_id": "australia_melbourne", "city_name": "Melbourne"},
            {"city_id": "australia_brisbane", "city_name": "Brisbane"},
        ],
    },
]
WORLD_GEOGRAPHY_BY_COUNTRY_ID = {
    country["country_id"]: country
    for country in WORLD_GEOGRAPHY
}
DEFAULT_COUNTRY_ID = WORLD_GEOGRAPHY[0]["country_id"]
DEFAULT_CITY_ID = WORLD_GEOGRAPHY[0]["cities"][0]["city_id"]
