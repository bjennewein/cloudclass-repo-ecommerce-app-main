from flask import Blueprint, request, jsonify, render_template

from flask_login import login_required

from app.models import db, Product

products = Blueprint("products", __name__)

@products.route("/shop", methods=["GET"])
def product_listing():
    product_list = [
        {
            "name": "Wireless Headphones",
            "description": "Comfortable Bluetooth headphones with clear sound.",
            "price": 79.99,
            "image": "headphones.jpg"
        },
        {
            "name": "Smart Watch",
            "description": "A lightweight watch for tracking activity and notifications.",
            "price": 129.99,
            "image": "smart-watch.jpg"
        },
        {
            "name": "Portable Speaker",
            "description": "A compact wireless speaker with rich sound.",
            "price": 49.99,
            "image": "speaker.jpg"
        }
    ]

    return render_template("products.html", products=product_list)

@products.route("/products", methods=["GET"])
def get_products():
    all_products = Product.query.all()

    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "stock": p.stock,
            "image_url": p.image_url,
            "status": "Low stock" if p.stock <= 5 else "In stock"
        }
        for p in all_products
    ])

@products.route("/products", methods=["POST"])
@login_required
def create_product():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    product = Product(
        name=data["name"],
        description=data.get("description"),
        price=data["price"],
        stock=data.get("stock", 0),
        image_url=data.get("image_url")
    )

    db.session.add(product)
    db.session.commit()

    return jsonify({"message": "Product created"}), 201

@products.route("/products/<int:id>", methods=["PUT"])
@login_required
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.get_json()

    for key, value in data.items():
        setattr(product, key, value)

    db.session.commit()
    return jsonify({"message": "Product updated"})

@products.route("/products/<int:id>", methods=["DELETE"])
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()

    return jsonify({"message": "Product deleted"})