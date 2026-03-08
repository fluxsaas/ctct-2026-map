# fetch_roads.py
import requests, json, time

OSRM = "https://router.project-osrm.org/route/v1/driving/"

def decode_polyline(enc):
    """Decode Google-encoded polyline (precision 5) -> [[lat, lon], ...]"""
    points, i, lat, lng = [], 0, 0, 0
    while i < len(enc):
        b, shift, res = 0, 0, 0
        while True:
            b = ord(enc[i]) - 63; i += 1
            res |= (b & 0x1f) << shift; shift += 5
            if b < 0x20: break
        lat += ~(res >> 1) if res & 1 else res >> 1
        b, shift, res = 0, 0, 0
        while True:
            b = ord(enc[i]) - 63; i += 1
            res |= (b & 0x1f) << shift; shift += 5
            if b < 0x20: break
        lng += ~(res >> 1) if res & 1 else res >> 1
        points.append([round(lat / 1e5, 6), round(lng / 1e5, 6)])
    return points

from road_segments import ROADS

results = {}
for road in ROADS:
    wp = road["wp"]
    # OSRM expects lon,lat in URL
    coords = ";".join(f"{p[1]},{p[0]}" for p in wp)
    url = OSRM + coords + "?overview=full&geometries=polyline"
    try:
        r = requests.get(url, timeout=15)
        d = r.json()
        if d.get("code") == "Ok":
            pts = decode_polyline(d["routes"][0]["geometry"])
            results[road["id"]] = pts
            print(f"  {road['id']}: {len(pts)} points")
        else:
            print(f"  {road['id']}: OSRM error - {d.get('code')} {d.get('message','')}")
    except Exception as e:
        print(f"  {road['id']}: {e}")
    time.sleep(1.2)  # respect OSRM ~1 req/s rate limit

with open("road_coords.json", "w") as f:
    json.dump(results, f)
print(f"\nSaved {len(results)} roads to road_coords.json")
