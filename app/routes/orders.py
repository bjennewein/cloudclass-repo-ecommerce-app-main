from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.models import db, Order, Product

orders = Blueprint("orders", __name__)


@orders.route("/orders", methods=["GET"])
def order_list():
    all_orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("orders.html", orders=all_orders)


@orders.route("/orders/new/<int:product_id>", methods=["GET", "POST"])
def create_order(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip()
        customer_email = request.form.get("customer_email", "").strip()
        quantity_text = request.form.get("quantity", "1").strip()

        try:
            quantity = int(quantity_text)
        except ValueError:
            quantity = 0

        if not customer_name or not customer_email:
            current_app.logger.warning(
                "Order validation failed for product_id=%s: missing name or email",
                product.id,
            )
            flash("Please enter your name and email address.")
            return render_template("new_order.html", product=product)

        if "@" not in customer_email or "." not in customer_email.split("@")[-1]:
            current_app.logger.warning(
                "Order validation failed for product_id=%s: invalid email",
                product.id,
            )
            flash("Please enter a valid email address.")
            return render_template("new_order.html", product=product)

        if quantity < 1:
            current_app.logger.warning(
                "Order validation failed for product_id=%s: invalid quantity=%s",
                product.id,
                quantity_text,
            )
            flash("Quantity must be at least 1.")
            return render_template("new_order.html", product=product)

        if quantity > product.stock:
            current_app.logger.warning(
                (
                    "Order validation failed for product_id=%s: "
                    "requested=%s available=%s"
                ),
                product.id,
                quantity,
                product.stock,
            )
            flash(
                f"Only {product.stock} unit(s) of {product.name} are available."
            )
            return render_template("new_order.html", product=product)

        order = Order(
            customer_name=customer_name,
            customer_email=customer_email,
            product_id=product.id,
            quantity=quantity,
            status="Pending",
        )

        product.stock -= quantity

        try:
            db.session.add(order)
            db.session.commit()

            current_app.logger.info(
                (
                    "New order created | order_id=%s | product=%s | "
                    "quantity=%s | customer=%s"
                ),
                order.id,
                product.name,
                quantity,
                customer_email,
            )

        except Exception:
            db.session.rollback()

            current_app.logger.exception(
                "Order creation failed for product_id=%s",
                product.id,
            )

            flash("The order could not be completed. Please try again.")
            return render_template("new_order.html", product=product)

        return redirect(
            url_for("orders.order_confirmation", order_id=order.id)
        )

    return render_template("new_order.html", product=product)


@orders.route("/orders/<int:order_id>/confirmation", methods=["GET"])
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template("order_confirmation.html", order=order)


@orders.route("/orders/<int:order_id>/status", methods=["POST"])
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)

    allowed_statuses = {
        "Pending",
        "Processing",
        "Shipped",
        "Completed",
        "Cancelled",
    }

    new_status = request.form.get("status")

    if new_status in allowed_statuses:
        old_status = order.status
        order.status = new_status
        db.session.commit()

        current_app.logger.info(
            "Order status updated | order_id=%s | %s -> %s",
            order.id,
            old_status,
            new_status,
        )
    else:
        current_app.logger.warning(
            "Invalid order status attempted | order_id=%s | status=%s",
            order.id,
            new_status,
        )

        flash("That order status is not valid.")

    return redirect(url_for("orders.order_list"))