# build_map.py
import json
from road_segments import ROADS

with open("road_coords.json") as f:
    coords = json.load(f)

# Build combined JSON data (roads + markers)
roads_data = []
for road in ROADS:
    rid = road["id"]
    if rid not in coords:
        print(f"  Skipping {rid} - not in road_coords.json")
        continue
    roads_data.append({
        "id": rid,
        "label": road["label"],
        "color": road["color"],
        "weight": road["weight"],
        "dash": road["dash"],
        "title": road["title"],
        "area": road["area"],
        "closed": road["closed"],
        "opens": road["opens"],
        "coords": coords[rid],
    })

markers_data = [
    {"pos": [-33.9264, 18.4242], "emoji": "\U0001f3c1", "title": "Start - Grand Parade, Cape Town CBD", "sub": "First wave: 06h16 | ~30,000 riders"},
    {"pos": [-33.8958, 18.4278], "emoji": "\U0001f3c6", "title": "Finish - Helen Suzman Boulevard, Green Point", "sub": "Closed Saturday 14h00 to Sunday 21h00"},
    {"pos": [-34.0680, 18.3530], "emoji": "\u26a0\ufe0f", "title": "Chapman's Peak Drive", "sub": "Closed Saturday 18h00 to Sunday 18h00"},
    {"pos": [-34.350, 18.484], "emoji": "\U0001f4cd", "title": "Cape Point - turnaround", "sub": "Closed 06h00 to 14h00"},
    {"pos": [-34.0450, 18.3910], "emoji": "\U0001f7e2", "title": "Ou Kaapse Weg (M64)", "sub": "OPEN all day - best bypass"},
    {"pos": [-34.1290, 18.4460], "emoji": "\U0001f4cd", "title": "Fish Hoek", "sub": "M4 closed 05h45 to 12h50"},
    {"pos": [-34.0600, 18.4720], "emoji": "\U0001f4cd", "title": "Muizenberg", "sub": "M3 + M4 junction - closed from 06h00"},
    {"pos": [-33.9650, 18.3758], "emoji": "\U0001f4cd", "title": "Camps Bay", "sub": "Victoria Rd from 04h00 - reopens ~17h30"},
    {"pos": [-33.9795, 18.4588], "emoji": "\U0001f3e0", "title": "Home — Bishopscourt", "sub": "Depart 12:15 · Cape Point by 14:00 · Home ~16:50"},
]

cutoffs_data = [
    {"pos": [-34.04538, 18.46978], "num": 1, "name": "M3/Steenberg", "time": "10h15"},
    {"pos": [-34.15597, 18.43553], "num": 2, "name": "Glencairn Express Way", "time": "11h15"},
    {"pos": [-34.205371, 18.405661], "num": 3, "name": "Perdekloof", "time": "13h00"},
    {"pos": [-34.11995, 18.39069], "num": 4, "name": "Noordhoek", "time": "14h00"},
    {"pos": [-34.04000, 18.34680], "num": 5, "name": "Hout Bay Main Road", "time": "15h00"},
    {"pos": [-33.95503, 18.37779], "num": 6, "name": "Bakoven", "time": "16h00"},
    {"pos": [-33.90015, 18.42626], "num": 7, "name": "Finish", "time": "17h00"},
]

data = {"roads": roads_data, "markers": markers_data, "cutoffs": cutoffs_data}

with open("roads_data.json", "w") as f:
    json.dump(data, f)
print(f"roads_data.json written ({len(roads_data)} roads, {len(markers_data)} markers)")

# Build HTML that loads JSON externally
html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0"/>
<title>CTCT 2026 Road Closures</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; }
#map { width:100vw; height:100vh; }
#legend {
  position:absolute; top:10px; right:10px; z-index:1000;
  background:rgba(255,255,255,0.97); border:1px solid #ddd;
  border-radius:12px; padding:0; min-width:242px;
  box-shadow:0 2px 14px rgba(0,0,0,0.15);
  max-height:90vh; overflow-y:auto;
}
#legend .legend-header {
  padding:12px 15px 0; cursor:pointer; display:flex;
  align-items:center; justify-content:space-between; user-select:none;
}
#legend .legend-header h3 { font-size:13px; font-weight:700; margin-bottom:2px; }
#legend .sub { font-size:10px; color:#888; padding:0 15px; margin-bottom:0; }
#legend .legend-body { padding:9px 15px 12px; }
#legend.collapsed .legend-body { display:none; }
#legend.collapsed .sub { padding-bottom:12px; }
#legend .legend-header .arrow { font-size:10px; color:#999; transition:transform 0.2s; }
#legend.collapsed .legend-header .arrow { transform:rotate(-90deg); }
.li { display:flex; align-items:center; gap:8px; margin-bottom:5px; font-size:11px; }
.lb { width:24px; height:5px; border-radius:3px; flex-shrink:0; }
.ld { width:24px; flex-shrink:0; border-top:4px dashed; }
hr { border:none; border-top:1px solid #eee; margin:7px 0; }
.note { font-size:10px; color:#999; line-height:1.4; }
#itinerary {
  position:absolute; bottom:10px; left:10px; z-index:1000;
  background:rgba(255,255,255,0.97); border:1px solid #ddd;
  border-radius:12px; padding:0; min-width:260px; max-width:300px;
  box-shadow:0 2px 14px rgba(0,0,0,0.15);
  font-size:11px;
}
#itinerary .itin-header {
  padding:10px 14px 8px; cursor:pointer; display:flex;
  align-items:center; justify-content:space-between;
  user-select:none;
}
#itinerary .itin-header h3 { font-size:13px; font-weight:700; margin:0; color:#1a73e8; }
#itinerary .itin-header .arrow { font-size:10px; color:#999; transition:transform 0.2s; }
#itinerary.collapsed .arrow { transform:rotate(-90deg); }
#itinerary.collapsed .itin-body { display:none; }
#itinerary .itin-body { padding:0 14px 10px; }
.itin-row { display:flex; gap:8px; padding:3px 0; border-bottom:1px solid #f0f0f0; }
.itin-row:last-child { border-bottom:none; }
.itin-time { font-weight:600; color:#1a73e8; min-width:38px; }
.itin-loc { flex:1; }
.itin-note { color:#999; font-size:10px; }
.itin-stop { background:#f0f7ff; border-radius:6px; margin:3px -4px; padding:3px 4px; }
.cutoff-icon { background:#c0392b;color:#fff;border-radius:50%;width:22px;height:22px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;box-shadow:0 1px 4px rgba(0,0,0,0.3);border:2px solid #fff; }
.leaflet-popup-content-wrapper { border-radius:10px; }
.pt { font-weight:700; font-size:13px; margin-bottom:4px; }
.pa { font-size:11px; color:#888; margin-bottom:5px; }
.pr { display:flex; justify-content:space-between; gap:12px; margin:3px 0; font-size:12px; color:#555; }
.cl { font-weight:600; color:#c0392b; }
.op { font-weight:600; color:#27ae60; }
</style>
</head>
<body>
<div id="map"></div>
<div id="legend">
  <div class="legend-header" onclick="document.getElementById('legend').classList.toggle('collapsed')">
    <h3>Cape Town Cycle Tour 2026</h3>
    <span class="arrow">&#9660;</span>
  </div>
  <div class="sub">Sun 8 March | Road geometry from OSRM</div>
  <div class="legend-body">
  <div class="li"><div class="lb" style="background:#e74c3c"></div>M3 / N2 outbound</div>
  <div class="li"><div class="ld" style="border-color:#c0392b;opacity:.6"></div>M3 inbound - 42km</div>
  <div class="li"><div class="lb" style="background:#e67e22"></div>M4 - False Bay coast</div>
  <div class="li"><div class="lb" style="background:#8e44ad"></div>M65 - Deep South</div>
  <div class="li"><div class="lb" style="background:#e8a000"></div>Chapman's Peak / Noordhoek M6</div>
  <div class="li"><div class="lb" style="background:#d35400"></div>M6 - Atlantic Seaboard</div>
  <div class="li"><div class="lb" style="background:#c0392b"></div>Helen Suzman - FINISH</div>
  <div class="li"><div class="lb" style="background:#2980b9"></div>CBD streets</div>
  <div class="li"><div class="ld" style="border-color:#27ae60"></div>Ou Kaapse Weg M64 (OPEN)</div>
  <div class="li" style="font-weight:600;margin-top:4px;">Cut-offs</div>
  <div class="li co" data-n="1" style="cursor:pointer;"><div class="cutoff-icon" style="width:18px;height:18px;font-size:9px;flex-shrink:0;">1</div>M3/Steenberg <span style="color:#c0392b;margin-left:auto;">10h15</span></div>
  <div class="li co" data-n="2" style="cursor:pointer;"><div class="cutoff-icon" style="width:18px;height:18px;font-size:9px;flex-shrink:0;">2</div>Glencairn <span style="color:#c0392b;margin-left:auto;">11h15</span></div>
  <div class="li co" data-n="3" style="cursor:pointer;"><div class="cutoff-icon" style="width:18px;height:18px;font-size:9px;flex-shrink:0;">3</div>Perdekloof <span style="color:#c0392b;margin-left:auto;">13h00</span></div>
  <div class="li co" data-n="4" style="cursor:pointer;"><div class="cutoff-icon" style="width:18px;height:18px;font-size:9px;flex-shrink:0;">4</div>Noordhoek <span style="color:#c0392b;margin-left:auto;">14h00</span></div>
  <div class="li co" data-n="5" style="cursor:pointer;"><div class="cutoff-icon" style="width:18px;height:18px;font-size:9px;flex-shrink:0;">5</div>Hout Bay <span style="color:#c0392b;margin-left:auto;">15h00</span></div>
  <div class="li co" data-n="6" style="cursor:pointer;"><div class="cutoff-icon" style="width:18px;height:18px;font-size:9px;flex-shrink:0;">6</div>Bakoven <span style="color:#c0392b;margin-left:auto;">16h00</span></div>
  <div class="li co" data-n="7" style="cursor:pointer;"><div class="cutoff-icon" style="width:18px;height:18px;font-size:9px;flex-shrink:0;">7</div>Finish <span style="color:#c0392b;margin-left:auto;">17h00</span></div>
  <hr/>
  <div class="li" id="toggle-myroute" style="cursor:pointer;"><div class="ld" style="border-color:#1a73e8"></div><strong>My Route</strong> (fastest, 12:15)</div>
  <hr/>
  <div class="note">Tap any road for closure times.<br>Data: official PDF, 1 Mar 2026.</div>
  </div>
</div>
<div id="itinerary">
  <div class="itin-header" onclick="document.getElementById('itinerary').classList.toggle('collapsed')">
    <h3>My Route</h3>
    <span class="arrow">&#9660;</span>
  </div>
  <div class="itin-body">
    <div class="itin-row"><div class="itin-time">12:15</div><div class="itin-loc">Depart Bishopscourt<div class="itin-note">Local roads: Klaasens &rarr; Brommersvlei &rarr; Constantia</div></div></div>
    <div class="itin-row"><div class="itin-time">12:30</div><div class="itin-loc">Steenberg area<div class="itin-note">M42 just reopened</div></div></div>
    <div class="itin-row"><div class="itin-time">12:45</div><div class="itin-loc">Muizenberg / St James<div class="itin-note">M4 open from 12:30</div></div></div>
    <div class="itin-row"><div class="itin-time">12:55</div><div class="itin-loc">Kalk Bay &rarr; Fish Hoek<div class="itin-note">Clairvaux reopens 12:50</div></div></div>
    <div class="itin-row"><div class="itin-time">13:15</div><div class="itin-loc">Through Simon's Town</div></div>
    <div class="itin-row"><div class="itin-time">13:50</div><div class="itin-loc">Cape Point gate<div class="itin-note">Wait ~10 min for 14:00 opening</div></div></div>
    <div class="itin-row itin-stop"><div class="itin-time">14:00</div><div class="itin-loc"><strong>Enter Cape Point</strong><div class="itin-note">Earliest possible entry</div></div></div>
    <div class="itin-row"><div class="itin-time">15:30</div><div class="itin-loc">Depart Cape Point</div></div>
    <div class="itin-row"><div class="itin-time">16:00</div><div class="itin-loc">Through Simon's Town</div></div>
    <div class="itin-row"><div class="itin-time">16:35</div><div class="itin-loc">Steenberg / Tokai<div class="itin-note">M3 inbound open (reopened 15:00)</div></div></div>
    <div class="itin-row"><div class="itin-time">16:50</div><div class="itin-loc">Home &mdash; Bishopscourt<div class="itin-note">Return via M3 &mdash; all roads open</div></div></div>
  </div>
</div>
<script>
const map = L.map('map').setView([-34.05, 18.42], 11);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  maxZoom: 19
}).addTo(map);

let myRouteLayer = null;
const cutoffMarkers = {};

function renderRoads(data) {
  data.roads.forEach(r => {
    const opts = { color: r.color, weight: r.weight, opacity: 0.88 };
    if (r.dash) opts.dashArray = r.dash;
    const line = L.polyline(r.coords, opts).addTo(map).bindPopup(
      `<div class="pt">${r.title}</div>
       <div class="pa">${r.area}</div>
       <div class="pr"><span>Closed</span><span class="cl">${r.closed}</span></div>
       <div class="pr"><span>Reopens</span><span class="op">${r.opens}</span></div>`,
      {maxWidth: 320}
    );
    if (r.id === 'my_route') myRouteLayer = line;
  });

  data.markers.forEach(m => {
    L.marker(m.pos, { icon: L.divIcon({
      iconSize:[32,32], iconAnchor:[16,16], popupAnchor:[0,-18], className:'',
      html:`<div style="background:#fff;border:2.5px solid #444;border-radius:50%;width:32px;height:32px;display:flex;align-items:center;justify-content:center;font-size:16px;box-shadow:0 2px 6px rgba(0,0,0,0.22);">${m.emoji}</div>`
    })}).addTo(map)
      .bindPopup(`<div class="pt">${m.title}</div><div style="font-size:11px;color:#666;margin-top:3px;">${m.sub}</div>`);
  });

  (data.cutoffs||[]).forEach(c => {
    const m = L.marker(c.pos, { icon: L.divIcon({
      iconSize:[22,22], iconAnchor:[11,11], popupAnchor:[0,-14], className:'',
      html:`<div class="cutoff-icon">${c.num}</div>`
    })}).addTo(map)
      .bindPopup(`<div class="pt">Cut-off ${c.num}: ${c.name}</div><div style="font-size:12px;color:#c0392b;font-weight:600;margin-top:3px;">Must pass by ${c.time}</div>`);
    cutoffMarkers[c.num] = m;
  });
}

// Load JSON data — uses browser cache on subsequent visits
fetch('roads_data.json')
  .then(r => r.json())
  .then(renderRoads)
  .catch(err => console.error('Failed to load road data:', err));

document.querySelectorAll('.co').forEach(el => {
  el.addEventListener('click', () => {
    const n = parseInt(el.dataset.n);
    const m = cutoffMarkers[n];
    if (m) { map.setView(m.getLatLng(), 14); m.openPopup(); }
  });
});

document.getElementById('toggle-myroute').addEventListener('click', () => {
  if (!myRouteLayer) return;
  const el = document.getElementById('toggle-myroute');
  if (map.hasLayer(myRouteLayer)) {
    map.removeLayer(myRouteLayer);
    el.style.opacity = '0.35';
  } else {
    map.addLayer(myRouteLayer);
    el.style.opacity = '1';
  }
});
</script>
</body>
</html>"""

with open("index.html", "w") as f:
    f.write(html)
print("index.html written - open in any browser!")
