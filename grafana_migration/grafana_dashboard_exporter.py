import json
import os
import requests
from dotenv import load_dotenv
load_dotenv()

HOST = os.environ.get('GRAFANA_API_URL')
API_KEY = os.environ.get('GRAFANA_API_KEY')
DIR = './grafana-dash-backup/'

def create_root_directories():
    if not os.path.exists(DIR):
        os.makedirs(DIR)

def fetch_resources():
    headers = {'Authorization': f'Bearer {API_KEY}'}
    response = requests.get(f'{HOST}/api/search?query=&', headers=headers)
    if response.raise_for_status():
        return response.json()
    return response.json()

def build_folder_map(search_results):
    # Map folder UID to folder info
    folders = {item['uid']: item for item in search_results if item.get('type') == 'dash-folder'}

    # Helper to get full path of a folder UID
    def get_full_path(folder_uid):
        parts = []
        current_uid = folder_uid
        while current_uid and current_uid in folders:
            folder = folders[current_uid]
            parts.insert(0, folder['title'])
            current_uid = folder.get('parentUid') # Parent folders UID
        return os.path.join(DIR, *parts) if parts else DIR
    
    return folders, get_full_path

def create_folder_structure(folders, get_full_path):
    for uid in folders:
        folder_path = get_full_path(uid)
        os.makedirs(folder_path, exist_ok=True)


def export_dashboards(search_results, folders, get_full_path):
    headers = {'Authorization': f'Bearer {API_KEY}'}
    for dash in search_results:
        if dash.get('type') != 'dash-db':
            continue
        print(f"Saving dashboard: {dash['title']}")
        dash_respponse = requests.get(f"{HOST}/api/dashboards/uid/{dash['uid']}", headers=headers)
        dash_json = dash_respponse.json()
        if 'dashboard' not in dash_json:
            print(f"Warning: Dashboard {dash['title']} not found in response for UID {dash['uid']}. Skipping.")
            continue
        data = dash_json['dashboard']
        dash_str = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
        name = data['title'].replace(' ', '').replace('/', '').replace(':', '')

        # Use folderUID from search result to determine path
        folder_uid = dash.get('folderUid')
        folder_path = get_full_path(folder_uid)
        os.makedirs(folder_path, exist_ok=True)
        with open(os.path.join(folder_path, f"{name}.json"), 'w') as f:
            f.write(dash_str)
            f.write('\n')

def main():
    create_root_directories()
    search_results = fetch_resources()
    folders, get_full_path = build_folder_map(search_results)
    create_folder_structure(folders, get_full_path)
    export_dashboards(search_results, folders, get_full_path)

if __name__ == "__main__":
    main()
    print("Grafana dashboards backup completed successfully.")