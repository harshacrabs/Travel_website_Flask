from flask import Flask, request, render_template, redirect, flash, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'krishna24'

# Function to establish a connection to the database


def create_conn():
    conn = sqlite3.connect('users.db')
    return conn


# create a database and table if they don't exist
conn = create_conn()
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username text, email text, password text)''')
conn.commit()
conn.close()


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/chart', methods=['GET'])
def chart():
    return render_template('charts.html')


@app.route('/packages', methods=['GET'])
def packages():
    return render_template('packages.html')


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@app.route('/payment', methods=['GET'])
def payment():
    return render_template('payment.html')




@app.route('/account', methods=['GET', 'POST'])
def account():
    if request.method == 'GET':
        return render_template('account.html')

    elif request.method == 'POST':
        conn = None
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']

            # Open the database connection
            conn = create_conn()
            c = conn.cursor()

            # insert the user data into the table
            c.execute("INSERT INTO users(username, email, password) VALUES (?, ?, ?)",
                      (username, email, password))
            conn.commit()
            flash("Record successfully added to database")

        except:
            if conn:
                conn.rollback()
            flash("Error in the Insert")

        finally:
            # Close the database connection
            if conn:
                conn.close()

            return render_template('booking.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # connect to the database and retrieve user info with matching email
        conn = create_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cur.fetchone()
        conn.close()

        # if the user is found, check the password
        if user:
            if user[2] == password:
                return redirect(url_for('booking'))

            else:
                flash('Password incorrect')
        else:
            flash('Email does not exist')

    return render_template('login.html')


@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'GET':
        return render_template('booking.html')
    if request.method == 'POST':
        origin = request.form['from_location']
        destination = request.form['to_location']
        travel_date_from = request.form['from_date']
        travel_date_to = request.form['to_date']
        num_travelers = request.form['num_travellers']
        promo_code = request.form['promo_code']

        import sqlite3
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    origin TEXT,
                    destination TEXT,
                    travel_date_from TEXT,
                    travel_date_to TEXT,
                    num_travelers INTEGER,
                    promo_code TEXT
                )
            """)

            cursor.execute("""
                INSERT INTO bookings (origin, destination, travel_date_from, travel_date_to, num_travelers, promo_code)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (origin, destination, travel_date_from, travel_date_to, num_travelers, promo_code))

            booking_id = cursor.lastrowid
            conn.commit()

        booking = {
            'origin': origin,
            'destination': destination,
            'travel_date_from': travel_date_from,
            'travel_date_to': travel_date_to,
            'num_travelers': num_travelers,
            'promo_code': promo_code,
        }

        return redirect(url_for('mybooking', booking_id=booking_id))


# create a database and table if they don't exist
conn = create_conn()
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username text, email text, password text)''')
c.execute('''CREATE TABLE IF NOT EXISTS prices
             (origin text, destination text, cost real)''')
conn.commit()


sample_data = [
    ('US', 'India', 1200),
    ('US', 'Pakistan', 1300),
    ('US', 'France', 1000),
    ('US', 'Italy', 1500),
    ('US', 'UK', 1100),
    ('India', 'Pakistan', 800),
    ('India', 'France', 1400),
    ('India', 'Italy', 1600),
    ('India', 'UK', 1700),
    ('Pakistan', 'France', 1800),
    ('Pakistan', 'Italy', 1900),
    ('Pakistan', 'UK', 2000),
    ('France', 'Italy', 900),
    ('France', 'UK', 950),
    ('Italy', 'UK', 1000),
]
c.executemany(
    "INSERT OR IGNORE INTO prices (origin, destination, cost) VALUES (?, ?, ?)", sample_data)
conn.commit()
conn.close()


@app.route('/mybooking', methods=['GET', 'POST'])
def mybooking():
    if request.method == 'POST':
        booking_id = request.form['booking_id']
        origin = request.form['from_location']
        destination = request.form['to_location']
        travel_date_from = request.form['from_date']
        travel_date_to = request.form['to_date']
        num_travelers = request.form['num_travellers']
        promo_code = request.form['promo_code']

        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE bookings
                SET origin = ?, destination = ?, travel_date_from = ?, travel_date_to = ?, num_travelers = ?, promo_code = ?
                WHERE id = ?
            """, (origin, destination, travel_date_from, travel_date_to, num_travelers, promo_code, booking_id))

            conn.commit()

            cursor.execute(
                "SELECT cost FROM prices WHERE origin=? AND destination=?", (origin, destination))
            cost_per_person = cursor.fetchone()[0]
            total_cost = cost_per_person * num_travelers
            tax_percentage = 20
            tax = tax_percentage / 100
            total_cost_including_tax = total_cost * (1 + tax)

            flash('Booking updated successfully')

            return render_template('payment.html', cost_per_person=cost_per_person, total_cost=total_cost, tax_percentage=tax_percentage, tax=tax, total_cost_including_tax=total_cost_including_tax)
           

    booking_id = request.args.get('booking_id', None)
    if booking_id:
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bookings WHERE id=?", (booking_id,))
            booking = cursor.fetchone()

        if booking:
            booking = {
                'id': booking[0],
                'origin': booking[1],
                'destination': booking[2],
                'travel_date_from': booking[3],
                'travel_date_to': booking[4],
                'num_travelers': booking[5],
                'promo_code': booking[6],
            }

            cursor.execute(
                "SELECT cost FROM prices WHERE origin=? AND destination=?", (booking['origin'], booking['destination']))
            cost_per_person = cursor.fetchone()[0]
            total_cost = cost_per_person * booking['num_travelers']
            tax = 0.2
            total_cost_including_tax = total_cost * (1 + tax)

            return render_template('payment.html', cost_per_person=cost_per_person, total_cost=total_cost, tax=tax, total_cost_including_tax=total_cost_including_tax)

        else:
            flash('Booking not found')
            return render_template('booking.html')
    else:
        return redirect(url_for('payment'))


if __name__ == '__main__':
    app.run(debug=True)
