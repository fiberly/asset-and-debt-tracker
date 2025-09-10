import re, requests

def estimate_gpu_4090():
    out = {}
    # Retail anchor via PCPartPicker product page (static MSRP reference)
    try:
        r = requests.get("https://pcpartpicker.com/product/BCGbt6/nvidia-founders-edition-geforce-rtx-4090-24-gb-video-card-900-1g136-2530-000", timeout=10)
        if r.ok and "$1599.99" in r.text:
            out["retail_anchor"] = 1599.99
    except Exception:
        pass

    # Market comps via eBay (no API token: show active listing snapshot page; parse lightly or just instruct)
    out["market_hint"] = "Check eBay active/sold listings; recent asks often ~$1.8k–$2.2k"
    return out

def estimate_bike_via_bbb():
    # You typically need brand/model/year; here we just return the URL to the guide.
    return {"bbb_url": "https://www.bicyclebluebook.com/value-guide/"}

# Generic shell to route:
def estimate_item(name: str):
    name_l = name.lower()
    if "4090" in name_l or "rtx 4090" in name_l:
        return {"kind":"gpu", **estimate_gpu_4090()}
    if any(b in name_l for b in ["trek","specialized","giant","cannondale","santa cruz","cervelo"]):
        return {"kind":"bike", **estimate_bike_via_bbb()}
    # fallback
    return {
        "kind":"generic",
        "tip":"Use eBay Browse API for sold prices, or manually check active & SOLD filters."
    }
