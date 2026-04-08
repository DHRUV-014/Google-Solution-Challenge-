"""In-memory cancer screening centres database with 20 real Indian centres."""
import math
import uuid
from typing import Optional

# ── Pre-seeded centres ─────────────────────────────────────────────────────────

_centres: list[dict] = [
    {
        "id": "c001",
        "name": "Tata Memorial Hospital",
        "address": "Dr E Borges Road, Parel",
        "city": "Mumbai",
        "state": "Maharashtra",
        "lat": 19.0046,
        "lng": 72.8413,
        "phone": "+91-22-24177000",
        "type": "Cancer Centre",
    },
    {
        "id": "c002",
        "name": "AIIMS Delhi — Cancer Centre",
        "address": "Ansari Nagar East",
        "city": "New Delhi",
        "state": "Delhi",
        "lat": 28.5672,
        "lng": 77.2100,
        "phone": "+91-11-26588500",
        "type": "Government Hospital",
    },
    {
        "id": "c003",
        "name": "Kidwai Memorial Institute of Oncology",
        "address": "M H Marigowda Road, Hombegowda Nagar",
        "city": "Bengaluru",
        "state": "Karnataka",
        "lat": 12.9354,
        "lng": 77.5950,
        "phone": "+91-80-26094000",
        "type": "Cancer Centre",
    },
    {
        "id": "c004",
        "name": "Cancer Institute (WIA)",
        "address": "38 Sardar Patel Road, Adyar",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "lat": 13.0067,
        "lng": 80.2537,
        "phone": "+91-44-22350241",
        "type": "Cancer Centre",
    },
    {
        "id": "c005",
        "name": "MNJ Institute of Oncology",
        "address": "Red Hills, Lakdikapul",
        "city": "Hyderabad",
        "state": "Telangana",
        "lat": 17.3921,
        "lng": 78.4560,
        "phone": "+91-40-23305400",
        "type": "Government Hospital",
    },
    {
        "id": "c006",
        "name": "Chittaranjan National Cancer Institute",
        "address": "37 S P Mukherjee Road",
        "city": "Kolkata",
        "state": "West Bengal",
        "lat": 22.5354,
        "lng": 88.3476,
        "phone": "+91-33-24765101",
        "type": "Cancer Centre",
    },
    {
        "id": "c007",
        "name": "Deenanath Mangeshkar Hospital — Oncology",
        "address": "Erandwane, Near Mhatre Bridge",
        "city": "Pune",
        "state": "Maharashtra",
        "lat": 18.5108,
        "lng": 73.8367,
        "phone": "+91-20-49150300",
        "type": "Private Hospital",
    },
    {
        "id": "c008",
        "name": "Gujarat Cancer & Research Institute",
        "address": "Civil Hospital Campus, Asarwa",
        "city": "Ahmedabad",
        "state": "Gujarat",
        "lat": 23.0469,
        "lng": 72.5982,
        "phone": "+91-79-22680020",
        "type": "Cancer Centre",
    },
    {
        "id": "c009",
        "name": "Bhagwan Mahaveer Cancer Hospital",
        "address": "Jawahar Lal Nehru Marg",
        "city": "Jaipur",
        "state": "Rajasthan",
        "lat": 26.9124,
        "lng": 75.8235,
        "phone": "+91-141-2700107",
        "type": "Cancer Centre",
    },
    {
        "id": "c010",
        "name": "King George's Medical University — Oncology",
        "address": "Shah Mina Road, Chowk",
        "city": "Lucknow",
        "state": "Uttar Pradesh",
        "lat": 26.8690,
        "lng": 80.9418,
        "phone": "+91-522-2257450",
        "type": "Government Hospital",
    },
    {
        "id": "c011",
        "name": "Regional Cancer Centre Thiruvananthapuram",
        "address": "Medical College PO",
        "city": "Thiruvananthapuram",
        "state": "Kerala",
        "lat": 8.5116,
        "lng": 76.9900,
        "phone": "+91-471-2442541",
        "type": "Cancer Centre",
    },
    {
        "id": "c012",
        "name": "Acharya Tulsi Regional Cancer Treatment Centre",
        "address": "S P Medical College, Bikaner",
        "city": "Bikaner",
        "state": "Rajasthan",
        "lat": 28.0229,
        "lng": 73.3119,
        "phone": "+91-151-2523155",
        "type": "Government Hospital",
    },
    {
        "id": "c013",
        "name": "B B Cancer Institute",
        "address": "A K Azad Road, Uzanbazar",
        "city": "Guwahati",
        "state": "Assam",
        "lat": 26.1890,
        "lng": 91.7458,
        "phone": "+91-361-2529457",
        "type": "Cancer Centre",
    },
    {
        "id": "c014",
        "name": "PGIMER Advanced Cancer Centre",
        "address": "Sector 12",
        "city": "Chandigarh",
        "state": "Punjab",
        "lat": 30.7660,
        "lng": 76.7784,
        "phone": "+91-172-2747585",
        "type": "Government Hospital",
    },
    {
        "id": "c015",
        "name": "Jawaharlal Nehru Cancer Hospital",
        "address": "Idgah Hills",
        "city": "Bhopal",
        "state": "Madhya Pradesh",
        "lat": 23.2441,
        "lng": 77.3971,
        "phone": "+91-755-2573444",
        "type": "Cancer Centre",
    },
    {
        "id": "c016",
        "name": "Basavatarakam Indo American Cancer Hospital",
        "address": "Banjara Hills Road No 14",
        "city": "Hyderabad",
        "state": "Telangana",
        "lat": 17.4239,
        "lng": 78.4481,
        "phone": "+91-40-23551235",
        "type": "Private Hospital",
    },
    {
        "id": "c017",
        "name": "HCG Cancer Centre",
        "address": "HCG Towers, P Kalinga Rao Road",
        "city": "Bengaluru",
        "state": "Karnataka",
        "lat": 12.9980,
        "lng": 77.5836,
        "phone": "+91-80-40206000",
        "type": "Private Hospital",
    },
    {
        "id": "c018",
        "name": "Mahavir Cancer Sansthan",
        "address": "Phulwarisharif",
        "city": "Patna",
        "state": "Bihar",
        "lat": 25.5636,
        "lng": 85.0883,
        "phone": "+91-612-2280590",
        "type": "Cancer Centre",
    },
    {
        "id": "c019",
        "name": "Rajiv Gandhi Cancer Institute",
        "address": "Sector 5, Rohini",
        "city": "New Delhi",
        "state": "Delhi",
        "lat": 28.7200,
        "lng": 77.0978,
        "phone": "+91-11-47022222",
        "type": "Private Hospital",
    },
    {
        "id": "c020",
        "name": "Apollo Cancer Centre",
        "address": "21 Greams Lane, Off Greams Road",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "lat": 13.0630,
        "lng": 80.2450,
        "phone": "+91-44-28293333",
        "type": "Private Hospital",
    },
]


# ── Haversine distance ─────────────────────────────────────────────────────────

def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlng / 2) ** 2
    )
    return round(2 * math.asin(math.sqrt(a)) * 6371, 1)


# ── Public API ─────────────────────────────────────────────────────────────────

def get_nearby_centres(
    lat: float,
    lng: float,
    radius_km: float = 50.0,
    limit: int = 5,
) -> list[dict]:
    """Return centres within radius_km sorted by distance, up to limit."""
    results = []
    for c in _centres:
        dist = _haversine_km(lat, lng, c["lat"], c["lng"])
        if dist <= radius_km:
            entry = dict(c)
            entry["distance_km"] = dist
            results.append(entry)
    results.sort(key=lambda x: x["distance_km"])
    return results[:limit]


def get_all_centres() -> list[dict]:
    """Return all centres."""
    return list(_centres)


def add_centre(data: dict) -> str:
    """Add a new centre and return its ID."""
    centre_id = f"c{str(uuid.uuid4())[:8]}"
    centre = dict(data)
    centre["id"] = centre_id
    _centres.append(centre)
    return centre_id
