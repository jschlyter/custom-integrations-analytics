all:
	poetry run python custom_integrations_analytics.py

fetch: custom_integrations.json hacs_data.json

custom_integrations.json:
	curl -o $@ https://analytics.home-assistant.io/custom_integrations.json

hacs_data.json:
	curl -o $@ https://data-v2.hacs.xyz/integration/data.json

clean:
	rm -f *.json *.html
