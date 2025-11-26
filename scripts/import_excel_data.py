"""
Excel to Database Import Script
Imports deployment data from Excel files to SQLite database.
Handles duplicates by checking jira_id + component_id combination.
"""

import pandas as pd
import sqlite3
import os
from datetime import datetime
from typing import Dict, Tuple, Optional
import re


def parse_timestamp(ts_str: str) -> Optional[datetime]:
    """Parse various timestamp formats from Excel."""
    if pd.isna(ts_str):
        return None

    ts_str = str(ts_str).strip()

    # Common formats
    formats = [
        "%d-%b-%Y %I:%M%p",      # 02-Nov-2025 12:08PM
        "%d-%b-%Y %I:%M %p",     # 02-Nov-2025 12:08 PM
        "%Y-%m-%d %H:%M:%S",     # 2025-11-02 12:08:00
        "%d/%m/%Y %H:%M",        # 02/11/2025 12:08
        "%d-%m-%Y %H:%M",        # 02-11-2025 12:08
        "%Y-%m-%dT%H:%M:%S",     # ISO format
    ]

    for fmt in formats:
        try:
            return datetime.strptime(ts_str, fmt)
        except ValueError:
            continue

    # Try pandas parsing as fallback
    try:
        return pd.to_datetime(ts_str).to_pydatetime()
    except:
        print(f"  Warning: Could not parse timestamp: {ts_str}")
        return None


def get_mappings(cursor) -> Tuple[Dict, Dict, Dict]:
    """Get project and component ID mappings from database."""
    # Project name to id
    cursor.execute("SELECT id, name FROM projects")
    proj_name_to_id = {}
    for row in cursor.fetchall():
        proj_name_to_id[row[1].upper()] = row[0]
        proj_name_to_id[row[1]] = row[0]
        # Handle variations
        clean_name = re.sub(r'[_\-\s]', '', row[1].upper())
        proj_name_to_id[clean_name] = row[0]

    # Component name to id
    cursor.execute("SELECT id, name, project_id FROM components")
    comp_name_to_id = {}
    comp_to_project = {}
    for row in cursor.fetchall():
        comp_name_to_id[row[1].upper()] = row[0]
        comp_name_to_id[row[1]] = row[0]
        comp_to_project[row[0]] = row[2]
        # Handle variations
        clean_name = re.sub(r'[_\-\s]', '', row[1].upper())
        comp_name_to_id[clean_name] = row[0]

    return proj_name_to_id, comp_name_to_id, comp_to_project


def get_existing_records(cursor) -> set:
    """Get existing deployment records as set of (jira_id, component_id, timestamp_date)."""
    cursor.execute("""
        SELECT jira_id, component_id, date(timestamp)
        FROM deployments
    """)
    records = set()
    for row in cursor.fetchall():
        jira_id = row[0] if row[0] else ''
        records.add((jira_id, row[1], row[2]))
    return records


def import_excel_files(reports_path: str, db_path: str, dry_run: bool = False):
    """Import all Excel files from reports folder to database."""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    proj_map, comp_map, comp_to_proj = get_mappings(cursor)
    existing = get_existing_records(cursor)

    print(f"Found {len(existing)} existing deployments in database")

    imported = 0
    skipped = 0
    errors = []

    # Process each month folder
    for month_folder in sorted(os.listdir(reports_path)):
        month_path = os.path.join(reports_path, month_folder)
        if not os.path.isdir(month_path) or month_folder.startswith('.'):
            continue

        print(f"\nProcessing {month_folder}...")

        for excel_file in sorted(os.listdir(month_path)):
            if not excel_file.endswith('.xlsx'):
                continue

            file_path = os.path.join(month_path, excel_file)
            print(f"  Reading {excel_file}...")

            try:
                df = pd.read_excel(file_path)
            except Exception as e:
                errors.append(f"Error reading {excel_file}: {e}")
                continue

            for idx, row in df.iterrows():
                try:
                    # Extract data
                    jira_id = str(row.get('JIRA PATCH ID', '')).strip()
                    if jira_id.lower() == 'nan':
                        jira_id = ''

                    comp_name = str(row.get('Component Name', '')).strip()
                    proj_name = str(row.get('Project Name', '')).strip()

                    # Get component ID
                    comp_id = comp_map.get(comp_name.upper()) or comp_map.get(comp_name)
                    if not comp_id:
                        clean_comp = re.sub(r'[_\-\s]', '', comp_name.upper())
                        comp_id = comp_map.get(clean_comp)

                    if not comp_id:
                        errors.append(f"Component not found: '{comp_name}' in {excel_file}")
                        continue

                    # Get project ID from component
                    proj_id = comp_to_proj.get(comp_id)

                    # Parse timestamp
                    timestamp = parse_timestamp(row.get('Timestamp'))
                    if not timestamp:
                        timestamp = datetime.now()

                    # Check for duplicate
                    ts_date = timestamp.strftime('%Y-%m-%d')
                    record_key = (jira_id, comp_id, ts_date)

                    if record_key in existing:
                        skipped += 1
                        continue

                    # Prepare deployment data
                    deployment = {
                        'jira_id': jira_id if jira_id else None,
                        'project_id': proj_id,
                        'component_id': comp_id,
                        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'environment': str(row.get('Environment', '')).strip() or None,
                        'vcs_url': str(row.get('SVN/GIT URL', '')).strip() or None,
                        'developer_name': str(row.get('Developer Name', '')).strip() or None,
                        'build_server': str(row.get('Build Server', '')).strip() or None,
                        'deploy_server': str(row.get('Deploy Server', '')).strip() or None,
                        'database_name': str(row.get('Database Name', '')).strip() or None,
                        'db_backup_location': str(row.get('DB Backup Location', '')).strip() or None,
                        'database_script': str(row.get('Database Script', '')).strip() or None,
                        'previous_build_backup': str(row.get('Previous Build Backup', '')).strip() or None,
                        'build_status': str(row.get('Build Status', 'success')).strip().lower() or 'success',
                        'deploy_status': str(row.get('Deploy Status', 'success')).strip().lower() or 'success',
                        'notes': str(row.get('Notes', '')).strip() or None,
                        'deployed_by': str(row.get('Deployed By', '')).strip() or None,
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    }

                    # Clean up 'nan' values
                    for key, val in deployment.items():
                        if val and str(val).lower() == 'nan':
                            deployment[key] = None

                    if not dry_run:
                        cursor.execute("""
                            INSERT INTO deployments (
                                jira_id, project_id, component_id, timestamp, environment,
                                vcs_url, developer_name, build_server, deploy_server,
                                database_name, db_backup_location, database_script,
                                previous_build_backup, build_status, deploy_status,
                                notes, deployed_by, created_at, updated_at
                            ) VALUES (
                                :jira_id, :project_id, :component_id, :timestamp, :environment,
                                :vcs_url, :developer_name, :build_server, :deploy_server,
                                :database_name, :db_backup_location, :database_script,
                                :previous_build_backup, :build_status, :deploy_status,
                                :notes, :deployed_by, :created_at, :updated_at
                            )
                        """, deployment)

                    existing.add(record_key)
                    imported += 1

                except Exception as e:
                    errors.append(f"Error in {excel_file} row {idx}: {e}")

    if not dry_run:
        conn.commit()

    conn.close()

    print(f"\n{'=' * 50}")
    print(f"Import Summary {'(DRY RUN)' if dry_run else ''}")
    print(f"{'=' * 50}")
    print(f"Imported: {imported}")
    print(f"Skipped (duplicates): {skipped}")
    print(f"Errors: {len(errors)}")

    if errors:
        print(f"\nErrors encountered:")
        for err in errors[:20]:
            print(f"  - {err}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more")

    return imported, skipped, errors


def verify_counts(reports_path: str, db_path: str):
    """Verify that DB counts match Excel counts."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\n" + "=" * 50)
    print("Verification")
    print("=" * 50)

    # Count by month in DB
    cursor.execute("""
        SELECT strftime('%Y-%m', timestamp) as month, COUNT(*)
        FROM deployments
        GROUP BY month
        ORDER BY month
    """)
    db_counts = {row[0]: row[1] for row in cursor.fetchall()}

    # Count by month in Excel
    excel_counts = {}
    for month_folder in os.listdir(reports_path):
        month_path = os.path.join(reports_path, month_folder)
        if not os.path.isdir(month_path):
            continue

        # Parse month from folder name (e.g., Nov_2025 -> 2025-11)
        month_map = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        parts = month_folder.split('_')
        if len(parts) == 2:
            month_num = month_map.get(parts[0], '00')
            year = parts[1]
            month_key = f"{year}-{month_num}"
        else:
            continue

        total = 0
        for f in os.listdir(month_path):
            if f.endswith('.xlsx'):
                df = pd.read_excel(os.path.join(month_path, f))
                total += len(df)

        excel_counts[month_key] = total

    print("\nMonth     | Excel | DB    | Match")
    print("-" * 40)

    all_match = True
    for month in sorted(set(list(excel_counts.keys()) + list(db_counts.keys()))):
        excel = excel_counts.get(month, 0)
        db = db_counts.get(month, 0)
        match = "✓" if excel == db else "✗"
        if excel != db:
            all_match = False
        print(f"{month}  | {excel:5} | {db:5} | {match}")

    print("-" * 40)
    print(f"Total     | {sum(excel_counts.values()):5} | {sum(db_counts.values()):5}")

    conn.close()
    return all_match


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import Excel data to database")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually import, just show what would be done")
    parser.add_argument("--verify", action="store_true", help="Only verify counts, don't import")
    args = parser.parse_args()

    reports_path = "/home/kannan/Projects/Active/chklst/reports"
    db_path = "/home/kannan/Projects/Active/chklst/data/chklst.db"

    if args.verify:
        verify_counts(reports_path, db_path)
    else:
        import_excel_files(reports_path, db_path, dry_run=args.dry_run)
        verify_counts(reports_path, db_path)
