#!/usr/bin/env python3
"""
backup_to_drive.py - Download the github repo as a ZIP and upload to Google Drive.

Run:
    python backup_to_drive.py

Prerequisite: token_drive.json (created once via get_token_drive.py).
"""
import json, urllib.request, sys, datetime
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

ROOT = Path(__file__).resolve().parent
REPO_ZIP_URL = "https://codeload.github.com/NO-NAME7861/youtube-automation/zip/refs/heads/main"
FOLDER_NAME = "YouTube-Automation-Backup"
EXCLUDE_PATHS = [
    "token.json",          # API credentials - DO NOT upload
    "client_secret*.json", # OAuth client secret - DO NOT upload
    ".git/",               # version info already on GitHub
    "work/",               # intermediate render files
    "__pycache__/",
    ".env",
]

def main():
    token = ROOT / "token_drive.json"
    if not token.exists():
        sys.exit("token_drive.json missing - run get_token_drive.py first")

    creds = Credentials.from_authorized_user_file(str(token), [
        "https://www.googleapis.com/auth/drive.file",
    ])
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)

    # 1. Find or create target folder
    q = f"name='{FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    hits = drive.files().list(q=q, fields="files(id,name)").execute().get("files", [])
    if hits:
        folder_id = hits[0]["id"]
        print("using existing folder:", FOLDER_NAME, folder_id)
    else:
        folder = drive.files().create(
            body={"name": FOLDER_NAME, "mimeType": "application/vnd.google-apps.folder"},
            fields="id",
        ).execute()
        folder_id = folder["id"]
        print("created folder:", FOLDER_NAME, folder_id)

    # 2. Download latest repo ZIP (always reflects current main)
    print("downloading repo zip...")
    tmp_zip = ROOT / "repo-snapshot.zip"
    urllib.request.urlretrieve(REPO_ZIP_URL, tmp_zip)
    print(f"  size: {tmp_zip.stat().st_size / 1e6:.2f} MB")

    # 3. Name with timestamp so backups stack instead of overwriting
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    remote_name = f"youtube-automation_{stamp}.zip"
    media = MediaFileUpload(str(tmp_zip), mimetype="application/zip", resumable=True, chunksize=1024 * 1024)
    uploaded = drive.files().create(
        body={"name": remote_name, "parents": [folder_id]},
        media_body=media,
        fields="id,name,size,parents",
    ).execute()
    print("uploaded to Drive:", uploaded)

    # Cleanup local staging file
    tmp_zip.unlink()

    print("\nDONE. Open Google Drive -> folder 'YouTube-Automation-Backup' to verify.")
    print("Each run creates a timestamped snapshot - they stack indefinitely.")

if __name__ == "__main__":
    main()
