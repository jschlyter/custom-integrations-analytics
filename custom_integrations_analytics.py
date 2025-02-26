"""Custom Integrations Analytics"""

import argparse
import json
from pathlib import Path

import httpx
import pandas as pd

ANALYTICS_URL = "https://analytics.home-assistant.io/custom_integrations.json"
ANALYTICS_FILE = Path("custom_integrations.json")

REPORT_FILE = Path("custom_integrations.html")

TITLE = "Home Assistant Custom Integrations"

PROLOGUE = f"""
<head>
<title>{TITLE}</title>
<style type="text/css">
    thead {{ background-color: grey; }}
    tbody tr:nth-child(even) {{ background-color: lightgrey; }}
</style>
</head>
<body>
<h1>{TITLE}</h1>
"""

EPILOGUE = """
</body>
"""


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
        table_html = df.style.to_html()
        fp.write(PROLOGUE + table_html + EPILOGUE)

    print(f"Result written to {args.output}")


if __name__ == "__main__":
    main()
