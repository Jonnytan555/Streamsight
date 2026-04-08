OIL_MARKET = "Brent crude oil price OR WTI oil price OR OPEC production OR oil supply disruption OR crude oil inventory"

COMMODITY_TREE = {
    "Energy": {
        "Oil": {
            "Crude Oil": [
                "Brent", "WTI", "Dubai", "OPEC Basket", "Urals", "Bonny Light",
            ],
            "Refined Products": [
                "Gasoline", "Diesel", "Jet Fuel", "Heating Oil", "Fuel Oil", "Naphtha",
            ],
            "NGLs": [
                "Propane", "Butane", "Ethane", "LPG",
            ],
        },
    },
}
