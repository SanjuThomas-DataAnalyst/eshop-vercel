import json
import csv
from statistics import mean

DATA = []

with open("telemetry.csv") as f:
    reader = csv.DictReader(f)
    for r in reader:
        DATA.append({
            "region": r["region"],
            "latency_ms": float(r["latency_ms"]),
            "uptime": float(r["uptime"])
        })

def percentile(values, p):
    values = sorted(values)
    k = (len(values) - 1) * (p / 100)
    f = int(k)
    c = min(f + 1, len(values) - 1)
    return values[f] + (values[c] - values[f]) * (k - f)

def handler(request):

    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST",
                "Access-Control-Allow-Headers": "Content-Type",
            }
        }

    if request.method != "POST":
        return {"statusCode": 405, "body": "POST only"}

    body = request.get_json()
    regions = body["regions"]
    threshold = body["threshold_ms"]

    result = {}

    for region in regions:
        rows = [r for r in DATA if r["region"] == region]
        lat = [r["latency_ms"] for r in rows]
        up = [r["uptime"] for r in rows]

        result[region] = {
            "avg_latency": mean(lat),
            "p95_latency": percentile(lat, 95),
            "avg_uptime": mean(up),
            "breaches": sum(1 for v in lat if v > threshold)
        }

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps(result)
    }
