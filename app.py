from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
from datetime import date

app = Flask(__name__)
app.secret_key = "super secret key"

database = mysql.connector.connect(user='root', password='sql123',
                                 host='127.0.0.1',
                                 database='petHotelDB',
                                   )

cursor = database.cursor()

print(database.is_connected())


@app.route('/')
def main_page():
    return render_template('main_page.html')

@app.route('/logged_out')
def logged_out_page():
    session.pop("password", None)
    session.pop("email", None)
    session.clear()
    return render_template('logged_out.html')

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

@app.route("/lincontact")
def contactlogged_page():

    return render_template('contact_r.html')

@app.route('/accommodation')
def accomodation_page():
    return render_template('accommodation.html')

@app.route("/linaccommodation")
def accomodationlogged_page():
    return render_template('accommodation_r.html')

count_night = {}

@app.route('/reservation', methods=["GET","POST"])
def reservation_page():

    if request.method == "GET":
        #print("getteyiz")
        return render_template("reservation.html")

    else:
        #print("posttayiz")
        check_in_date = request.form["check_in_date"]
        check_out_date = request.form["check_out_date"]
        number_of_rooms = request.form["number_of_rooms"]
        number_of_pets = request.form["number_of_pets"]
        room_selection = request.form['room_selection']


        d0 = date(int(check_in_date.split('-')[0]), int(check_in_date.split('-')[1]), int(check_in_date.split('-')[2]))
        d1 = date(int(check_out_date.split('-')[0]), int(check_out_date.split('-')[1]), int(check_out_date.split('-')[2]))
        count_nights = d1 - d0


        if room_selection == 'Zen':
            amount_zen = count_nights*20
            count_night[room_selection] = str(amount_zen).split(',')[0].split(' ')[0]
        if room_selection == 'Royal':
            amount_royal = count_nights*35
            count_night[room_selection] = str(amount_royal).split(',')[0].split(' ')[0]
        if room_selection == 'Presidential':
            amount = count_nights*60
            count_night[room_selection] = str(amount).split(',')[0].split(' ')[0]


        return redirect(url_for('my_reservations_page',check_in_date=check_in_date, check_out_date=check_out_date,
                                number_of_rooms=number_of_rooms,number_of_pets=number_of_pets, room_selection=room_selection, count_night=count_night))



available_rooms = {'Zen': 100, 'Royal': 100, 'Presidential': 100}


@app.route('/myreservations', methods=["GET","POST"])
def my_reservations_page():


    if request.method == "GET":
        print("getteyiz")
        check_in_date = request.args.get('check_in_date', None)
        check_out_date = request.args.get('check_out_date', None)
        number_of_rooms = request.args.get('number_of_rooms', None)
        number_of_pets = request.args.get('number_of_pets', None)
        room_selection = request.args.get('room_selection', None)

        cursor.execute("select count(check_out_date) from reservation where check_out_date < NOW() and room_type=%s",
                       [room_selection])
        room_update = cursor.fetchall()[0][0]
        available_rooms[room_selection] += room_update

        return render_template('my_reservations.html', check_in_date=check_in_date, check_out_date=check_out_date,
                           number_of_rooms=number_of_rooms, number_of_pets=number_of_pets, room_selection=room_selection,available_rooms=available_rooms,
                               count_night=count_night)

    else:
        print("posttayiz")
        check_in_date = request.form['check_in_date']
        check_out_date = request.form['check_out_date']
        room_type = request.form['room_type']
        number_of_rooms = request.form['number_of_rooms']
        number_of_pets = request.form['number_of_pets']
        hotel_name = 'Biscuits and Bath'
        customer_ID = session['customer_ID']


        check = True
        
        if available_rooms[room_type] == 0:
            check = False

        if check == True:


            cursor.execute("insert into reservation(check_in_date, check_out_date, room_type, hotel_hotel_name, customer_customer_ID)"
                               " values(%s,%s,%s,%s,%s);", (check_in_date, check_out_date, room_type, hotel_name, customer_ID))
            database.commit()

            cursor.execute("select reservation_ID from reservation")

            reservation_ID = cursor.fetchall()[-1][0]


            cursor.execute("insert into room(room_type, reservation_reservation_ID, reservation_hotel_hotel_name)"
                               " values(%s,%s,%s);", (room_type, reservation_ID, hotel_name))
            database.commit()


            available_rooms[room_type] -= 1

            cursor.execute("insert into bill(bill_date, amount, customer_customer_ID)"
                           " values(%s,%s,%s);", (str(date.today()),count_night[room_type], customer_ID))
            database.commit()

            cursor.execute("insert into pets(number_of_pets, customer_customer_ID)"
                           " values(%s,%s);", (number_of_pets, customer_ID))
            database.commit()


        return redirect('/reservation')


@app.route('/login/', methods=["GET","POST"])
def login_page():
    if request.method == "GET":
        return render_template('login.html')
    else:
        email = request.form["email"]
        password = request.form["password"]
        check = False

        cursor.execute("select * from customer")
        customers = cursor.fetchall()

        for customer in customers:
            if customer[2] == email and customer[3] == password:
                customer_ID = customer[0]
                check = True

        if check == True:
            session["email"] = email
            session["customer_ID"] = customer_ID
            return redirect('/reservation')
        else:
            return redirect("/login/")


@app.route('/signup', methods=["GET","POST"])
def signup_page():
    if request.method == "GET":
        print("getteyiz")
        return render_template("signup.html")

    else:
        print("posttayiz")
        customer_name = request.form["customer_name"]
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute("select * from customer")
        customers = cursor.fetchall()

        check = True
        for customer in customers:
            if customer[2] == email:
                check = False

        if check == True:
            cursor.execute("insert into customer(customer_name, email, password)"
                           " values(%s,%s,%s);",(customer_name,email,password))
            database.commit()
        else:
            return redirect("/signup")
        return redirect("/login/")

@app.route("/home_page")
def home_page():
    return render_template("home_page.html")

if __name__ == '__main__':
    app.debug = True
    app.run()
