all:
	poetry run python custom_integrations_analytics.py

fetch: custom_integrations.json

custom_integrations.json:
	curl -o $@ https://analytics.home-assistant.io/custom_integrations.json

clean:
	rm -f *.json *.html
