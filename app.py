from flask import Flask, jsonify, abort, make_response, request
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:123@127.0.0.1:5432/gns'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['POSTS_PER_PAGE'] = 5

cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

db = SQLAlchemy(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), unique=True, nullable=False)
    asin = db.Column(db.String(), unique=True, nullable=False)
    reviews = db.relationship('Review', backref='product', lazy=True)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), unique=True, nullable=False)
    review = db.Column(db.String(), unique=True, nullable=False)
    product_asin = db.Column(db.String(), db.ForeignKey('product.asin'),
                             nullable=False)


def get_pagination(items):
    pagination = []
    for item in items:
        pagination.append({"Title": item.title, "Review": item.review})
    return pagination


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.route('/product/<int:product_id>/<int:page>', methods=['GET'])
@cache.cached(timeout=50)
def product_info(product_id, page):
    product = Product.query.filter_by(id=product_id).first()
    review = Review.query.filter_by(product_asin=product.asin).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    return jsonify({
        "Asin": product.asin,
        "Title": product.title,
        "Reviews": get_pagination(review.items),
    })


@app.route('/product/<int:product_id>', methods=['PUT'])
def review_update(product_id):
    product = Product.query.get(product_id)
    review = Review(
        title=request.form['title'],
        review=request.form['review'],
        product_asin=product.asin
    )
    db.session.add(review)
    db.session.commit()

    if product:
        return jsonify({
            "Title": review.title,
            "Asin": review.product_asin,
            "Review": review.review
        })
    abort(400)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
