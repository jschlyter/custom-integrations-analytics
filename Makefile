all:
	poetry run python custom_integrations_analytics.py

clean:
	rm -f *.json *.html
