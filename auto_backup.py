"""
auto_backup.py
--------------
Automatically backs up files from a source folder to a destination,
with timestamped versioning and a summary log.
Usage: python auto_backup.py --src /path/to/source --dest /path/to/backup
"""

import os
import shutil
import argparse
import hashlib
import logging
from datetime import datetime
from pathlib import Path


def setup_logging(log_dir: str):
    """Set up logging to both console and file."""
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"backup_{datetime.now().strftime('%Y%m%d')}.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return log_file


def file_hash(filepath: str) -> str:
    """Return MD5 hash of a file for change detection."""
    hasher = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (IOError, OSError):
        return ""


def get_all_files(folder: str) -> list:
    """Recursively get all file paths in a folder."""
    files = []
    for root, _, filenames in os.walk(folder):
        for fname in filenames:
            files.append(os.path.join(root, fname))
    return files


def run_backup(src: str, dest: str, incremental: bool = True) -> dict:
    """
    Copy files from src to dest.
    If incremental=True, skip files that haven't changed (same hash).
    Returns a summary dict.
    """
    if not os.path.exists(src):
        logging.error(f"Source folder not found: {src}")
        return {}

    # Create timestamped backup subfolder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dest = os.path.join(dest, f"backup_{timestamp}")
    os.makedirs(backup_dest, exist_ok=True)
    logging.info(f"Backup started  |  Source: {src}  →  Dest: {backup_dest}")

    files = get_all_files(src)
    summary = {"copied": 0, "skipped": 0, "failed": 0, "total": len(files)}

    for src_path in files:
        relative = os.path.relpath(src_path, src)
        dest_path = os.path.join(backup_dest, relative)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        # Incremental: skip unchanged files
        if incremental and os.path.exists(dest_path):
            if file_hash(src_path) == file_hash(dest_path):
                logging.debug(f"  SKIP  {relative}  (unchanged)")
                summary["skipped"] += 1
                continue

        try:
            shutil.copy2(src_path, dest_path)
            logging.info(f"  COPY  {relative}")
            summary["copied"] += 1
        except Exception as e:
            logging.error(f"  FAIL  {relative}  ({e})")
            summary["failed"] += 1

    return summary


def print_summary(summary: dict, log_file: str):
    """Print and log the backup summary."""
    logging.info("=" * 50)
    logging.info("  BACKUP SUMMARY")
    logging.info("=" * 50)
    logging.info(f"  Total files  : {summary.get('total', 0)}")
    logging.info(f"  Copied       : {summary.get('copied', 0)}")
    logging.info(f"  Skipped      : {summary.get('skipped', 0)}  (unchanged)")
    logging.info(f"  Failed       : {summary.get('failed', 0)}")
    logging.info(f"  Log saved to : {log_file}")
    logging.info("=" * 50)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated File Backup Tool")
    parser.add_argument("--src",  required=True, help="Source folder to back up")
    parser.add_argument("--dest", required=True, help="Destination backup folder")
    parser.add_argument("--full", action="store_true",
                        help="Full backup (default is incremental)")
    args = parser.parse_args()

    log_file = setup_logging(os.path.join(args.dest, "logs"))
    summary = run_backup(args.src, args.dest, incremental=not args.full)
    if summary:
        print_summary(summary, log_file)
