import csv
import os
import sys

from app import db, Product, Review


def csv_to_db(file_path):
    """Write csv to db"""
    with open(file_path, mode='r', newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if os.path.basename(file_path) == "products.csv":
                product = Product(
                    title=row['Title'],
                    asin=row['Asin']
                )
                db.session.add(product)
                db.session.commit()
            elif os.path.basename(file_path) == "reviews.csv":
                review = Review(
                    title=row['Title'],
                    review=row['Review'],
                    product_asin=row['Asin']
                )
                db.session.add(review)
                db.session.commit()


if __name__ == '__main__':
    for arg in sys.argv[1:]:
        csv_to_db(arg)
