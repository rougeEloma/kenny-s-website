"""Writes map.svg.txt: an inline SVG of Central Africa with the four Kenny's cities."""
import sys, warnings
warnings.filterwarnings("ignore")
import geopandas as gpd
from shapely.geometry import box, Polygon, MultiPolygon

OUT = sys.argv[1]
W, H = 1000, 760
LON0, LON1, LAT0, LAT1 = 5.5, 34.5, -17.0, 5.0   # view box (degrees)
sx = W / (LON1 - LON0); sy = H / (LAT1 - LAT0)

def xy(lon, lat): return ((lon - LON0) * sx, (LAT1 - lat) * sy)

world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
clip = box(LON0 - 2, LAT0 - 2, LON1 + 2, LAT1 + 2)
HOME = {"Dem. Rep. Congo", "Congo"}

def ring(coords):
    pts = [xy(x, y) for x, y in coords]
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z"

def path_d(geom):
    polys = [geom] if isinstance(geom, Polygon) else list(geom.geoms) if isinstance(geom, MultiPolygon) else []
    return "".join(ring(p.exterior.coords) + "".join(ring(i.coords) for i in p.interiors) for p in polys)

others, home = [], []
for _, r in world.iterrows():
    g = r.geometry.intersection(clip)
    if g.is_empty: continue
    d = path_d(g)
    if not d: continue
    (home if r["name"] in HOME else others).append((r["name"], d))

CITIES = [  # name, country, lat, lon, label side
    ("Kinshasa", "DR Congo", -4.325, 15.322, "r"),
    ("Pointe-Noire", "Congo", -4.778, 11.863, "lb"),
    ("Kolwezi", "DR Congo", -10.716, 25.473, "l"),
    ("Lubumbashi", "DR Congo", -11.664, 27.479, "r"),
]

parts = [f'<svg class="amap" viewBox="0 0 {W} {H}" role="img" aria-labelledby="map-t" preserveAspectRatio="xMidYMid meet">',
         '<title id="map-t">Map of Central Africa showing Kinshasa, Lubumbashi and Kolwezi in DR Congo, and Pointe-Noire in Congo</title>',
         '<g class="m-oth">' + "".join(f'<path d="{d}"/>' for _, d in others) + "</g>",
         '<g class="m-home">' + "".join(f'<path d="{d}"/>' for _, d in home) + "</g>"]
# country labels
for name, lat, lon in [("DR CONGO", -2.2, 23.0), ("CONGO", 0.6, 14.6)]:
    x, y = xy(lon, lat)
    parts.append(f'<text class="m-cty" x="{x:.0f}" y="{y:.0f}" text-anchor="middle">{name}</text>')
for i, (name, ctry, lat, lon, side) in enumerate(CITIES):
    x, y = xy(lon, lat)
    anchor = "start" if side == "r" else "end"
    dx = 22 if side == "r" else -22
    extra = " below" if side == "lb" else ""
    parts.append(f'<g class="m-pin" style="--d:{i * 0.18:.2f}s">'
                 f'<circle class="m-pulse" cx="{x:.1f}" cy="{y:.1f}" r="9"/>'
                 f'<rect x="{x - 6:.1f}" y="{y - 6:.1f}" width="12" height="12" transform="rotate(45 {x:.1f} {y:.1f})"/>'
                 f'<text class="m-city{extra}" x="{x + dx:.1f}" y="{y + 6:.1f}" text-anchor="{anchor}">{name}</text></g>')
parts.append("</svg>")
svg = "".join(parts)
open(OUT, "w").write(svg)
print(len(svg), "bytes")
