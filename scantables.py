import argparse
import csv
import json
import subprocess
from os import path

def parse_arguments():
    parser = argparse.ArgumentParser(description='Scan VPX tables and update or add them to upopdb.csv.')
    parser.add_argument('vpx_table_path', help='Path to VPXTables directory')
    parser.add_argument('wheelimage_file_path', help='Path to wheel image files')
    parser.add_argument('vpxtool_app', help='Path to vpxtool application')
    parser.add_argument('vpx_command', help='Path to VPinballX_GL application')
    parser.add_argument('vpx_table', nargs='?', default=None, help='Specific VPX table file (optional)')
    return parser.parse_args()

import subprocess

def run_vpxtool_info(vpxtool_app, vpx_table):
    """
    Executes the vpxtool command to get information about a specific VPX table.

    :param vpxtool_app: Path to the vpxtool application.
    :param vpx_table: Path to the VPX table file.
    :return: The output from the vpxtool command as a string.
    """
    # Prepare the command to be executed. It's important to use the full path to both the vpxtool application
    # and the VPX table file to avoid any path resolution issues.
    command = [vpxtool_app, 'info', vpx_table]
    
    try:
        # Execute the command. The subprocess.run function is used here with the arguments:
        # - command: the command and its arguments as a list.
        # - capture_output: set to True to capture the command's standard output and standard error.
        # - text: set to True to get the output as a string instead of bytes.
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        # If the command was successful, its output is contained in result.stdout
        return result.stdout
    except subprocess.CalledProcessError as e:
        # If the command execution failed, an exception is raised.
        # Here, we're catching it to handle errors gracefully.
        print(f"Error executing vpxtool: {e}")
        return None


def parse_vpxtool_output(output):
    """
    Parses the output from the vpxtool command to extract key pieces of information.

    :param output: The string output from the vpxtool info command.
    :return: A dictionary containing the extracted information.
    """
    # Initialize a dictionary to hold the extracted information
    table_info = {
        'vpxversion': None,
        'tablename': None,
        'tableversion': None,
        'releasedate': None,
        'tablerules': None,
    }

    # Split the output into lines for easier processing
    lines = output.split('\n')

    # Iterate through each line, looking for the information we're interested in
    for line in lines:
        if 'VPX Version:' in line:
            table_info['vpxversion'] = line.split(': ')[1].strip()
        elif 'Table Name:' in line:
            table_info['tablename'] = line.split(': ')[1].strip()
        elif 'Version:' in line:
            table_info['tableversion'] = line.split(': ')[1].strip()
        elif 'Release Date:' in line:
            table_info['releasedate'] = line.split(': ')[1].strip()
        elif 'Rules:' in line:
            # The Rules field is expected to span multiple lines until the end of the output,
            # so we need to capture all subsequent lines as part of the rules.
            rules_index = lines.index(line)
            tablerules_lines = lines[rules_index + 1:]  # Get all lines after "Rules:"
            table_info['tablerules'] = '\n'.join(tablerules_lines).strip()
            break  # No need to continue processing after finding the rules

    return table_info


import subprocess

def run_vpxtool_index(vpxtool_app, vpx_table_path):
    """
    Indexes all tables in the specified directory using the vpxtool.

    :param vpxtool_app: Path to the vpxtool application.
    :param vpx_table_path: Path to the directory containing the VPX tables.
    :return: The path to the generated vpxtool_index.json file or None if the operation fails.
    """
    # Prepare the command to be executed. It's important to use the full path to the vpxtool application
    # and to specify the directory containing the VPX tables.
    command = [vpxtool_app, 'index', vpx_table_path]
    
    try:
        # Execute the command. The subprocess.run function is used here with the arguments:
        # - command: the command and its arguments as a list.
        # - capture_output: set to True to capture the command's standard output and standard error.
        # - text: set to True to get the output as a string instead of bytes.
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        # Assuming the indexing operation generates a vpxtool_index.json file in the specified directory,
        # construct the path to this file.
        json_file_path = path.join(vpx_table_path, 'vpxtool_index.json')
        
        # Optionally, you can check the output to confirm that the indexing was successful before returning the JSON file path.
        if 'Indexed' in result.stdout:
            return json_file_path
        else:
            print("Indexing failed or the output format has changed.")
            return None
    except subprocess.CalledProcessError as e:
        # If the command execution failed, an exception is raised.
        # Here, we're catching it to handle errors gracefully.
        print(f"Error executing vpxtool index: {e}")
        return None


import json

def parse_vpxtool_json(json_file):
    """
    Parses the vpxtool_index.json file to extract details about each VPX table.

    :param json_file: Path to the vpxtool_index.json file.
    :return: A list of dictionaries, each containing details of a VPX table.
    """
    try:
        # Open and load the JSON file
        with open(json_file, 'r') as file:
            data = json.load(file)

        # Initialize a list to hold the parsed table details
        tables_info = []

        # Check if the 'tables' key exists in the loaded data
        if 'tables' in data:
            # Iterate through each table entry in the JSON data
            for entry in data['tables']:
                table_info = {
                    'path': entry.get('path', ''),
                    'table_name': entry['table_info'].get('table_name', ''),
                    'author_name': entry['table_info'].get('author_name', ''),
                    'table_version': entry['table_info'].get('table_version', ''),
                    'release_date': entry['table_info'].get('release_date', ''),
                    'table_description': entry['table_info'].get('table_description', ''),
                    'table_rules': entry['table_info'].get('table_rules', '').replace('\r\n', '\n'), # Normalize line breaks
                }
                # Add the parsed table information to the list
                tables_info.append(table_info)

        return tables_info
    except Exception as e:
        print(f"Error parsing vpxtool_index.json: {e}")
        return []


import csv

def read_upopdb(csv_path):
    """
    Reads the upopdb.csv file and returns its contents as a list of dictionaries.

    :param csv_path: Path to the upopdb.csv file.
    :return: A list of dictionaries, each representing a row in the upopdb.csv file.
    """
    try:
        with open(csv_path, mode='r', encoding='utf-8') as csvfile:
            # Use DictReader to read the CSV file into a list of dictionaries.
            # Each dictionary corresponds to a row in the CSV, with keys being the column headers.
            reader = csv.DictReader(csvfile)
            # Convert the reader object to a list to return all rows at once
            rows = list(reader)
            return rows
    except FileNotFoundError:
        print(f"File not found: {csv_path}")
        return []
    except Exception as e:
        print(f"Error reading {csv_path}: {e}")
        return []



import csv

def update_upopdb(csv_path, table_info):
    """
    Updates or adds a table's information in upopdb.csv.

    :param csv_path: Path to the upopdb.csv file.
    :param table_info: A dictionary containing the table information to update or add.
    """
    # First, read the existing data
    existing_data = read_upopdb(csv_path)
    table_found = False

    # Check if the table already exists in the data
    for row in existing_data:
        if row['vpx_file_name'] == table_info['vpx_table']:
            # Update existing row with new information
            row.update({
                'display_name': table_info['tablename'],
                'notes': table_info['description']  # Assuming 'description' is the key for table description in table_info
            })
            table_found = True
            break

    # If the table was not found, add it as a new row
    if not table_found:
        new_row = {
            'd': '',  # Assuming 'd' needs a default value or is generated somehow
            'vpx_file_name': table_info['vpx_table'],
            'VPS-ID': '',  # Assuming a default or generated value
            'image_file': '',  # Assuming this needs to be provided or generated
            'display_name': table_info['tablename'],
            'show_in_arcade': '',  # Assuming a default value
            'favorite': '',  # Assuming a default value
            'notes': table_info['description']  # Assuming 'description' is the key for table description in table_info
        }
        existing_data.append(new_row)

    # Write the updated data back to the CSV file
    with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['d', 'vpx_file_name', 'VPS-ID', 'image_file', 'display_name', 'show_in_arcade', 'favorite', 'notes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header
        writer.writeheader()
        # Write the updated data
        writer.writerows(existing_data)


def scan_table(args):
    """
    Scans a single VPX table and updates or adds its information in upopdb.csv.

    :param args: Command line arguments passed to the script.
    """
    # Extract the relevant arguments
    vpxtool_app = args.vpxtool_app
    vpx_table = args.vpx_table
    csv_path = 'path/to/upopdb.csv'  # Adjust the path to your upopdb.csv file as needed

    # Step 1: Run vpxtool to get information about the table
    vpxtool_output = run_vpxtool_info(vpxtool_app, vpx_table)
    if vpxtool_output is None:
        print(f"Failed to get information for table {vpx_table} using vpxtool.")
        return

    # Step 2: Parse the output from vpxtool
    table_info = parse_vpxtool_output(vpxtool_output)
    if not table_info:
        print(f"Failed to parse information for table {vpx_table}.")
        return

    # Assuming that 'vpx_table' argument corresponds to the 'vpx_file_name' in upopdb.csv
    # Adjust the table_info dictionary keys as necessary
    table_info['vpx_table'] = args.vpx_table  # Add the 'vpx_table' key to table_info for update_upopdb

    # Step 3: Update upopdb.csv with the obtained table information
    update_upopdb(csv_path, table_info)
    print(f"Successfully updated information for table {vpx_table} in upopdb.csv.")


def scan_all_tables(args):
    """
    Scans all VPX tables in the specified directory and updates or adds their information in upopdb.csv.

    :param args: Command line arguments passed to the script.
    """
    # Extract the relevant arguments
    vpxtool_app = args.vpxtool_app
    vpx_table_path = args.vpx_table_path
    csv_path = 'path/to/upopdb.csv'  # Adjust the path to your upopdb.csv file as needed

    # Step 1: Index all tables using vpxtool
    json_file_path = run_vpxtool_index(vpxtool_app, vpx_table_path)
    if json_file_path is None:
        print("Failed to index tables using vpxtool.")
        return

    # Step 2: Parse the JSON file to get information about all tables
    tables_info = parse_vpxtool_json(json_file_path)
    if not tables_info:
        print("Failed to parse table information from the vpxtool index.")
        return

    # Step 3: Update upopdb.csv with the obtained tables information
    for table_info in tables_info:
        # The 'path' key from table_info is not needed for update_upopdb, so it's removed
        vpx_table_filename = table_info.pop('path', None).split('/')[-1]  # Extract filename for 'vpx_file_name'
        table_info['vpx_table'] = vpx_table_filename  # Assuming 'vpx_table' key is used in update_upopdb function

        # Update the CSV for each table
        update_upopdb(csv_path, table_info)

    print(f"Successfully updated information for all tables in {vpx_table_path} in upopdb.csv.")


def main():
    args = parse_arguments()
    if args.vpx_table:
        scan_table(args)
    else:
        scan_all_tables(args)

if __name__ == '__main__':
    main()
