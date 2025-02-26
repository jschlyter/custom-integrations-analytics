"""Custom Integrations Analytics"""

import json
from pathlib import Path

import httpx
import pandas as pd
from pandas.io.formats.style import Styler

ANALYTICS_URL = "https://analytics.home-assistant.io/custom_integrations.json"
ANALYTICS_FILE = Path("custom_integrations.json")

REPORT_FILE = Path("custom_integrations.html")

CSS = """
<style>
    thead { background-color: grey; }
    tbody tr:nth-child(even) { background-color: lightgrey; }
</style>
"""


def make_pretty(styler: Styler) -> Styler:
    styler.set_caption("Custom Integrations Analytics")
    return styler


def read_dataset():
    if ANALYTICS_FILE.exists():
        with open(ANALYTICS_FILE) as fp:
            dataset = json.load(fp)
    else:
        dataset = httpx.get(ANALYTICS_URL).json()
        with open(ANALYTICS_FILE, "w") as fp:
            json.dump(dataset, fp)

    return dataset


def main():
    dataset = read_dataset()
    usage = [(name, data["total"]) for name, data in dataset.items()]

    df = pd.DataFrame(
        sorted(usage, key=lambda v: v[1], reverse=True),
        columns=["Integration", "Count"],
    )

    with open(REPORT_FILE, "w") as fp:
        html = df.style.pipe(make_pretty).to_html()
        fp.write(CSS + html)

    print(f"Result written to {REPORT_FILE}")


if __name__ == "__main__":
    main()
