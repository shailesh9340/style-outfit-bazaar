from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Folder for uploaded images
UPLOAD_FOLDER = 'static/images'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

# Sample outfits (initial)
outfits = []

# Customers (in-memory)
customers = []

# ------------------ Routes ------------------

# Home page
@app.route("/", methods=["GET"])
def home():
    query = request.args.get('search', '').lower()
    price_sort = request.args.get('price', '')
    category_filter = request.args.get('category', '')

    filtered = outfits
    if query:
        filtered = [o for o in filtered if query in o['name'].lower()]
    if category_filter:
        filtered = [o for o in filtered if o['category'] == category_filter]
    if price_sort == 'low':
        filtered = sorted(filtered, key=lambda x: x['price'])
    elif price_sort == 'high':
        filtered = sorted(filtered, key=lambda x: x['price'], reverse=True)

    return render_template("index.html", outfits=filtered)

# ------------------ Admin ------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            return redirect(url_for("dashboard"))
        else:
            return "Login Failed! Wrong Credentials"
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        name = request.form.get("name")
        link = request.form.get("link")
        category = request.form.get("category")
        price = int(request.form.get("price", 0))
        file = request.files.get("image")
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            outfits.append({
                "name": name,
                "link": link,
                "category": category,
                "image": filepath,
                "price": price
            })
    return render_template("dashboard.html", outfits=outfits)

# ------------------ Customer ------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if any(c['username'] == username for c in customers):
            return "Username already exists!"
        customers.append({"username": username, "password": password})
        return redirect(url_for("customer_login"))
    return render_template("customer_register.html")

@app.route("/customer_login", methods=["GET", "POST"])
def customer_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = next((c for c in customers if c['username'] == username and c['password'] == password), None)
        if user:
            session['customer'] = username
            return redirect(url_for("home"))
        else:
            return "Login Failed! Wrong Credentials"
    return render_template("customer_login.html")

@app.route("/customer_logout")
def customer_logout():
    session.pop('customer', None)
    return redirect(url_for("home"))

# ------------------ Run ------------------
if __name__ == "__main__":
    app.run(debug=True)
