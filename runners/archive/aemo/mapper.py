def record_id(r):
    return f"{r['GasDate']}_{r['FacilityId']}_{r['LocationId']}_{r['VersionNum']}"


def title(r):
    prefix = "[UPDATE] " if r['VersionNum'] > 1 else ""
    return f"{prefix}{r['FacilityName']} ({r['LocationName']}) — {r['GasDate']}"


def body(r):
    prefix = "[This is a revised data submission]\n\n" if r['VersionNum'] > 1 else ""
    return (
        f"{prefix}"
        f"Facility: {r['FacilityName']} | Type: {r['FacilityType']}\n"
        f"Location: {r['LocationName']}\n"
        f"Gas Date: {r['GasDate']}\n"
        f"Demand: {r['Demand']} | Supply: {r['Supply']}\n"
        f"Transfer In: {r['TransferIn']} | Transfer Out: {r['TransferOut']}"
    )


def published_at(r):
    return r["GasDate"]
