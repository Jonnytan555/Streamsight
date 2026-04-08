AGS_MARKET = "wheat price OR corn price OR soybean price OR grain supply OR crop harvest OR agricultural commodity"

COMMODITY_TREE = {
    "Agriculture": {
        "Grains": {
            "Wheat":     ["CBOT Wheat", "Kansas Wheat", "Milling Wheat", "Feed Wheat"],
            "Corn":      ["CBOT Corn", "Feed Corn", "Yellow Corn"],
            "Soybeans":  ["CBOT Soybeans", "Soybean Oil", "Soybean Meal"],
            "Rice":      ["Rough Rice", "Milled Rice"],
        },
        "Soft Commodities": {
            "Sugar":     ["Sugar No.11", "White Sugar", "Raw Sugar"],
            "Coffee":    ["Arabica", "Robusta"],
            "Cocoa":     ["ICE Cocoa", "LIFFE Cocoa"],
            "Cotton":    ["ICE Cotton", "Cotton No.2"],
        },
        "Oilseeds": {
            "Palm Oil":  ["CPO", "RBDPO", "Palm Olein"],
            "Canola":    ["ICE Canola", "Rapeseed"],
            "Sunflower": ["Sunflower Oil", "Sunflower Seed"],
        },
    },
}
