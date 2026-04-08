GAS_MARKET = "TTF gas prices OR Henry Hub OR JKM LNG prices OR European gas storage OR LNG supply disruption"

COMMODITY_TREE = {
    "Energy": {
        "Natural Gas": {
            "European Gas":  ["TTF", "NBP", "THE", "PEG", "PSV", "CEGH"],
            "US Gas":        ["Henry Hub", "SoCal Gas", "Chicago Citygate", "Transco Zone 6"],
            "Asian LNG":     ["JKM", "Platts JKM", "DES Japan", "DES Korea"],
            "Australian Gas":["STTM Sydney", "STTM Adelaide", "STTM Brisbane", "Victorian DWGM"],
            "LNG Global":    ["LNG Spot", "LNG DES", "FOB LNG", "LNG Freight"],
        },
    },
}
