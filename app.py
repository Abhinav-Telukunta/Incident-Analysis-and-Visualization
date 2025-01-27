from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from wordcloud import WordCloud
from scipy.cluster.hierarchy import linkage, dendrogram
import os
from project0 import extract_data, create_db, populate_db, status
import shutil
from sklearn.feature_extraction.text import TfidfVectorizer


app = Flask(__name__)
incidents_folder = 'incidents'
static_folder = 'static'
app.config['INCIDENTS_FOLDER'] = incidents_folder
app.config['STATIC_FOLDER'] = static_folder

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return "No files part in the request", 400
    
    files = request.files.getlist('files')  # Get list of uploaded files
    if not files:
        return "No files selected", 400

    if os.path.exists(app.config['INCIDENTS_FOLDER']): # if already incidents folder exists, remove it
        shutil.rmtree(app.config['INCIDENTS_FOLDER'])

    os.makedirs(incidents_folder, exist_ok=True)

    filepaths = []
    for file in files:
        if file.filename == '':
            return "One of the files has no name", 400

        # Save each file
        filepath = os.path.join(app.config['INCIDENTS_FOLDER'], file.filename)
        file.save(filepath) # save files in incident folder
        filepaths.append(filepath)

    data = process_files(filepaths) # extracting pages data

    db_path = create_db() # create database

    populate_db(db_path, data) # populate database with incident data

    collected_data = status(db_path) # fetch incident types and their counts from database

    df = pd.DataFrame(collected_data, columns=['Incident', 'Count'])

    X = vectorize(collected_data, df) # tf idf vectorizer on dataframe

    return generate_visualizations(X, df, collected_data) # plot visualizations

# vectorize
def vectorize(collected_data, df):
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(df['Incident'])
    return X

# extracting page data from incident pdf's
def process_files(filepaths):
    data = []

    for filepath in filepaths:
        data.extend(extract_data(filepath))

    return data

# plot visualizations (clustering, bar graph, word cloud)
def generate_visualizations(X, df, collected_data):

    # if images folder already exists, remove it
    if os.path.exists(os.path.join(app.config['STATIC_FOLDER'],'images')):
        shutil.rmtree(os.path.join(app.config['STATIC_FOLDER'],'images'))
    
    os.makedirs(static_folder, exist_ok=True)

    images_folder = os.path.join(static_folder,'images')

    os.makedirs(images_folder, exist_ok=True)

    linkage_matrix = linkage(X.toarray(), method='ward') # hierarchial clustering of records
    plt.figure(figsize=(12, 6))
    dendrogram(
        linkage_matrix,
        labels=df['Incident'].values,  # Use incidents as labels
        leaf_rotation=90,              
        leaf_font_size=10,             
        color_threshold=0.5          
    )
    plt.title("Hierarchical Clustering Dendrogram")
    plt.xlabel("Incident Labels")
    plt.ylabel("Distance")
    plt.tight_layout() 
    dendrogram_path = os.path.join(images_folder, 'dendrogram.png')
    plt.savefig(dendrogram_path)
    plt.close()

    plt.figure(figsize=(12, 6))
    plt.bar(df["Incident"], df["Count"], color="skyblue")
    # Adding labels and title
    plt.xlabel("Incidents", fontsize=12)
    plt.ylabel("Counts", fontsize=12)
    plt.title("Incident Counts Bar Graph", fontsize=14)
    plt.xticks(rotation=90, ha="right")  # Rotate x-axis labels for readability
    plt.tight_layout()  
    bar_path = os.path.join(images_folder, 'bar.png')
    plt.savefig(bar_path)
    plt.close()

    # prepare frequency map for wordcloud
    incident_map = {}
    for lst in collected_data:
        incident_map[lst[0]] = lst[1]

    # Generate word cloud
    wordcloud = WordCloud(
        width=800, height=400,
        background_color='white',
        colormap='viridis'
    ).generate_from_frequencies(incident_map)
    # Plot word cloud
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")  
    plt.title("Incident Types Word Cloud", fontsize=16)
    wordcloud_path = os.path.join(images_folder, 'wordcloud.png')
    plt.savefig(wordcloud_path)
    plt.close()


    # Render results
    return render_template('visualizations.html', bar_path='images/bar.png',
                           wordcloud_path='images/wordcloud.png',
                           dendrogram_path='images/dendrogram.png')

if __name__ == '__main__':
    app.run(debug=True)