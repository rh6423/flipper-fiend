import argparse
import csv
import json
import subprocess
from os import path
import re

# #######################################
# # Script takes 5 arguments:
# # 1. Path to VPXTables directory
# # 2. Path to wheel image files
# # 3. Path to vpxtool application
# # 4. Path to VPinballX_GL application
# # 5. Specific VPX table file (optional)
# #
# # If the 5th argument is not provided, the script will scan all VPX tables in the 
# #   specified directory.
# #
# # If the 5th argument is provided, the script will scan only the specified VPX table.
# Test command:
# python scantables.py "~/Documents/VPXTables" "~/vpxpinball/wheelimg" "~/Documents/VPXTables/vpxtool" "foo" "Space\ Invaders\ \(Bally\ 1980\)\ v4.vpx"


def parse_arguments():
    parser = argparse.ArgumentParser(description='Scan VPX tables and update or add them to upopdb.csv.')
    parser.add_argument('vpx_table_path', help='Path to VPXTables directory')
    parser.add_argument('wheelimage_file_path', help='Path to wheel image files')
    parser.add_argument('vpxtool_app', help='Path to vpxtool application')
    parser.add_argument('vpx_command', help='Path to VPinballX_GL application')
    parser.add_argument('vpx_table', nargs='?', default=None, help='Specific VPX table file (optional)')
    # debug: print all arguments to the console
    args = parser.parse_args()
    print(args.vpx_table_path)
    print(args.wheelimage_file_path)
    print(args.vpxtool_app)
    print(args.vpx_command)
    print(args.vpx_table)
    return parser.parse_args()

def run_vpxtool_info(vpxtool_app, vpx_table_path, vpx_table):
    """
    Executes the vpxtool command to get information about a specific VPX table.

    :param vpxtool_app: Path to the vpxtool application.
    :param vpx_table: Path to the VPX table file.
    :return: The output from the vpxtool command as a string.
    """
    # Prepare the command to be executed. It's important to use the full path to both the vpxtool application
    # and the VPX table file to avoid any path resolution issues.
    # strip out any single quotes in vpx_table
    vpx_table = vpx_table.replace("'", "")

    #the command should look like ../vpxtool info vpx_table_path/vpx_table
    command = f"{vpxtool_app} info {path.join(vpx_table_path, vpx_table)}"

    # debug: print command to the console
    print(command)
    
    try:
        # Execute the command. The subprocess.run function is used here with the arguments:
        # - command: the command and its arguments as a list.
        # - capture_output: set to True to capture the command's standard output and standard error.
        # - text: set to True to get the output as a string instead of bytes.
        result = subprocess.run(command, capture_output=True, text=True, check=True, shell=True)
        
        # If the command was successful, its output is contained in result.stdout
        return result.stdout
    except subprocess.CalledProcessError as e:
        # If the command execution failed, an exception is raised.
        # Here, we're catching it to handle errors gracefully.
        print(f"Error executing vpxtool: {e}")
        return None


def parse_vpxtool_output(output, args):
    # Parse the output from the vpxtool command to extract key pieces of information.

    # Initialize a dictionary to hold the extracted information
    table_info = {
        'vpxversion': None,
        'tablename': None,
        'tableversion': None,
        'releasedate': None,
        'table_rules': None,
        'path': args.vpx_table if args.vpx_table else None
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


def run_vpxtool_index(vpxtool_app, vpx_table_path):
    
    # Indexes all tables in the specified directory using the vpxtool.
    # :param vpxtool_app: Path to the vpxtool application.
    # :param vpx_table_path: Path to the directory containing the VPX tables.
    # :return: The path to the generated vpxtool_index.json file or None if the operation fails.
    
    # Prepare the command to be executed. It's important to use the full path to the vpxtool application
    # and to specify the directory containing the VPX tables.
    # command = [vpxtool_app, 'index', vpx_table_path]
    command = f"{vpxtool_app} index {vpx_table_path}"
    # print label "index command: " the command to the console
    print(f"index command: {command}")
    
    try:
        # Execute the command. The subprocess.run function is used here with the arguments:
        # - command: the command and its arguments as a list.
        # - capture_output: set to True to capture the command's standard output and standard error.
        # - text: set to True to get the output as a string instead of bytes.
        result = subprocess.run(command, capture_output=True, text=True, check=True, shell=True)
        
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


def parse_vpxtool_json(json_file, args):
    # Parses the vpxtool_index.json file to extract details about each VPX table.
    # :param json_file: Path to the vpxtool_index.json file.
    # :return: A list of dictionaries, each containing details of a VPX table.
    try:
        with open(json_file, mode='r', encoding='utf-8') as f:
            # Load the JSON data from the file
            data = json.load(f)
            # print a dictionary of the data to the console
            print(f"data: {data}")
            # how many data.tables are there?
            print(f"length of data['tables']: {len(data['tables'])}")
            # print the keys of the first entry in data['tables'] to the console
            print(f"keys of the first entry in data['tables']: {data['tables'][0].keys()}")
            # print the keys of data.tables.table_info to the console.
            print(f"keys of data['tables'][0]['table_info']: {data['tables'][0]['table_info'].keys()}")
            # print the values of the first entry in data['tables'] to the console, including the keys and values of the table_info dictionary
            print(f"values of the first entry in data['tables'][0]: {data['tables'][0]}")
            # Extract the information for each table
            # each table in data['tables'] is a dictionary. Use these keys in tables_info:
            # table_name, vpx_version, version, release_date, rules
            tables_info = []
            # print debug to the console: starting parse_vpxtool_json loop
            print("starting parse_vpxtool_json loop")
            # print debug: looping count of data['tables'] times
            print(f"looping count of data['tables'] times: {len(data['tables'])}")
            tablenumber = 1
            for table in data['tables']:
                print(f"table_name: {table['table_info']['path']}")
                # extract the flat table_info dictionary from the nested table data
                table_info = {
                    'table_name': table['table_info']['path'],
                    'version': table['table_info']['table_version'],
                    'release_date': table['table_info']['release_date'],
                    'rules': table['table_info']['table_rules'],
                    'path': args.vpx_table if args.vpx_table else None
                }
                tables_info.append(table_info)
                # print debug to the console when the loop completes and give the table number
                print("parse_vpxtool_json loop complete for table number: " + str(tablenumber))
                # if the table number is equal to length of data['tables'], print the table_info to the console
                if tablenumber == len(data['tables']):
                    # print the name of the last table in the loop to the console
                    print(f"Last table in loop done: {table_info['table_name']}")
                tablenumber += 1
            return tables_info
    except FileNotFoundError:
        print(f"File not found: {json_file}")
        return []
    except Exception as e:
        print(f"Error reading {json_file}: {e}")
        return []



def read_upopdb(csv_path):
    
    # Reads the upopdb.csv file and returns its contents as a list of dictionaries.
    # :param csv_path: Path to the upopdb.csv file.
    # :return: A list of dictionaries, each representing a row in the upopdb.csv file.
    
    try:
        with open(csv_path, mode='r', encoding='utf-8') as csvfile:
            # Use DictReader to read the CSV file into a list of dictionaries.
            # Each dictionary corresponds to a row in the CSV, with keys being the column headers.
            reader = csv.DictReader(csvfile)
            # Convert the reader object to a list to return all rows at once
            rows = list(reader)
            # Generate a unique ID by finding the max ID in existing_data and adding 1
            if rows:  # Check if existing_data is not empty
                max_id = max(int(row['id']) for row in rows)
                next_id = max_id + 1
            else:
                next_id = 1  # Starting ID if existing_data is empty

            print(f"new_id: {next_id}")
            return rows, next_id
    except FileNotFoundError:
        print(f"File not found: {csv_path}")
        return []
    except Exception as e:
        print(f"Error reading {csv_path}: {e}")
        return []


"""
def update_upopdb(csv_path, table_info):
    existing_data = read_upopdb(csv_path)
    table_found = False

    # Normalize the input table's filename for comparison
    input_file_name = table_info['vpx_table'].strip().lower()

    for row in existing_data:
        existing_file_name = row['vpx_file_name'].strip().lower()
        if existing_file_name == input_file_name:
            row.update({
                'display_name': table_info['tablename'],
                # Update other fields as necessary
            })
            table_found = True
            break

    if not table_found:
        # Handle adding new entries as before
        pass

    # Continue with writing the updated data back to the CSV file

    """

def update_upopdb(csv_path, table_info):
    # Assuming read_upopdb returns a tuple: (list_of_rows, next_id)
    existing_data, id_value = read_upopdb(csv_path)
    print(f"id_value: {id_value}")

    
    table_found = False
    print(f"length of table_info: {len(table_info)}")
    print(f"keys of table_info: {table_info.keys()}")
    print(f"table_info: {table_info}")
    # print id_value to the console
    print(f"id_value: {id_value}")
    table_found = False
    # print the length of the dictionary for table_info to the console
    print(f"length of table_info: {len(table_info)}")
    # print the keys of the dictionary for table_info to the console
    print(f"keys of table_info: {table_info.keys()}")
    # print the dictionary for table_info to the console
    print(f"table_info: {table_info}")
    # generate an unique id
    # look for the highest id in the existing_data and add 1

    # Here, we assume 'vpx_table' is the correct key containing the file name
    for row in existing_data:
        # print all values contained in the row to the console
        print(f"row: {row}")
        display_name = f"{table_info['path']}"
        # real_file = vpx_file_name from row
        real_file = row['vpx_file_name']
        # DEBUG: print display_name and real_file and row['vpx_file_name'] to the console
        print(f"display_name: {display_name}")
        print(f"real_file: {real_file}")
        print(f"row['vpx_file_name']: {row['vpx_file_name']}")
        # remove the leading path from vpx_file_name
        vpx_file_name = re.sub(r"\\([ ])", r"\1", row['vpx_file_name'])
        if row['vpx_file_name'] == real_file:  # Direct string comparison
            row.update({
                'display_name': display_name,  # Assuming this needs to be provided or generated
                'notes': table_info.get('releasedate')  # Use table rules for notes, with a default value of '
                # Update other fields as necessary
            })
            table_found = True
            break
        if not table_found:
            # print table_info['path'] to the console
            print(table_info['path'])
            real_file = re.sub(r"\\([ ])", r"\1", table_info['path'])
            # Create a new row for the table
            new_row = {
                'id': id_value,  # local uuid for the table file
                'vpx_file_name': real_file,  # Assuming this needs to be provided or generated
                'VPS-ID': '',  # Assuming a default or generated value
                'image_file': '',  # Assuming this needs to be provided or generated
                'display_name': display_name,
                'show_in_arcade': '1',  # Assuming a default value
                'favorite': '',  # Assuming a default value
                'notes': table_info.get('releasedate')  # Use table rules for notes, with a default value of ''
            }
            existing_data.append(new_row)
            # increment the id_value
            id_value += 1

    # Write the updated data back to the CSV file
    with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'vpx_file_name', 'VPS-ID', 'image_file', 'display_name', 'show_in_arcade', 'favorite', 'notes']
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
    vpx_table_path = args.vpx_table_path
    vpx_table = args.vpx_table
    csv_path = 'upopdb.csv'  # Adjust the path to your upopdb.csv file as needed

    # Step 1: Run vpxtool to get information about the table
    vpxtool_output = run_vpxtool_info(vpxtool_app, vpx_table_path, vpx_table)
    if vpxtool_output is None:
        print(f"Failed to get information for table {vpx_table} using vpxtool.")
        return

    # Step 2: Parse the output from vpxtool
    table_info = parse_vpxtool_output(vpxtool_output, args)
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
    csv_path = 'upopdb.csv'  # Adjust the path to your upopdb.csv file as needed

    # Index all tables using vpxtool
    json_file_path = run_vpxtool_index(vpxtool_app, vpx_table_path)
    print(f"json_file_path: {json_file_path}")
    if json_file_path is None:
        print("Failed to index tables using vpxtool.")
        return
    """
    Here's an example entry from the json_file_path:
    {
      "path": "/Users/legba/Documents/VPXTables/Fun Land (Gottlieb 1968)_Teisen_MOD.vpx",
      "table_info": {
        "table_name": "Fun Land",
        "author_name": null,
        "table_blurb": null,
        "table_rules": null,
        "author_email": null,
        "release_date": null,
        "table_save_rev": "55",
        "table_version": "1.0",
        "author_website": null,
        "table_save_date": "Thu Sep 21 17:32:02 2023",
        "table_description": null,
        "properties": {}
      },
      "game_name": "FunLand_1968",
      "b2s_path": null,
      "local_rom_path": null,
      "requires_pinmame": false,
      "last_modified": "2023-09-22T00:32:02+00:00"
    },
    """

    # Parse the JSON file into table_info (information about all tables). Provide debug level output to the console
    tables_info = parse_vpxtool_json(json_file_path, args)
    # print the number of entries in the dictionary labeled "tables_info length: " to the console
    print(f"tables_info length: {len(tables_info)}")
    # verify the schema of tables_info matches the schema in the example entry above
    # extract the schema from the first entry in tables_info
    # print the table name for the first table to the console
    print(f"first table: {tables_info[0]['table_name']}")
    if not tables_info:
        print(f"Failed to parse table information from {json_file_path}.")
        return
    # check each table in the list - does it exist in the upopdb.csv file?
    for table in tables_info:
        # print the table name to the console
        print(f"table name returned to scan all tables: {table['table_name']}")
        # print the table path to the console
        print(f"table path returned to scan all tables: {table['path']}")
        # set table['path'] to str(table['table_name']) with the leading path stripped, and append the string '.vpx'
        table['path'] = str(table['table_name']).split('/')[-1] + '.vpx'
        # print correct table['path'] to the console
        print(f"correct table['path']: {table['path']}")



        # table['path'] = vpx_table_filename  # Assuming 'vpx_table' key is used in update_upopdb function  
        table['version'] = table.pop('table_version', 'Error')  # Rename 'table_version' to 'version
        table['release_date'] = table.pop('release_date', None)
        table['rules'] = table.pop('table_rules', None)
        # print both  the vpx_table_filename and the table_info to the console
        print(f"vpx_table_filename: {table['path']}")
        print(f"table_info: {table['path']}")
        # Update the CSV for each table
        update_upopdb(csv_path, table)
        """table_info = {
            'table_name': table['table_info']['table_name'],
            'version': table['table_info']['table_version'],
            'release_date': table['table_info']['release_date'],
            'rules': table['table_info']['table_rules'],
            'path': args.vpx_table if args.vpx_table else None
            """






    print(f"Successfully updated information for all tables in {vpx_table_path} in upopdb.csv.")


def main():
    args = parse_arguments()
    if args.vpx_table:
        scan_table(args)
        # this returns 
    else:
        scan_all_tables(args)

if __name__ == '__main__':
    main()
