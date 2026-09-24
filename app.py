
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# =========================
# APP CONFIGURATION
# =========================

app.secret_key = "foodhub-change-this-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///foodhub.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================
# ORDER MODEL
# =========================

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    customer_name = db.Column(
        db.String(100),
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=False
    )

    address = db.Column(
        db.Text,
        nullable=False
    )

    city = db.Column(
        db.String(100),
        nullable=False
    )

    pincode = db.Column(
        db.String(10),
        nullable=False
    )

    items = db.Column(
        db.Text,
        nullable=False
    )

    total_amount = db.Column(
        db.Float,
        nullable=False
    )

    payment_method = db.Column(
        db.String(20),
        nullable=False
    )

    payment_status = db.Column(
        db.String(20),
        default="Pending"
    )

    order_status = db.Column(
        db.String(20),
        default="Pending"
    )


# =========================
# PRODUCT MODEL
# =========================

class Product(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    category = db.Column(
        db.String(50),
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    image = db.Column(
        db.String(500),
        default=""
    )

    stock = db.Column(
        db.Integer,
        default=0
    )

    description = db.Column(
        db.Text,
        default=""
    )


# =========================
# CUSTOMER HOME
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# CHECKOUT PAGE
# =========================

@app.route("/checkout")
def checkout():
    return render_template("checkout.html")


# =========================
# PLACE ORDER
# =========================

@app.route("/place-order", methods=["POST"])
def place_order():

    try:

        data = request.get_json()

        customer_name = data.get("customer_name")
        phone = data.get("phone")
        address = data.get("address")
        city = data.get("city")
        pincode = data.get("pincode")
        items = data.get("items")
        total_amount = data.get("total_amount")
        payment_method = data.get("payment_method")

        # Required fields validation
        if not customer_name or not phone or not address:
            return jsonify({
                "success": False,
                "message": "Please fill all required details."
            }), 400

        if not city:
            city = ""

        if not pincode:
            pincode = ""

        if not items:
            return jsonify({
                "success": False,
                "message": "Your cart is empty."
            }), 400

        if total_amount is None:
            return jsonify({
                "success": False,
                "message": "Total amount is missing."
            }), 400

        if not payment_method:
            payment_method = "COD"

        # Create order
        new_order = Order(
            customer_name=customer_name,
            phone=phone,
            address=address,
            city=city,
            pincode=pincode,
            items=str(items),
            total_amount=float(total_amount),
            payment_method=payment_method,
            payment_status="Pending",
            order_status="Pending"
        )

        db.session.add(new_order)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Order placed successfully!",
            "order_id": new_order.id
        })

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Something went wrong.",
            "error": str(e)
        }), 500


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Temporary admin credentials
        if username == "admin" and password == "foodhub123":

            session["admin_logged_in"] = True

            return redirect(
                url_for("admin")
            )

        return render_template(
            "admin_login.html",
            error="Invalid username or password"
        )

    # If not logged in
    if not session.get("admin_logged_in"):

        return render_template(
            "admin_login.html"
        )

    return render_template(
        "admin.html"
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin/logout")
def admin_logout():

    session.pop(
        "admin_logged_in",
        None
    )

    return redirect(
        url_for("admin")
    )


# =========================================================
# ADMIN ORDERS
# =========================================================

@app.route("/admin/orders")
def admin_orders():

    # Security check
    if not session.get("admin_logged_in"):

        return jsonify({
            "success": False,
            "message": "Unauthorized access."
        }), 401

    orders = Order.query.order_by(
        Order.id.desc()
    ).all()

    order_list = []

    for order in orders:

        order_list.append({

            "id": order.id,

            "customer_name": order.customer_name,

            "phone": order.phone,

            "address": order.address,

            "city": order.city,

            "pincode": order.pincode,

            "items": order.items,

            "total_amount": order.total_amount,

            "payment_method": order.payment_method,

            "payment_status": order.payment_status,

            "order_status": order.order_status

        })

    return jsonify({

        "success": True,

        "orders": order_list

    })


# =========================================================
# UPDATE ORDER STATUS
# =========================================================

@app.route("/admin/update-status", methods=["POST"])
def update_order_status():

    # Security check
    if not session.get("admin_logged_in"):

        return jsonify({
            "success": False,
            "message": "Unauthorized access."
        }), 401

    data = request.get_json()

    order_id = data.get("order_id")

    status = data.get("status")

    if not order_id or not status:

        return jsonify({

            "success": False,

            "message": "Order ID and status are required."

        }), 400

    order = Order.query.get(
        order_id
    )

    if not order:

        return jsonify({

            "success": False,

            "message": "Order not found."

        }), 404

    # Allowed statuses
    allowed_statuses = [

        "Pending",

        "Confirmed",

        "Preparing",

        "Dispatched",

        "Delivered",

        "Cancelled"

    ]

    if status not in allowed_statuses:

        return jsonify({

            "success": False,

            "message": "Invalid order status."

        }), 400

    order.order_status = status

    db.session.commit()

    return jsonify({

        "success": True,

        "message": "Order status updated."

    })


# =========================================================
# ADMIN - GET PRODUCTS
# =========================================================

@app.route("/admin/products")
def admin_products():

    # Security check
    if not session.get("admin_logged_in"):

        return jsonify({

            "success": False,

            "message": "Unauthorized access."

        }), 401

    products = Product.query.order_by(
        Product.id.desc()
    ).all()

    product_list = []

    for product in products:

        product_list.append({

            "id": product.id,

            "name": product.name,

            "category": product.category,

            "price": product.price,

            "image": product.image,

            "stock": product.stock,

            "description": product.description

        })

    return jsonify({

        "success": True,

        "products": product_list

    })


# =========================================================
# ADMIN - ADD PRODUCT
# =========================================================

@app.route("/admin/products/add", methods=["POST"])
def add_product():

    # Security check
    if not session.get("admin_logged_in"):

        return jsonify({

            "success": False,

            "message": "Unauthorized access."

        }), 401

    data = request.get_json()

    name = data.get("name")
    category = data.get("category")
    price = data.get("price")
    image = data.get("image", "")
    stock = data.get("stock", 0)
    description = data.get(
        "description",
        ""
    )

    # Validation
    if not name or not category or price is None:

        return jsonify({

            "success": False,

            "message": "Name, category and price are required."

        }), 400

    try:

        price = float(price)

        stock = int(stock)

    except ValueError:

        return jsonify({

            "success": False,

            "message": "Price and stock must be valid numbers."

        }), 400

    new_product = Product(

        name=name,

        category=category,

        price=price,

        image=image,

        stock=stock,

        description=description

    )

    db.session.add(
        new_product
    )

    db.session.commit()

    return jsonify({

        "success": True,

        "message": "Product added successfully!",

        "product_id": new_product.id

    })


# =========================================================
# ADMIN - UPDATE PRODUCT
# =========================================================

@app.route("/admin/products/update", methods=["POST"])
def update_product():

    # Security check
    if not session.get("admin_logged_in"):

        return jsonify({

            "success": False,

            "message": "Unauthorized access."

        }), 401

    data = request.get_json()

    product_id = data.get("id")

    if not product_id:

        return jsonify({

            "success": False,

            "message": "Product ID is required."

        }), 400

    product = Product.query.get(
        product_id
    )

    if not product:

        return jsonify({

            "success": False,

            "message": "Product not found."

        }), 404

    # Update only supplied values

    if data.get("name") is not None:

        product.name = data.get(
            "name"
        )

    if data.get("category") is not None:

        product.category = data.get(
            "category"
        )

    if data.get("price") is not None:

        product.price = float(
            data.get("price")
        )

    if data.get("image") is not None:

        product.image = data.get(
            "image"
        )

    if data.get("stock") is not None:

        product.stock = int(
            data.get("stock")
        )

    if data.get("description") is not None:

        product.description = data.get(
            "description"
        )

    db.session.commit()

    return jsonify({

        "success": True,

        "message": "Product updated successfully."

    })


# =========================================================
# ADMIN - DELETE PRODUCT
# =========================================================

@app.route("/admin/products/delete", methods=["POST"])
def delete_product():

    # Security check
    if not session.get("admin_logged_in"):

        return jsonify({

            "success": False,

            "message": "Unauthorized access."

        }), 401

    data = request.get_json()

    product_id = data.get("id")

    if not product_id:

        return jsonify({

            "success": False,

            "message": "Product ID is required."

        }), 400

    product = Product.query.get(
        product_id
    )

    if not product:

        return jsonify({

            "success": False,

            "message": "Product not found."

        }), 404

    db.session.delete(
        product
    )

    db.session.commit()

    return jsonify({

        "success": True,

        "message": "Product deleted successfully."

    })


# =========================================================
# DATABASE CREATION
# =========================================================

with app.app_context():

    db.create_all()


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
