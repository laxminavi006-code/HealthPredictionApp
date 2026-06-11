import google.generativeai as genai
from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime


app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS patients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        dob TEXT,
        email TEXT,
        glucose REAL,
        haemoglobin REAL,
        cholesterol REAL,
        remarks TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

def predict(glucose, haemoglobin, cholesterol):

    try:

        model = genai.GenerativeModel("gemini-2.0-flash")

        prompt = f"""
        Patient Blood Test Results:

        Glucose: {glucose}
        Haemoglobin: {haemoglobin}
        Cholesterol: {cholesterol}

        Predict possible health risks in one short sentence.
        """

        response = model.generate_content(prompt)

        return response.text.strip()

    except Exception:

        risks = []

        if glucose > 180:
            risks.append("High Diabetes Risk")

        if cholesterol > 240:
            risks.append("High Cholesterol Risk")

        if haemoglobin < 12:
            risks.append("Possible Anemia Risk")

        if glucose > 180 and cholesterol > 240:
            risks.append("Possible Cardiovascular Risk")

        if len(risks) == 0:
            return "Normal Health Indicators"

        return ", ".join(risks)


@app.route('/')
def index():

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM patients")
    patients = c.fetchall()

    conn.close()

    return render_template('index.html', patients=patients)


@app.route('/add', methods=['GET', 'POST'])
def add():

    if request.method == 'POST':

        name = request.form['name']
        dob = request.form['dob']
        email = request.form['email']

        glucose = float(request.form['glucose'])
        haemoglobin = float(request.form['haemoglobin'])
        cholesterol = float(request.form['cholesterol'])

        remarks = predict(glucose, haemoglobin, cholesterol)

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""
        INSERT INTO patients
        (name,dob,email,glucose,haemoglobin,cholesterol,remarks)
        VALUES (?,?,?,?,?,?,?)
        """,
        (name,dob,email,glucose,haemoglobin,cholesterol,remarks))

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('add_patient.html')


@app.route('/delete/<int:id>')
def delete(id):

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("DELETE FROM patients WHERE id=?", (id,))
    conn.commit()

    conn.close()

    return redirect('/')


@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':

        name = request.form['name']
        dob = request.form['dob']
        email = request.form['email']

        glucose = float(request.form['glucose'])
        haemoglobin = float(request.form['haemoglobin'])
        cholesterol = float(request.form['cholesterol'])

        remarks = predict(glucose,haemoglobin,cholesterol)

        c.execute("""
        UPDATE patients
        SET name=?,dob=?,email=?,glucose=?,haemoglobin=?,cholesterol=?,remarks=?
        WHERE id=?
        """,
        (name,dob,email,glucose,haemoglobin,cholesterol,remarks,id))

        conn.commit()
        conn.close()

        return redirect('/')

    c.execute("SELECT * FROM patients WHERE id=?", (id,))
    patient = c.fetchone()

    conn.close()

    return render_template('edit_patient.html', patient=patient)


if __name__ == '__main__':
    app.run(debug=True)