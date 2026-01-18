from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)  # frontend se call allow karega

@app.route("/")
def home():
    return "BEU Result Backend Running"

@app.route("/api/result", methods=["POST"])
def result():
    data = request.get_json()
    reg_no = data.get("reg_no")
    sem = data.get("sem")

    if not reg_no or not sem:
        return jsonify({"success": False, "message": "Registration number and semester required"}), 400

    url = "https://beu-bih.ac.in/result-one"

    payload = {
        "reg_no": reg_no,
        "sem": sem
    }

    res = requests.post(url, data=payload, timeout=20)
    soup = BeautifulSoup(res.text, "html.parser")

    tables = soup.find_all("table")
    if len(tables) < 4:
        return jsonify({"success": False, "message": "Result not found"}), 404

    # Student Info
    info_table = tables[0]
    student = {}
    for r in info_table.find_all("tr"):
        t = r.text.replace("\n", " ").strip()
        if "Registration No" in t:
            student["reg_no"] = t.split(":")[-1].strip()
        if "Student Name" in t:
            student["name"] = t.split(":")[-1].strip()
        if "Course Name" in t:
            student["course"] = t.split(":")[-1].strip()
        if "College Name" in t:
            student["college"] = t.split(":")[-1].strip()

    # Theory
    theory = []
    for tr in tables[1].find_all("tr")[1:]:
        td = tr.find_all("td")
        theory.append({
            "code": td[0].text.strip(),
            "name": td[1].text.strip(),
            "ese": td[2].text.strip(),
            "ia": td[3].text.strip(),
            "total": td[4].text.strip(),
            "grade": td[5].text.strip(),
            "credit": td[6].text.strip()
        })

    # Practical
    practical = []
    for tr in tables[2].find_all("tr")[1:]:
        td = tr.find_all("td")
        practical.append({
            "code": td[0].text.strip(),
            "name": td[1].text.strip(),
            "ese": td[2].text.strip(),
            "ia": td[3].text.strip(),
            "total": td[4].text.strip(),
            "grade": td[5].text.strip(),
            "credit": td[6].text.strip()
        })

    # SGPA
    sgpa = []
    for tr in tables[3].find_all("tr")[1:]:
        sgpa.append([x.text.strip() for x in tr.find_all("td")])

    return jsonify({
        "success": True,
        "student": student,
        "theory": theory,
        "practical": practical,
        "sgpa": sgpa
    })

if __name__ == "__main__":
    app.run()
