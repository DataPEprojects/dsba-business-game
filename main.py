from flask import Flask, jsonify, request, render_template
from engine.parameters import Parameters

app = Flask(__name__)
params = Parameters()

def get_turn_data(num: int):
    return params.get_turn(num)

@app.route("/")
def index():
    return "OK. Try /turn?num=1 or /select"

@app.route("/turn")
def turn():
    num = request.args.get("num", default=1, type=int)
    return jsonify(get_turn_data(num))

@app.route("/countries")
def countries():
    num = request.args.get("num", default=1, type=int)
    data = get_turn_data(num)
    return jsonify(sorted(list(data["countries"].keys())))

@app.route("/products")
def products():
    num = request.args.get("num", default=1, type=int)
    country = request.args.get("country", default=None, type=str)

    data = get_turn_data(num)
    countries_data = data["countries"]

    if country:
        if country not in countries_data:
            return jsonify({"error": f"Unknown country: {country}"}), 400
        return jsonify(sorted(list(countries_data[country]["products"].keys())))

    all_products = set()
    for cdata in countries_data.values():
        all_products.update(cdata["products"].keys())
    return jsonify(sorted(list(all_products)))

@app.route("/country_info")
def country_info():
    num = request.args.get("num", default=1, type=int)
    country = request.args.get("country", default=None, type=str)

    if not country:
        return jsonify({"error": "Missing query param: country"}), 400

    data = get_turn_data(num)
    if country not in data["countries"]:
        return jsonify({"error": f"Unknown country: {country}"}), 400

    return jsonify(data["countries"][country])

@app.route("/select")
def select():
    num = request.args.get("num", default=1, type=int)
    country = request.args.get("country", default="", type=str)
    product = request.args.get("product", default="", type=str)

    data = get_turn_data(num)

    countries_list = sorted(list(data["countries"].keys()))
    products_list = []
    base_demand = None

    if country and country in data["countries"]:
        products_list = sorted(list(data["countries"][country]["products"].keys()))
        if product and product in data["countries"][country]["products"]:
            base_demand = data["countries"][country]["products"][product]["base_demand"]

    return render_template(
        "select.html",
        num=num,
        countries=countries_list,
        country=country,
        products=products_list,
        product=product,
        base_demand=base_demand,
    )

if __name__ == "__main__":
    app.run(port=5000)
