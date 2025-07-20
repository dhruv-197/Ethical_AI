import os
import io
import zipfile
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
BASE_DIR = os.path.dirname(__file__)
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'client_secret_1088208770059-75og3oqedmpnb3f52reg2e4kol7o2kac.apps.googleusercontent.com.json')

def download_models():
    FOLDER_ID = '1GXWq6Qqpq4jQC8myAK2zQx7l7XxvROu4'
    OUTPUT_DIR = BASE_DIR
    TOKEN_FILE = os.path.join(BASE_DIR,'token.json')
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    creds = None
    
    # Check if token file exists and is valid
    if os.path.exists(TOKEN_FILE):
        try:
            # Check if file is empty or corrupted
            with open(TOKEN_FILE, 'r') as token_file:
                content = token_file.read().strip()
                if not content:
                    print("Token file is empty, will recreate authentication")
                    os.remove(TOKEN_FILE)
                else:
                    # Try to parse as JSON
                    json.loads(content)
                    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except (json.JSONDecodeError, ValueError, FileNotFoundError) as e:
            print(f"Token file is corrupted or invalid: {e}")
            # Remove corrupted token file
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)
    
    # If no valid credentials, create new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Failed to refresh token: {e}")
                # Remove corrupted token file and create new authentication
                if os.path.exists(TOKEN_FILE):
                    os.remove(TOKEN_FILE)
                creds = None
        
        if not creds:
            try:
                if os.path.exists(CREDENTIALS_FILE):
                    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                    creds = flow.run_local_server(port=0)
                    with open(TOKEN_FILE, 'w') as token:
                        token.write(creds.to_json())
                else:
                    print(f"Credentials file not found: {CREDENTIALS_FILE}")
                    print("Skipping model download - authentication not available")
                    return
            except Exception as e:
                print(f"Failed to create authentication flow: {e}")
                print("Skipping model download - authentication failed")
                return

    try:
        service = build('drive', 'v3', credentials=creds)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        query = f"'{FOLDER_ID}' in parents and trashed = false"
        results = service.files().list(q=query, pageSize=1000, fields="files(id, name, mimeType)").execute()
        files = results.get('files', [])

        if not files:
            print("No files found in the folder.")
        else:
            print(f"Found {len(files)} files in the folder.")

        for file in files:
            file_id = file['id']
            file_name = file['name']
            mime_type = file['mimeType']
            output_path = os.path.join(OUTPUT_DIR, file_name)

            # Skip unsupported extensions
            if not (file_name.endswith('.zip') or file_name.endswith('.keras')):
                print(f"  Skipped (unsupported extension): {file_name}")
                continue

            # Skip if .keras file already exists
            if file_name.endswith('.keras') and os.path.exists(output_path):
                print(f"  Skipped (already exists): {file_name}")
                continue

            # Skip if .zip is already extracted
            if file_name.endswith('.zip'):
                extracted_folder = os.path.join(OUTPUT_DIR, file_name.replace('.zip', ''))
                if os.path.exists(extracted_folder):
                    print(f"  Skipped (already extracted): {file_name}")
                    continue

            print(f"Downloading: {file_name}")

            # Skip Google Docs formats
            if mime_type.startswith('application/vnd.google-apps'):
                print(f"  Skipped (Google Docs file): {file_name}")
                continue

            request = service.files().get_media(fileId=file_id)
            fh = io.FileIO(output_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    print(f"  {int(status.progress() * 100)}% downloaded")

            print(f"  Saved to: {output_path}")

            # === If ZIP: extract and delete ===
            if file_name.endswith('.zip'):
                try:
                    with zipfile.ZipFile(output_path, 'r') as zip_ref:
                        zip_ref.extractall(extracted_folder)
                    print(f"  Extracted to: {extracted_folder}")
                    os.remove(output_path)
                    print(f"  Deleted zip: {file_name}")
                except zipfile.BadZipFile:
                    print(f"  Error: {file_name} is not a valid zip file.")
    
    except Exception as e:
        print(f"Error during model download: {e}")
        print("Continuing without downloaded models...")

# Run the function

