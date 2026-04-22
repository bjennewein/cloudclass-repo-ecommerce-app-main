from flask import Flask

app = Flask(__name__)

products = [
    {"name": "Notebook", "price": 5.99, "stock": 12},
    {"name": "Water Bottle", "price": 14.99, "stock": 8},
    {"name": "Backpack", "price": 29.99, "stock": 4}
]

@app.route('/')
def home():
    html = """
    <h1>Welcome to My Ecommerce App</h1>
    <p><strong>Spring Sale:</strong> 20% off select items!</p>
    <h2>Products</h2>
    <ul>
    """
    for product in products:
        html += f"<li>{product['name']} - ${product['price']} (Stock: {product['stock']})</li>"
    html += "</ul>"
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)