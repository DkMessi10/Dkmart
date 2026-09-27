from flask import Flask, render_template, request, redirect, session
import mysql.connector


app = Flask(__name__)

app.secret_key = "shopmart_secret_key"



db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="dhilipk2006",
    database="shopping_db"
)


cursor = db.cursor()



@app.route("/")
def home():

    return render_template("home.html")




@app.route("/products")
def products():

    search = request.args.get("search")
    category = request.args.get("category")

    if search:

        cursor.execute(
            "SELECT * FROM products WHERE name LIKE %s",
            ("%" + search + "%",)
        )

    elif category:

        cursor.execute(
            "SELECT * FROM products WHERE category=%s",
            (category,)
        )

    else:

        cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    return render_template("products.html", products=products)

@app.route("/product/<int:id>")
def product_details(id):

    cursor.execute("SELECT * FROM products WHERE id=%s", (id,))
    product = cursor.fetchone()

    cursor.execute(
        "SELECT user_name, rating, review, created_at FROM reviews WHERE product_name=%s ORDER BY created_at DESC",
        (product[1],)
    )

    reviews = cursor.fetchall()

    return render_template(
        "product_details.html",
        product=product,
        reviews=reviews
    )
@app.route("/add_review", methods=["POST"])
def add_review():

    product_name = request.form["product_name"]
    user_name = request.form["user_name"]
    rating = request.form["rating"]
    review = request.form["review"]

    cursor.execute(
        """
        INSERT INTO reviews(product_name, user_name, rating, review)
        VALUES(%s, %s, %s, %s)
        """,
        (product_name, user_name, rating, review)
    )

    db.commit()

    return redirect(request.referrer)


@app.route("/register")
def register_page():

    return render_template("register.html")




@app.route("/register", methods=["POST"])
def register():

    fullname = request.form["fullname"]

    email = request.form["email"]

    password = request.form["password"]

    phone = request.form["phone"]


    cursor.execute(
        "INSERT INTO users(fullname,email,password,phone) VALUES(%s,%s,%s,%s)",
        (fullname,email,password,phone)
    )


    db.commit()


    return redirect("/login")






@app.route("/login")
def login_page():

    return render_template("login.html")





@app.route("/login", methods=["POST"])
def login():


    email = request.form["email"]

    password = request.form["password"]



    cursor.execute(
        "SELECT * FROM users WHERE email=%s AND password=%s",
        (email,password)
    )


    user = cursor.fetchone()



    if user:


        session["user"] = user[1]


        return redirect("/products")


    else:


        return "Invalid Email or Password"






@app.route("/cart")
def cart():

    return render_template("cart.html")

@app.route("/wishlist")
def wishlist():
    return render_template("wishlist.html")

@app.route("/categories")
def categories():
    return render_template("categories.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/contact", methods=["POST"])
def contact_form():

    name = request.form["name"]
    email = request.form["email"]
    message = request.form["message"]

    cursor.execute(
        "INSERT INTO contact(name,email,message) VALUES(%s,%s,%s)",
        (name, email, message)
    )

    db.commit()

    return redirect("/contact")






@app.route("/checkout")
def checkout():

    return render_template("checkout.html")






# SAVE ORDER

@app.route("/place_order", methods=["POST"])
def place_order():


    if "user" not in session:

        return redirect("/login")



    product_name = request.form["product_name"]

    price = request.form["price"]


    user_email = session["user"]



    cursor.execute(

        "INSERT INTO orders(user_email,product_name,price) VALUES(%s,%s,%s)",

        (user_email, product_name, price)

    )


    db.commit()



    return redirect("/myorders")








# MY ORDERS PAGE

@app.route("/myorders")
def myorders():


    if "user" not in session:

        return redirect("/login")



    user_email = session["user"]



    cursor.execute(

        "SELECT * FROM orders WHERE user_email=%s",

        (user_email,)

    )


    orders = cursor.fetchall()



    return render_template(
        "myorders.html",
        orders=orders
    )

@app.route("/admin")
def admin():

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM contact")
    total_contacts = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reviews")
    total_reviews = cursor.fetchone()[0]

    return render_template(
        "admin.html",
        total_users=total_users,
        total_products=total_products,
        total_orders=total_orders,
        total_contacts=total_contacts,
        total_reviews=total_reviews
    )



@app.route("/manage_products")
def manage_products():

    cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    return render_template(
        "manage_products.html",
        products=products
    )

@app.route("/manage_orders")
def manage_orders():

    cursor.execute("SELECT * FROM orders ORDER BY order_date DESC")

    orders = cursor.fetchall()

    return render_template(
        "manage_orders.html",
        orders=orders
    )

@app.route("/update_order_status/<int:id>", methods=["POST"])
def update_order_status(id):

    status = request.form["status"]

    cursor.execute(
        "UPDATE orders SET status=%s WHERE id=%s",
        (status, id)
    )

    db.commit()

    return redirect("/manage_orders")

@app.route("/delete_product/<int:id>")
def delete_product(id):

    cursor.execute("DELETE FROM products WHERE id=%s", (id,))
    db.commit()

    return redirect("/manage_products")


@app.route("/edit_product/<int:id>")
def edit_product(id):

    cursor.execute("SELECT * FROM products WHERE id=%s", (id,))
    product = cursor.fetchone()

    return render_template(
        "edit_product.html",
        product=product
    )


@app.route("/update_product/<int:id>", methods=["POST"])
def update_product(id):

    name = request.form["name"]
    price = request.form["price"]
    image = request.form["image"]
    description = request.form["description"]
    category = request.form["category"]

    cursor.execute("""
        UPDATE products
        SET name=%s,
            price=%s,
            image=%s,
            description=%s,
            category=%s
        WHERE id=%s
    """, (name, price, image, description, category, id))

    db.commit()

    return redirect("/manage_products")


@app.route("/add_product")
def add_product():
    return render_template("add_product.html")


@app.route("/save_product", methods=["POST"])
def save_product():

    name = request.form["name"]
    price = request.form["price"]
    image = request.form["image"]
    description = request.form["description"]
    category = request.form["category"]

    cursor.execute("""
        INSERT INTO products(name, price, image, description, category)
        VALUES(%s, %s, %s, %s, %s)
    """, (name, price, image, description, category))

    db.commit()

    return redirect("/manage_products")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")





if __name__ == "__main__":

    app.run(debug=True)
  