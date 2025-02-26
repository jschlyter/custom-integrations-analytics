"""Custom Integrations Analytics"""

import argparse
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


def read_dataset(filename: Path, url: str):
    if filename.exists():
        with open(filename) as fp:
            dataset = json.load(fp)
    else:
        dataset = httpx.get(url).json()

    return dataset


def main():
    """Main function"""

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, help="Input file", default=ANALYTICS_FILE)
    parser.add_argument("--output", type=str, help="Output file", default=REPORT_FILE)

    args = parser.parse_args()

    dataset = read_dataset(filename=Path(args.input), url=ANALYTICS_URL)
    usage = [(name, data["total"]) for name, data in dataset.items()]

    df = pd.DataFrame(
        sorted(usage, key=lambda v: v[1], reverse=True),
        columns=["Integration", "Count"],
    )

    with open(args.output, "w") as fp:
        html = df.style.pipe(make_pretty).to_html()
        fp.write(CSS + html)

    print(f"Result written to {args.output}")


if __name__ == "__main__":
    main()
