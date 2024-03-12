import argparse
import csv
import json
import subprocess
import os
from fuzzywuzzy import process
import re
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


def parse_filename(vpx_file):
    """
    Extracts year, manufacturer, and name from the filename.
    This is a simplified example and may need to be adjusted.
    
    EXAMPLE filenames:
    1-2-3 (Talleres de Llobregat 1973) v4.vpx
    2001 (Gottlieb 1971) v0.99a.vpx
    250cc (Inder - 1992) v4.vpx
    300 (Special Edition) (Gottlieb 1975) team scampa123 mod  v1.1.vpx
    301 Bullseye (Grand Products 1986).vpx
    4 Aces (Williams 1970) JP_VPX8.vpx
    4X4 Atari.vpx
    8 Ball (Williams 1966) 1.2.1.vpx
    AC-DC LUCI Premium VR (Stern 2013) v1.1.vpx
    Aaron Spinlling (Data East 1992) v1.02.vpx
    AbraCaDabra (Gottlieb1975) 1.1.0.vpx
    AceOfSpeed.vpx
    Aces High (Bally 1965) v1.1.0 - 4K - Dakarx - English.vpx
    Aces High (Bally 1965).vpx
    Airport (Gottlieb 1969) 1.2.2.vpx
    Aladdin's Castle (Bally 1976) - DOZER - MJR_1.01.vpx
    Algar (Williams 1980) 1.33.vpx
    Alice in Wonderland (Gottlieb 1948) JP_VPX8.vpx
    Alien Poker (Williams 1980).vpx
    Alien Star (Gottlieb 1984) v2.0.1.vpx
    
    """
    # use a regex match on a space followed by four digits in a row 
    # to find the year in the vpx_file
    year_match = re.search(r'\s(\d{4})\)', vpx_file)
    year = int(year_match.group(1)) if year_match else None
    
    # extract the name and manufacturer as name and manufacturer likely needs refinement
    # the name is the first part of the filename
    # the manufacturer is the second part of the filename
    name_match = re.search(r'^(.*?)\s\(', vpx_file)
    name = name_match.group(1) if name_match else None
    manufacturer_match = re.search(r'\((.*?)\s\d{4}\)', vpx_file)
    manufacturer = manufacturer_match.group(1) if manufacturer_match else None
    return year, name, manufacturer


def find_closest_match(vpx_file, png_files):
    vpx_year, vpx_name, _ = parse_filename(vpx_file)
    if vpx_year is None or vpx_name is None:  # Ensure vpx_name is also checked
        print(f"Year or name not found for {vpx_file}, skipping...")
        return None

    best_match_score = 0
    best_match_file = None
    for png_file in png_files:
        if not png_file:  # Skip empty strings
            continue
        # Assuming png_file is the full path, extract just the file name
        png_name = os.path.basename(png_file).split('.')[0]  # Ensure it's treated as a string

        if not png_name:  # Additional check
            continue

        score = process.extractOne(vpx_name, [png_name])[1]  # Ensure inputs are strings
        if score > best_match_score:
            best_match_score = score
            best_match_file = png_file

    return best_match_file


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

    # spaces and parentheses in the file name need to be escaped
    vpx_table = vpx_table.replace(" ", "\ ")
    vpx_table = vpx_table.replace("(", "\(")
    vpx_table = vpx_table.replace(")", "\)")
    # if the vpx_table has multiple . in it, 

    #the command should look like ../vpxtool info vpx_table_path/vpx_table
    command = f"{vpxtool_app} info {path.join(vpx_table_path, vpx_table)}"

    # debug: print command to the console
    print(f"run_vpxtool_info command: {command}")

    
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


def update_upopdb(csv_path, table_info, wheelimage_file_path, wheel_image):
    existing_data, next_id = read_upopdb(csv_path)
    table_found = False
    # check for a matching wheel image file in the wheel_image
    # use the table_info['path'] with the .vpx extension removed as the base name
    # look in the wheel_image for a file with the same base name and a png, gif, webp or jpg extension
    # if a matching file is found, set table_info['image_file'] to the matching file name
    # if no matching file is found, set table_info['image_file'] to an empty string
    # use the os.path.splitext function to split the file name into the base name and the extension
    # img_file should be the path to the wheel_image directory/filename.png
    img_file = wheel_image
    # unless img_file is empty, remove the leading path from the file name
    if img_file:
        img_file = img_file.split('/')[-1]
    # print the image file to the console
    print(f"update_upopdb table_info['image_file']: {img_file}")
    
    for row in existing_data:
        if row['vpx_file_name'] == table_info['path']:
            # print original row to the console
            print(f"update_upopdb original row: {row}")
            # Update existing row
            row['image_file'] = img_file
            row['display_name'] = f"{table_info['tablename']}"
            row['show_in_arcade'] = '1'
            row['favorite'] = ''
            row['notes'] = table_info.get('releasedate', '')  # Default to empty string if not found
            row['year'] = table_info.get('year', '')
            row['manufacturer'] = table_info.get('manufacturer', '')
            table_found = True
            # print the row to the console
            print(f"update_upopdb row: {row}")
            break  # Stop searching once the table is found and updated
    
    if not table_found:
        # Append new row
        new_row = {
            'id': str(next_id),
            'vpx_file_name': table_info['path'],
            'VPS-ID': '',
            'image_file': '',
            # if table_info['tablename'] is not set, use the table_info['path'] instead
            'display_name': table_info['tablename'] if table_info['tablename'] else table_info['path'],
            'show_in_arcade': '1',
            'favorite': '',
            'notes': table_info.get('releasedate', ''),
            'year': table_info.get('year', ''),
            'manufacturer': table_info.get('manufacturer', '')
        }
        existing_data.append(new_row)

    # Write updates or new entry to CSV, outside the loop
    with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'vpx_file_name', 'VPS-ID', 'image_file', 'display_name', 'show_in_arcade', 'favorite', 'notes', 'year', 'manufacturer']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
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
    wheelimage_file_path = args.wheelimage_file_path


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
    wheelimage_file_path = args.wheelimage_file_path

    # call parse_filename to get the year, name, and manufacturer from the vpx_table
    year, name, manufacturer = parse_filename(vpx_table)
    
    # add the year, name, and manufacturer to the table_info dictionary
    table_info['year'] = year
    table_info['name'] = name
    table_info['manufacturer'] = manufacturer

    # get a list of wheel image files from the wheel_image
    # and store the list in the variable png_files
    png_files = subprocess.run(f"ls -1 {wheelimage_file_path}/*.png", capture_output=True, text=True, check=True, shell=True)
    
    # strip the leading path from each file name - /foo/bar/image.png becomes image.png
    png_files = png_files.stdout.split('\n')
    
    # find the closest match from the png_files
    wheel_image = find_closest_match(vpx_table, png_files)
    # print the closest match to the console
    print(f"Closest matching wheel for {table_info['vpx_table']} is: {wheel_image}")

    # Step 3: Update upopdb.csv with the obtained table information
    # Evaluate return from update_upopdb and error check to see if the update was successful
    # print the arguments to the console before calling update_upopdb
    print(f"csv_path: {csv_path}")
    print(f"table_info: {table_info}")
    print(f"wheelimage_file_path: {wheelimage_file_path}")
    print(f"wheel_image: {wheel_image}")
    print(f"about to call update_upopdb")
    update_upopdb(csv_path, table_info, wheelimage_file_path, wheel_image)


    



    print(f"Successfully updated information for table {vpx_table} in upopdb.csv.")


def scan_all_tables(args):
    # original code
    """
    Scans all VPX tables in the specified directory and updates or adds their information in upopdb.csv.

    :param args: Command line arguments passed to the script.
    """
    """
    # Extract the relevant arguments from args and store in vpxtool_app, vpx_table_path, and csv_path
    vpxtool_app = args.vpxtool_app
    vpx_table_path = args.vpx_table_path
    csv_path = 'upopdb.csv'  # Adjust the path to your upopdb.csv file as needed

    # Make a list of all tables in vpx_table_path (these are files that end in a .vpx extension)
    # and store the list in the variable vpx_tables
    # use the subprocess.run function to execute the command
    # the command should look like ls vpx_table_path/*.vpx
    vpx_tables = subprocess.run(f"ls -1 {vpx_table_path}/*.vpx", capture_output=True, text=True, check=True, shell=True)

    # Split the output from the command into a list of table names
    # the list of table names is stored in vpx_tables
    vpx_tables = vpx_tables.stdout.split('\n')

    # strip out the path from each table name
    # use a list comprehension to remove the path from each table name
    vpx_tables = [path.split('/')[-1] for path in vpx_tables]

    # print the total number of vpx_tables to the console
    print(f"Total number of tables: {len(vpx_tables)}")

    # Iterate through each table in the list and call scan_table for each table
    # use a for loop to iterate through each table in the list
    for vpx_table in vpx_tables:
        # call scan_table for each table
        # the call will need to pass modified args and include each table in the list
        # create my_args as a copy of args and substitute vpx_table for my_args.vpx_table
        # before calling scan_table
        my_args = args
        my_args.vpx_table = vpx_table
        scan_table(my_args)
        # print the table name to the console: "Scanning table: {vpx_table}"
        print(f"Scanning table: {vpx_table}")
        # print a count of the number of tables scanned so far to the console:
        # "Scanned {count} tables so far."
        count = len(vpx_tables)
        print(f"Scanned {count} tables so far.")
        count -= 1
        """
    # refactored code will call scan_table for each table in the list
    # Extract the relevant arguments from args and store in vpxtool_app, vpx_table_path, and csv_path
    # vpxtool_app = args.vpxtool_app
    vpx_table_path = args.vpx_table_path
    # csv_path = 'upopdb.csv'  # Adjust the path to your upopdb.csv file as needed

    # Make a list of all tables in vpx_table_path (these are files that end in a .vpx extension)
    # and store the list in the variable vpx_tables
    # use the subprocess.run function to execute the command
    # the command should look like ls vpx_table_path/*.vpx
    vpx_tables = subprocess.run(f"ls -1 {vpx_table_path}/*.vpx", capture_output=True, text=True, check=True, shell=True)

    # Split the output from the command into a list of table names
    # the list of table names is stored in vpx_tables
    vpx_tables = vpx_tables.stdout.split('\n')
    
    # strip out the path from each table name
    # use a list comprehension to remove the path from each table name
    vpx_tables = [path.split('/')[-1] for path in vpx_tables]
    count = len(vpx_tables)
    # print the total number of vpx_tables to the console
    print(f"Total number of tables: {len(vpx_tables)}")

    # Iterate through each table in the list and call scan_table for each table
    # use a for loop to iterate through each table in the list
    for vpx_table in vpx_tables:
        # call scan_table for each table
        # the call will need to pass modified args and include each table in the list
        # create my_args as a copy of args and substitute vpx_table for my_args.vpx_table
        # before calling scan_table
        my_args = args
        my_args.vpx_table = vpx_table
        scan_table(my_args)
        # print the table name to the console: "Scanning table: {vpx_table}"
        print(f"Scanning table: {vpx_table}")
        # print a count of the number of tables scanned so far to the console:
        # "Scanned {count} tables so far."
        print(f"Scanned {count} tables to go.")
        count -= 1


def main():
    args = parse_arguments()
    if args.vpx_table:
        scan_table(args)
        # this returns 
    else:
        scan_all_tables(args)

if __name__ == '__main__':
    main()
