omie
edf 
genscape/natgas/woodmack
bmrs
rte

🌍 1. Pan-European (START HERE)
🔥 ENTSO-E Transparency Platform
Best overall source (core backbone)
Covers:
Generation outages
Transmission outages
Load, generation, flows
API:
REST API (token required)
Docs:
👉 https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html
Overview:
Notes:
Most complete dataset
Slight lag / messy schema
You’ll need mapping logic (fuel types, units, etc.)
🇬🇧 2. UK
BMRS (Elexon)
Generation outages + availability
API:

👉 https://developer.bmreports.com/

Key endpoints:
B1610 (plant availability)
B1620 (unavailability)
Notes:
Very clean API
Widely used in UK desks
🇫🇷 3. France
RTE (eco2mix / transparency)
Generation + outages (especially nuclear)
API:

👉 https://data.rte-france.com/

Notes:
Requires API key
Good granularity
Often paired with EDF disclosures
EDF (nuclear outages)
Not a clean API
Access:
Scraping / CSV downloads / REMIT

👉 https://www.edf.fr/en/the-edf-group/production/nuclear-power/nuclear-availability

Notes:
Important for French nuclear
Often scraped in practice
🇩🇪 4. Germany
EEX Transparency Platform (REMIT hub)
UMMs (outage notices)
API:

👉 https://www.eex-transparency.com/en/api

Notes:
One of the most important outage sources
Covers:
Planned outages
Forced outages
Event-based (not time series → you must transform)
🇮🇹 5. Italy
Terna
Grid + generation outages
API:

👉 https://api.terna.it/

Notes:
Requires registration
Good for transmission + capacity
🇪🇸 6. Spain
Red Eléctrica (REE)
Transmission + generation
API:

👉 https://apidatos.ree.es/en

Notes:
Clean REST API
Good for outages + system data
🇳🇱 / 🇩🇪 / 🇩🇰 7. TenneT
TenneT Transparency
Interconnectors + outages
API:

👉 https://www.tennet.eu/electricity-market/transparency

Notes:
Often requires scraping
Important for cross-border flows
🇧🇪 8. Belgium
Elia
Grid + outages
API:

👉 https://opendata.elia.be/

🇳🇴 / Nordics 9. Nord Pool / TSOs
Nord Pool
Market + REMIT UMMs
API:

👉 https://data.nordpoolgroup.com/api

Statnett / Svenska kraftnät
TSO-level data (limited APIs)
⚡ 10. REMIT Platforms (VERY IMPORTANT)

These are where actual outage announcements come from:

EEX REMIT (best)

👉 https://www.eex-transparency.com/

Nord Pool REMIT

👉 https://umm.nordpoolgroup.com/

🧠 How to structure this (important for your project)
🔥 Real-world pipeline
ENTSO-E (baseline time series)
    +
REMIT (event outages)
    +
TSO APIs (granular / country-specific)
💥 Key insight (this matters a lot)

👉 There is no single “perfect API”

ENTSO-E = best structured
REMIT = most accurate (but messy)
TSOs = most granular