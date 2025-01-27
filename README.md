## Project Description 

This project is a Python-based application designed to process, analyze, and visualize incident data effectively. It provides users with an intuitive way to understand patterns in incident records, enabling better insights and decision-making. The application focuses on generating meaningful visualizations and making data exploration more accessible.

## How to install

 - Install pipenv using sudo apt install pipenv

 - Then, it would create a virtual environment in the current directory.

 - Activate the virtual environment using pipenv shell.

 - Install scikit-learn using command pipenv install scikit-learn

 - Install pandas using command pipenv install pandas

 - Install flask using command pipenv install flask

 - Install wordcloud using command pipenv install wordcloud

 - Install scipy using command pipenv install scipy

 - Install pypdf using command pipenv install pypdf

 - Install pytest using command pipenv install pytest

 - Make sure python is also installed

## How to run

 - Open Terminal in the project root directory

 - Activate virtual environment using command pipenv shell

 - Then run command for example: pipenv run python app.py to launch server on localhost. Click on it to view app on browser. Upload the incident files and then click Visualize. All the visualizations would be displayed.

 - For running tests, run command pipenv run python -m pytest from root directory.


## Functions

### app.py 

The app.py script serves as the entry point for the project, orchestrating the entire process of extracting, storing, analyzing and visualizing incident report data. It leverages functions defined in the project0.py module to handle specific tasks like extracting incident information, and managing a SQLite database.

  - index(): Serves the homepage of the application, renders the index.html template, which allows users to upload incident files.
  - upload_file(): Handles file uploads and processes incident data.
  - process_files(filepaths): Extracts text data from uploaded incident files.
  - create_db(): Creates an SQLite database for storing incident data.
  - populate_db(db_path, data): Inserts extracted incident data into the database.
  - status(db_path): Fetches incident types and their counts from the database.
  - vectorize(collected_data, df): Converts text data into numerical vectors for clustering.
  - generate_visualizations(X, df, collected_data): Creates and saves visualizations for the processed data.
  - app.run(debug=True): Runs the Flask application in debug mode for local development.

### project0.py

The project0.py file provides functions for handling PDF data extraction, SQLite database creation, data population, and cleanup. Each function plays a crucial role in processing incident report data. Below is a description of each function:

 - download_data(pdf_url): Downloads a PDF file from the given URL and stores it in a temporary directory.
 - extract_fields(incidents): Extracts specific incident details like time, location, and nature using regex patterns.
 - extract_data(file_path): Extracts text from the downloaded PDF and processes it into structured data.
 - create_db(): Creates an SQLite database and sets up the incidents table to store the extracted data.
 - populate_db(db_path, data): Inserts the extracted incident data into the SQLite database.
 - status(db_path): Queries the database and fetches a summary of incidents by nature and their count.
 - drop_db(db_path): Deletes the SQLite database file once the processing is complete.
 - remove_file(file_path): Deletes the downloaded PDF file and cleans up the temporary directory.

### test_functions.py

The test_functions.py file contains unit tests for various functions within the app.py file. The tests ensure that the functions are working as expected. Here's a description of each test:

 - test_extract_fields(): Tests the extract_fields function to ensure it correctly extracts the required information from incident strings.
 - test_create_db(): Verifies that the SQLite database and the incidents table are created successfully.
 - test_populate_db(): Ensures that the extracted incident data is correctly inserted into the SQLite database.
 - test_status(): Checks whether the incident counts by nature are fetched correctly.
 - test_generate_visualizations(): Verifies the functionality of the generate_visualizations() function. Tests whether three visualizations (clustering, bar and wordcloud are generated)
These tests use pytest and unittest.mock to simulate real scenarios and validate the functionality of the project code.

### Video

Watch the narrated video showcasing the full functionality of the website:

[Watch the full demo on YouTube](https://youtu.be/-p7T2LGma-o)


## Example Visualizations

![dendrogram](https://github.com/user-attachments/assets/e3beae4a-7e8c-4044-b6d6-b1358007f8b9)

![bar](https://github.com/user-attachments/assets/1205ab63-fcf6-444a-8802-fa125196f165)

![wordcloud](https://github.com/user-attachments/assets/c90a4327-755a-41c3-b85a-1b10446a2e07)



