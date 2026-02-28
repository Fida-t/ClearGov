
from flask import Flask, render_template, request, redirect, url_for, session

import sqlite3

app = Flask(__name__)
app.secret_key = "123abcd"


citizen_queries = []  





# Temporary storage (for hackathon demo)
users = {}         # citizen users
govt_users = {}    # government users

def init_db():
    conn = sqlite3.connect("cleargov.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            question TEXT,
            answer TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=["GET"])
def home():
    return render_template('index.html')

@app.route("/select_role")
def select_role():
    return render_template("select_role.html")





@app.route("/govt_login", methods=["GET", "POST"])
def govt_login():
    if request.method == "POST":
        emp_id = request.form["employee_id"]
        password = request.form["password"]

        if emp_id in govt_users and govt_users[emp_id]["password"] == password:
            return redirect(url_for("govt_dashboard", employee_id=emp_id))
        else:
            return "Invalid credentials. Please try again."

    return render_template("govt_login.html")




@app.route("/govt_register", methods=["GET", "POST"])
def govt_register():
    if request.method == "POST":
        name = request.form["name"]
        emp_id = request.form["employee_id"]
        password = request.form["password"]

        # Save in temporary dictionary
        govt_users[emp_id] = {
            "name": name,
            "password": password
        }

        # Redirect to dashboard
        return redirect(url_for("govt_dashboard", employee_id=emp_id))

    return render_template("govt_register.html")

@app.route("/citizen_login", methods=["GET", "POST"])
def citizen_login():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]

        if name in users and users[name]["password"] == password:
            session["username"] = name   # <--- store in session
            return redirect(url_for("dashboard", username=name))
        else:
            return "Invalid credentials"

    return render_template("citizen_login.html")




@app.route('/govt_dashboard', methods=['GET','POST'])
def govt_dashboard():
    return render_template('govt_dashboard.html')




# REGISTER PAGE
@app.route("/citizen_register", methods=["GET", "POST"])
def citizen_register():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        password = request.form["password"]

        users[name] = {"phone": phone, "password": password}
        return redirect(url_for("dashboard", username=name))

    return render_template("citizen_register.html")

@app.route("/dashboard/<username>")
def dashboard(username):
    return render_template("citizen_dashboard.html", username=username)

@app.route("/documents/passport")
def passport_docs():
    if not session.get("username"):
        return redirect(url_for("citizen_login"))
    return render_template("passport_checklist.html")

@app.route("/documents/voter_id")
def voter_docs():
    if not session.get("username"):
        return redirect(url_for("citizen_login"))
    return render_template("votersid_checklist.html")

@app.route("/documents/drivers_license")
def drivers_docs():
    if not session.get("username"):
        return redirect(url_for("citizen_login"))
    return render_template("drivinglicense_checklist.html")


@app.route('/ask_query', methods=['GET','POST'])
def ask_query():
    if request.method == "POST":
        name = request.form.get("name")
        query_text = request.form.get("query")
        citizen_queries.append({
            "id": len(citizen_queries),  # assign an index
            "name": name,
            "query": query_text,
            "answer": "",
            "status": "Pending"
        })
        return redirect(url_for('ask_query'))
    return render_template('ask_query.html', queries=citizen_queries)


@app.route('/admin_queries', methods=['GET','POST'])
def admin_queries():
    if request.method == "POST":
        query_index = int(request.form.get("query_index"))
        answer = request.form.get("answer")
        citizen_queries[query_index]["answer"] = answer
        citizen_queries[query_index]["status"] = "Answered"
        return redirect(url_for('admin_queries'))

    return render_template('admin_queries.html', queries=citizen_queries)


@app.route("/reply/<int:id>", methods=["POST"])
def reply(id):
    answer = request.form["answer"]

    conn = sqlite3.connect("cleargov.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE queries SET answer = ?, status = ? WHERE id = ?",
        (answer, "Answered", id)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin_queries"))


# Temporary storage for knowledge posts
knowledge_posts = []  # each post: {"id": int, "author": str, "title": str, "content": str}

# Temporary storage for blog posts
knowledge_posts = []

@app.route('/knowledge', methods=['GET', 'POST'])
def knowledge():
    if request.method == "POST":
        username = session.get("username")  # Only registered users have a session
        if not username:
            return "You must be logged in to post knowledge.", 403

        title = request.form.get("title")
        content = request.form.get("content")

        knowledge_posts.append({
            "username": username,
            "title": title,
            "content": content
        })
        return redirect(url_for('knowledge'))

    return render_template('knowledge.html', posts=knowledge_posts, username=session.get("username"))

@app.route("/knowledge/new", methods=["GET", "POST"])
def new_post():
    # check if user is logged in
    if not session.get("username"):
        return redirect(url_for("citizen_login"))

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        author = session["username"]

        knowledge_posts.append({
            "id": len(knowledge_posts) + 1,
            "author": author,
            "title": title,
            "content": content
        })

        return redirect(url_for("knowledge"))

    return render_template("new_knowledge.html")






@app.route("/drivers_license")
def drivers_license():
    
    documents = [
        "Aadhar Card (Identity Proof)",
        "Address Proof (Electricity Bill / Ration Card)",
        "Birth Certificate or 10th Marksheet",
        "Passport Size Photos",
        "Learner's License"
    ]
    
    steps = [
        "Apply online through Parivahan website",
        "Book a driving test slot",
        "Visit the RTO office",
        "Give driving test",
        "Receive Driving License by post"
    ]
    
    estimated_cost = "₹500 - ₹1500 (varies by state)"
    
    return render_template(
        "drivers_license.html",
        docs=documents,
        process_steps=steps,
        cost=estimated_cost
    )


@app.route("/voters_id")
def voters_id():
    
    documents = [
        "Aadhar Card (Identity Proof)",
        "Address Proof",
        "Passport Size Photograph",
        "Mobile Number",
        "Age Proof (Birth Certificate / 10th Marksheet)"
    ]
    
    steps = [
        "Visit the National Voters' Service Portal",
        "Fill Form 6 for new voter registration",
        "Upload required documents",
        "Submit the application",
        "Wait for verification",
        "Receive Voter ID card by post"
    ]
    
    estimated_cost = "Free of cost"
    
    return render_template(
        "voters_id.html",
        docs=documents,
        process_steps=steps,
        cost=estimated_cost
    )

@app.route("/passport")
def passport():
    
    passport_data = {
        "Adult": {
            "documents": [
                "Aadhar Card",
                "PAN Card",
                "Address Proof",
                "Birth Certificate"
            ],
            "cost": "₹1500 (Normal) / ₹3500 (Tatkal)"
        },
        
        "Minor": {
            "documents": [
                "Birth Certificate",
                "Parents' Passport Copy",
                "Address Proof of Parents",
                "Passport Size Photos"
            ],
            "cost": "₹1000"
        },
        
        "Senior Citizen": {
            "documents": [
                "Aadhar Card",
                "Age Proof",
                "Address Proof",
                "Old Passport (if renewal)"
            ],
            "cost": "₹1500"
        }
    }

    return render_template("passport.html", passport_data=passport_data)


if __name__ == "__main__":
    app.run(debug=True, port=5001)