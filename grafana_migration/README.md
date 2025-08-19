# Grafana Dashboard Exporter Script

This script exports Grafana dashboards and their associated data from a Grafana instance.

## Prerequisites

- Python 3.x
- Running Grafana instance

## Prep Work

Before using this script, ensure you have the necessary permissions and configurations set up for your Grafana instance. You will need to create a Grafana API key with the appropriate permissions to read dashboard data.

- [Create Service Account](https://grafana.com/docs/grafana/latest/administration/service-accounts/)

Make sure you have the following 2 environment variables either set or passed as command-line arguments:

- `GRAFANA_API_URL`: The URL of your Grafana instance (e.g., `https://your-grafana.example.com`)
- `GRAFANA_API_KEY`: Your Grafana API key

You can install the required packages using pip:

```bash
pip install -r requirements.txt
```

## Usage (Python)

1. Setup a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ``` 
3. Run the script:
    ```bash
    python grafana_dashboard_exporter.py --host <grafana_api_url> --api-key <your_api_key> --dir <output_directory>
    ```
4. Deactivate the virtual environment when done:
    ```bash
    deactivate
    ```

### Options

You can specify the Grafana API URL and API key as environment variables or pass them as command-line arguments. The script will use these to connect to your Grafana instance. Or you can modify the script to set these values directly.

- '--host': The URL of your Grafana instance (e.g., `https://your-grafana.example.com`)
- '--api-key': Your Grafana API key
- '--dir': Directory to save exported dashboards (optional)

## Example

```bash
python grafana_dashboard_exporter.py --host <grafana_api_url> --api-key <your_api_key> --dir <output_directory>
```

## Output
The script will output the Grafana dashboards that were exported to JSON files in the `./grafana-dash-backup/` directory.
