"""Custom Integrations Analytics"""

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx2
import jinja2
import pandas as pd
from pandas.io.formats.style import Styler

ANALYTICS_URL = "https://analytics.home-assistant.io/custom_integrations.json"
ANALYTICS_FILE = Path("custom_integrations.json")

TEMPLATE_FILE = Path("custom_integrations_analytics.html.j2")
REPORT_FILE = Path("custom_integrations.html")

TITLE = "Home Assistant Custom Integrations"

REPOSITORY_NAME = "jschlyter/custom-integrations-analytics"
REPOSITORY_URL = "https://github.com/jschlyter/custom-integrations-analytics"

MARKETPLACE_DATA_URL = "https://data-v2.hacs.xyz/integration/data.json"
MARKETPLACE_DATA_FILE = "marketplace_data.json"


@dataclass(frozen=True)
class MarketplaceIntegration:
    domain: str
    manifest_name: str
    full_name: str

    @property
    def href(self) -> str:
        return urljoin("https://github.com", self.full_name)


def read_dataset(filename: Path, url: str) -> dict[str, Any]:
    """Read dataset from file or URL"""

    if filename.exists():
        with open(filename) as fp:
            return json.load(fp)
    else:
        return httpx2.get(url).json()


def make_pretty(styler: Styler) -> Styler:
    styler.format(thousands=",")
    styler.set_uuid("integrations")
    styler.set_table_attributes('class="display"')
    return styler


def main() -> None:
    """Main function"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        type=str,
        help="Input URL",
        default=ANALYTICS_URL,
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Input file",
        default=ANALYTICS_FILE,
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file",
        default=REPORT_FILE,
    )
    parser.add_argument(
        "--template",
        type=Path,
        help="Template file",
        default=TEMPLATE_FILE,
    )

    args = parser.parse_args()

    dataset = read_dataset(filename=Path(args.input), url=args.url)

    # Read integration data from Home Assistant Marketplace
    integrations: dict[str, MarketplaceIntegration] = {}
    marketplace_dataset = read_dataset(filename=Path(MARKETPLACE_DATA_FILE), url=MARKETPLACE_DATA_URL)
    for data in marketplace_dataset.values():
        i = MarketplaceIntegration(
            domain=data["domain"],
            manifest_name=data["manifest_name"],
            full_name=data["full_name"],
        )
        integrations[i.domain] = i

    usage = []
    for name, data in dataset.items():
        if integration := integrations.get(name):
            description = f'<a href="{integration.href}">{integration.manifest_name}</a>'
        else:
            description = ""
        usage.append([name, description, data.get("total")])

    df = pd.DataFrame(
        sorted(usage, key=lambda v: v[2], reverse=True),
        columns=["Integration", "Description", "Count"],
    )

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("."), autoescape=jinja2.select_autoescape()
    )

    template = env.get_template(str(args.template))

    with open(args.output, "w") as fp:
        table_html = df.style.pipe(make_pretty).to_html()

        fp.write(
            template.render(
                title=TITLE,
                table=table_html,
                now=datetime.now(tz=timezone.utc),
                repository_url=REPOSITORY_URL,
                repository_name=REPOSITORY_NAME,
            )
        )

    print(f"Result written to {args.output}")


if __name__ == "__main__":
    main()
