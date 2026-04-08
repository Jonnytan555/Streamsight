def record_id(r):
    return r["id"]


def title(r):
    asset  = r.get("affectedAssetName") or r.get("balancingZoneName") or "Unknown Asset"
    etype  = r.get("eventType") or "Event"
    status = r.get("eventStatus") or ""
    prefix = "[UPDATE] " if (r.get("versionNumber") or 1) > 1 else ""
    return f"{prefix}{asset} — {etype} ({status})"


def body(r):
    lines = []
    if r.get("marketParticipantName"):
        lines.append(f"Market Participant: {r['marketParticipantName']}")
    if r.get("balancingZoneName"):
        lines.append(f"Balancing Zone: {r['balancingZoneName']}")
    if r.get("affectedAssetName"):
        lines.append(f"Affected Asset: {r['affectedAssetName']}")
    if r.get("eventType"):
        lines.append(f"Event Type: {r['eventType']}")
    if r.get("eventStatus"):
        lines.append(f"Status: {r['eventStatus']}")
    if r.get("eventStart"):
        lines.append(f"Start: {r['eventStart']}")
    if r.get("eventStop"):
        lines.append(f"End: {r['eventStop']}")
    if r.get("unavailableCapacity") is not None:
        lines.append(f"Unavailable Capacity: {r['unavailableCapacity']} {r.get('unitMeasure', '')}")
    if r.get("availableCapacity") is not None:
        lines.append(f"Available Capacity: {r['availableCapacity']} {r.get('unitMeasure', '')}")
    if r.get("technicalCapacity") is not None:
        lines.append(f"Technical Capacity: {r['technicalCapacity']} {r.get('unitMeasure', '')}")
    if r.get("unavailabilityReason"):
        lines.append(f"\nReason: {r['unavailabilityReason']}")
    if r.get("remarks"):
        lines.append(f"Remarks: {r['remarks']}")
    return "\n".join(lines)


def published_at(r):
    pub = r.get("publicationDateTime") or r.get("CreatedDate")
    if not pub:
        return None
    return str(pub)[:10]
