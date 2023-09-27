from flask_restful import Api, Resource, reqparse
from models import *
from datetime import datetime
from flask import *

api = Api()

parser = reqparse.RequestParser()
parser.add_argument('c_name')

class Api_category(Resource):
    def get(self):
        all_category = {}
        c1 = Category.query.filter_by(is_deleted=False).all()
        for category in c1:
            all_category[category.id] = category.name
        return all_category
    # category update
    def put(self, id):
        info = parser.parse_args()
        print(info)
        c_update = Category.query.filter_by(id=id, is_deleted=False).first()
        if c_update:
            c_update.name = info['c_name']
            db.session.commit()
            return {"category_name": info['c_name'], "status": "updated"}, 201
        else:
            return {"status": "Category does not exist"}, 404
    # category deleted
    def delete(self, id):
        c_delete = Category.query.get(id)
        c_delete.is_deleted = True
        db.session.commit()
        return {"status": "deleted"}, 202
    #category create
    
    def post(self):
        info = parser.parse_args()
        c_name = info['c_name']

        if not c_name:
            return {"error": "Category name is required"}, 400

        existing_category = Category.query.filter_by(name=c_name).first()

        if existing_category:
            
            if existing_category.is_deleted:
                existing_category.is_deleted = False
                db.session.commit()
                return {"category_name": c_name, "status": "created"}, 200
            else:
                
                return {"error": "Category already exists"}, 400
        else:
            
            new_category = Category(name=c_name, is_deleted=False)
            db.session.add(new_category)
            db.session.commit()
            return {"category_name": c_name, "status": "created"}, 201


class Api_products(Resource):
    
    def get(self):
           
        products_info = []

        
        products = Product.query.filter_by(is_deleted=False).all()

       
        for product in products:
            product_info = {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'quantity': product.quantity,
                'manufacturing_date': product.manufacturing_date.strftime("%Y-%m-%d"),
                'category_id': product.category_id
            }
            products_info.append(product_info)

        return products_info, 200
    

    #create product

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('product_name')  
        parser.add_argument('price')
        parser.add_argument('quantity')
        parser.add_argument('manufacturing_date')
        parser.add_argument('category_id')


        info = parser.parse_args()
        product_name = info['product_name']
        price = info['price']
        quantity = info['quantity']
        manufacturing_date = info['manufacturing_date']
        category_id = info['category_id']

        if not product_name or not price or not quantity or not manufacturing_date or not category_id:
            return {"error": "All fields are required"}, 400

        try:
            price = float(price)
            quantity = int(quantity)
            manufacturing_date = datetime.strptime(manufacturing_date, '%Y-%m-%d')
        except ValueError:
            return {"error": "Invalid data format"}, 400

        category = Category.query.get(category_id)
        if not category:
            return {"error": "Category does not exist"}, 400

        new_product = Product(
            name=product_name,
            price=price,
            quantity=quantity,
            manufacturing_date=manufacturing_date,
            category_id=category_id,
        )
        db.session.add(new_product)
        db.session.commit()

        return {"product_name": product_name, "status": "created"}, 201
    
    #update product
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('product_name')  
        parser.add_argument('price')
        parser.add_argument('quantity')
        parser.add_argument('manufacturing_date')
        parser.add_argument('category_id')

        info = parser.parse_args()
        product_name = info.get('product_name')
        price = info.get('price')
        quantity = info.get('quantity')
        manufacturing_date = info.get('manufacturing_date')
        category_id = info.get('category_id')

        if not product_name or not price or not quantity or not manufacturing_date or not category_id:
            return {"error": "All fields are required"}, 400

        try:
            price = float(price)
            quantity = int(quantity)
            manufacturing_date = datetime.strptime(manufacturing_date, '%Y-%m-%d')
        except ValueError:
            return {"error": "Invalid data format"}, 400

        category = Category.query.get(category_id)
        if not category:
            return {"error": "Category does not exist"}, 400

        product = Product.query.get(id)
        if not product:
            return {"error": "Product does not exist"}, 404

        product.name = product_name
        product.price = price
        product.quantity = quantity
        product.manufacturing_date = manufacturing_date
        product.category_id = category_id
        db.session.commit()

        return {"product_name": product_name, "status": "updated"}, 200

    #delete
    def delete(self, id):
        product = Product.query.get(id)
        if not product:
            return {"error": "Product does not exist"}, 404
        
        db.session.delete(product)
        db.session.commit()
        return {"status": "deleted"}, 204

# Add the new routes for creating, updating, and deleting products
api.add_resource(Api_category, "/api/all_category", "/api/all_category/<int:id>")
api.add_resource(Api_products, "/api/products", "/api/products/<int:id>")
