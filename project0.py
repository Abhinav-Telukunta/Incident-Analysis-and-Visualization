import urllib.request
import ssl
import os
import pypdf
from pypdf import PdfReader
import re
import sqlite3

def download_data(pdf_url):
    # Define the path for the tmp directory within the project folder
    project_dir = os.getcwd()  # This gets the current working directory (your project folder)
    tmp_dir = os.path.join(project_dir, "tmp")
    file_path = os.path.join(tmp_dir, "incident_summary.pdf")

    # Ensure the tmp directory exists (create it if it doesn't)
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    # Create an unverified SSL context 
    context = ssl._create_unverified_context()

    # Fetch the URL without SSL certificate verification
    response = urllib.request.urlopen(pdf_url, context=context)
    data = response.read()

    # Save the data to a file
    with open(file_path, 'wb') as f:
        f.write(data)

    return file_path

def extract_fields(incidents):

    # pattern for identifying First letter capital then all letters lowercase
    pascal_case = r"([A-Z][a-z]+(\s|\/)*)+"
    
    # pattern for start word uppercase and then First letter capital then all lowercase
    uppercase_start = r"(MVA|COP|EMS)(\s[A-Z][a-z]+)+"

    # pattern for all uppercase characters appearing in middle or end
    uppercase_middle = r"([A-Z][a-z]+(\s|\/)*)+(EMS|AICD|HazMat)(\s)([A-Z][a-z]+(\s|\/)*)*"

    # pattern for all uppercase
    just_uppercase = r"COP DDACTS"

    # pattern for 911 in beginning and then First letter capital then all lowercase
    numbers = r"911(\s[A-Z][a-z]+)+"

    # pattern for some lowercase characters in the middle
    uppercase_and_lowercase = r"([A-Z][a-z]+(\s)+)+([a-z]+(\s)*)+([A-Z][a-z]+(\s)*)+"

    # final nature pattern 
    nature_pattern = fr"{uppercase_middle}|{uppercase_start}|{just_uppercase}|{numbers}|{uppercase_and_lowercase}|{pascal_case}"

    page_data = []

    for incident in incidents:
        # extract all required fields
        time = re.search(r"\d{1,2}:\d{2}", incident).group()
        incident_number_match = re.search(r"\d{4}-\d{8}", incident)
        incident_ori = re.search(r"OK0140200|EMSSTAT|14005|14009|COMMAND", incident).group()
        nature_match = re.search(nature_pattern,incident)
        location = incident[incident_number_match.end()+1:nature_match.start()]
        page_data.append((time,incident_number_match.group(),location.strip(),nature_match.group().strip(),incident_ori))

    return page_data

def extract_data(file_path):

    # using pdfReader to read pdf data
    reader = PdfReader(file_path) 

    data = []

    for i in range(0,len(reader.pages)):
        rows = reader.pages[i].extract_text().split('\n') 
        if i==0:
            # if it is 1st page, then remove first 2 headings
            rows = rows[1:len(rows)-1]
            rows[-1] = rows[-1].replace("NORMAN POLICE DEPARTMENT","")
        elif i==len(reader.pages)-1:
            # if it is last page, then remove last row since it just contains timestamp
            rows = rows[:len(rows)-1]

        incidents = []

        for row in rows:
            # handling multi line scenario
            if re.search(r"\d{1,2}:\d{2}",row) is None:
                incidents[-1] = incidents[-1]+row
            else:
                incidents.append(row)

        data.append(extract_fields(incidents))

    return data


def create_db():

    # Path to create the 'resources' folder in the current directory
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.join(cur_dir, 'resources')

    # Create the folder if it doesn't exist
    os.makedirs(resources_dir, exist_ok=True)

    # Path to the SQLite database file
    db_path = os.path.join(resources_dir, 'normanpd.db')

    # drop the database if it already exists
    drop_db(db_path)

    # Connect to the SQLite database (creates a new file)
    conn = sqlite3.connect(db_path)

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # SQL command to create the incidents table
    create_table_query = '''
    CREATE TABLE incidents (
        incident_time TEXT,
        incident_number TEXT,
        incident_location TEXT,
        nature TEXT,
        incident_ori TEXT
    );
    '''

    # Execute the query
    cursor.execute(create_table_query)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    return db_path



def populate_db(db_path, data):
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    
    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # SQL command to insert data into the incidents table
    insert_query = '''
    INSERT INTO incidents (incident_time, incident_number, incident_location, nature, incident_ori)
    VALUES (?, ?, ?, ?, ?);
    '''

    # Loop through the list of lists of tuples (incidents)
    for page_incidents in data:
        for incident in page_incidents:
            # Each incident is a tuple (incident_time, incident_number, incident_location, nature, incident_ori)
            cursor.execute(insert_query, incident)

    # Commit the changes to save the inserted data
    conn.commit()

    # Close the database connection
    conn.close()



def status(db_path):

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL query to count the number of times each 'nature' of incident has occurred
    query = '''
    SELECT nature, COUNT(*) as count
    FROM incidents
    GROUP BY nature
    ORDER BY nature;
    '''
    
    # Execute the query and fetch the results
    cursor.execute(query)
    results = cursor.fetchall()

    # Close the connection
    conn.close()

    collected_data = []

    for nature, count in results:
        collected_data.append([nature,int(count)])

    return collected_data

def drop_db(db_path):

    # Check if the database file exists
    if os.path.exists(db_path):
        try:
            # Remove (delete) the database file
            os.remove(db_path)
        except Exception as e:
            print(f"An error occurred while deleting the database: {e}")

def remove_file(file_path):
    
    # Check if the file at file_path exists
    if os.path.exists(file_path):
        try:
            # Remove (delete) the file
            os.remove(file_path)
        except Exception as e:
            print(f"An error occurred while deleting the file at {file_path}: {e}")
    else:
        print(f"File not found at {file_path}.")

    # Get the directory path (in this case, the 'tmp' directory)
    tmp_dir = os.path.dirname(file_path)

    # Check if the tmp directory is empty
    if os.path.exists(tmp_dir) and not os.listdir(tmp_dir):  # os.listdir() returns a list of files in the directory
        try:
            # Remove the empty directory
            os.rmdir(tmp_dir)
        except Exception as e:
            print(f"An error occurred while removing the directory {tmp_dir}: {e}")
    else:
        print(f"Directory {tmp_dir} not empty or not found.")

    
    











