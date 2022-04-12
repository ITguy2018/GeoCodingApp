from flask import Flask, render_template, request, send_file
from geopy.geocoders import ArcGIS
import os
import pandas as pd
import datetime

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", utc_dt=datetime.datetime.utcnow())


@app.route('/success-table', methods=['POST'])
def success_table():
    global filename
    if request.method == "POST":
        file = request.files['file']
        try:
            df = pd.read_csv(file)
            gc = ArcGIS(scheme='https')
            df["coordinates"] = df["Address"].apply(gc.geocode)
            df['Latitude'] = df['coordinates'].apply(
                lambda x: x.latitude if x != None else None)
            df['Longitude'] = df['coordinates'].apply(
                lambda x: x.longitude if x != None else None)
            df = df.drop("coordinates", 1)
            filename = datetime.datetime.now().strftime(
                "uploads/%Y-%m-%d-%H-%M-%S-%f" + ".csv")
            df.to_csv(filename, index=None)
            return render_template("index.html", text=df.to_html(), btn='download.html')
        except Exception as e:
            return render_template("index.html", text=str(e))


@app.route("/uploads", methods=['GET', 'POST'])
def download_file():
    try:
        return send_file(filename, mimetype='text/csv', attachment_filename='yourfile.csv', as_attachment=True)
    except Exception as e:
        return(e)


@app.route('/about/')
def about():
    return render_template('about.html')


if __name__ == "__main__":
    app.run(debug=False)
