from flask import Flask,render_template, request , redirect , url_for, flash,session
from flask_sqlalchemy import SQLAlchemy
from models import *
from datetime import datetime
from flask_cors import CORS
import re
from api_resources import * 
from flask_restful import *



app = Flask(__name__)
app.config['SECRET_KEY'] = '026f45e44043f2c417198178ffa070f72eee7c11fd58492435b3696f08ffe47b6a1b4471d7a24d8038dd449d98cb7964ab50b6140d49f41a52889d00a8f596b7'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project_db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


CORS(app)
db.init_app(app)
api.init_app(app)
app.app_context().push()
db.create_all()


admin=User.query.filter_by(username='admin').first()
if not admin:
    admin=User(username='admin',password='admin',name='admin',is_admin=True)
    db.session.add(admin)
    db.session.commit()




@app.route('/admin')
def admin():
    if 'user_id' not in session:
        flash('Please login to continue.')
        return redirect(url_for('login'))
    
    user=User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not allowed to view this page.')
        return redirect(url_for('index'))
    return render_template('admin.html',user=user,categories=Category.query.all())





@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Please login to continue.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        username = request.form.get('username')
        name = request.form.get('name')
        password = request.form.get('password')
        current_password = request.form.get('current_password')

        if not username or not password or not current_password:
            flash('Username or password cannot be empty.')
            return redirect(url_for('profile'))

        if not user.check_password(current_password):
            flash('Incorrect password.')
            return redirect(url_for('profile'))

        if User.query.filter_by(username=username).first() and username != user.username:
            flash('User with this username already exists. Please choose another username.')
            return redirect(url_for('profile'))

        user.username = username
        user.name = name
        user.password = password
        db.session.commit()
        flash('Profile updated successfully.')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)


@app.route("/login",methods=["GET",'POST'])
def login():
    print("Routing working fine")
    if request.method=="GET":
        return render_template('login.html')
    print("routing fine for post")
    if request.method=="POST":
        print("Enter in post method")
    username = request.form.get('username')
    password = request.form.get('password')
    if username == '' or password == '':
        flash('Username or password cannot be empty.')
        return redirect(url_for('login'))
    user=User.query.filter_by(username=username).first()
    if not user:
        flash('User does not exist.')
        return redirect(url_for('login'))
    if not user.check_password(password):
        flash('Incorrect password.')
        return redirect(url_for('login'))
    #login successful
    session['user_id']=user.id
    return redirect(url_for('index'))

@app.route("/register", methods=["GET", 'POST'])
def register():
    print("Routing working fine")
    if request.method=="GET":
        return render_template('register.html')
    print("routing fine for post")
    if request.method=="POST":
        print("Enter in post method")
        username = request.form.get('username')
        password= request.form.get('password')
        name = request.form.get('name')

        if not username or not password:
            print("first if conditon true") 
            flash('Username or password cannot be empty.')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            print("Second if condition true")
            flash('User with this username already exists.')
            return redirect(url_for('register'))

        user = User(username=username, password=password, name=name)
        print("line 60")
        db.session.add(user)
        print("line 62")
        try:
            db.session.commit()
            print("commit")
        except:
            print("rollback")
            db.session.rollback()
        flash('User successfully registered.')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id',None)
    flash('Logged out successfuly.')
    return redirect(url_for('login'))


@app.route("/category/add", methods=['GET', 'POST'])
def add_new_category():
    if 'user_id' not in session:
        flash('Please login to continue.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if not user.is_admin:
        flash('You are not allowed to view this page.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name')

        
        existing_category = Category.query.filter_by(name=name, is_deleted=True).first()

        if existing_category:
            # If found, update it to is_deleted=False
            existing_category.is_deleted = False
            db.session.commit()
            flash('Category added successfully')
            return redirect(url_for('admin'))
        elif not name:
            flash('Category name cannot be empty')
        elif len(name) > 50:
            flash('Category name cannot be greater than 50 characters')
        else:
            category = Category(name=name)
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully')
            return redirect(url_for('admin'))

    return render_template('category/add_category.html', user=user)



@app.route("/category/<int:id>/display")
def display_category(id):
    if 'user_id' not in session:
        flash('Please login to continue.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not allowed to view this page.')
        return redirect(url_for('index'))

    
    available_products = Product.query.filter_by(category_id=id, is_deleted=False).all()

    return render_template('category/display_category.html', user=user, category=Category.query.get(id), products=available_products)


@app.route("/product/<int:id>/add", methods=['GET', 'POST'])
def add_product(id):
    if 'user_id' not in session:
        flash('Please login to continue.')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not allowed to view this page.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name')
        

        existing_product = Product.query.filter_by(name=name, is_deleted=True).first()

        if not name:
            flash('Product name cannot be empty')
        elif len(name) > 50:
            flash('Product name cannot be greater than 50 characters')
        elif existing_product:
            # Update the existing product by setting is_deleted to False
            existing_product.is_deleted = False
            db.session.commit()
            flash('Product added successfully')
            return redirect(url_for('display_category', id=id))
              
        else:
            name = request.form.get('name')
            quantity = request.form.get('quantity')
            price = request.form.get('price')
            category_id = request.form.get('category_id') 
            manufacturing_date = request.form.get('manufacturing_date')

            if not price:
                flash('Price cannot be empty.')
                return redirect(url_for('add_product', id=id))

            if not re.match(r'^\d+(\.\d+)?$', price):
                flash('Price must be a number.')
                return redirect(url_for('add_product', id=id))

            price = float(price)

            if not quantity:
                flash('Quantity cannot be empty')
                return redirect(url_for('add_product', id=id))

            if not quantity.isdigit():
                flash('Quantity must be a number.')
                return redirect(url_for('add_product', id=id))

            quantity = int(quantity)

            if not category_id:
                flash('Category cannot be empty.')
                return redirect(url_for('add_product', id=id))

            

            if category_id:
               cat_id = int(id)
               cat = Category.query.get(category_id)
               

            if not cat:
                flash('Category does not exist.')
                return redirect(url_for('add_product', id=id))

            if not manufacturing_date:
                flash('Manufacturing date cannot be empty.')
                return redirect(url_for('add_product', id=id))

            try:
                manufacturing_date = datetime.strptime(manufacturing_date, '%Y-%m-%d')
            except ValueError:
                flash('Invalid manufacturing data')
                return redirect(url_for('add_product', id=id))

            product = Product(name=name, quantity=quantity, price=price, category_id=category_id, manufacturing_date=manufacturing_date)
            db.session.add(product)
            db.session.commit()
            flash('Product added successfully')
            return redirect(url_for('display_category', id=cat.id))
        
    cat_id = int(id)
    cat = Category.query.get(cat_id)
    if not cat:
        flash('Category does not exist.')
        return redirect(url_for('admin'))
    
    return render_template('product/add_product.html', user=User.query.get(session['user_id']), categories=Category.query.all(), catn=cat, currdatetime=datetime.now().strftime("%Y-%m-%d"))
    

@app.route("/product/<int:id>/edit", methods=['GET', 'POST'])
def edit_product(id):
    if 'user_id' not in session:
        flash('Please login to continue.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if not user.is_admin:
        flash('You are not allowed to view this page.')
        return redirect(url_for('index'))

    product = Product.query.get(id)

    if request.method == 'POST':
        

        name = request.form.get('name')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        category_id = request.form.get('category')
        manufacturing_date = request.form.get('manufacturing_date')
        category_id = request.form.get('category_id')

        if not name:
            flash('Product name cannot be empty')
        elif len(name) > 50:
            flash('Product name cannot be greater than 50 characters')
        elif not price:
            flash('Price cannot be empty.')
        elif not re.match(r'^\d+(\.\d+)?$', price):
            flash('Price must be a number.')
        elif float(price) <= 0:  
           flash('Price must be greater than zero.')    
        elif not quantity:
            flash('Quantity cannot be empty')
        elif not quantity.isdigit():
            flash('Quantity must be a number.')
        elif not category_id:
            flash('Category cannot be empty.')
        else:
            category_id = int(category_id)
            category = Category.query.get(category_id)

            if not category:
                flash('Category does not exist.')
            elif not manufacturing_date:
                flash('Manufacturing date cannot be empty.')
            else:
                try:
                    manufacturing_date = datetime.strptime(manufacturing_date, '%Y-%m-%d')
                except ValueError:
                    flash('Invalid manufacturing data')
                else:
                    product.name = name
                    product.quantity = int(quantity)
                    product.price = float(price)
                    product.category_id = category_id
                    product.manufacturing_date = manufacturing_date
                    db.session.commit()
                    flash('Product edited successfully')
                    return redirect(url_for('display_category', id=category.id))
    

    categories = Category.query.all()
    currdatetime = datetime.now().strftime("%Y-%m-%d")
    return render_template('product/edit_product.html', user=user, product=product, categories=categories, currdatetime=currdatetime, manufacturing_date=product.manufacturing_date.strftime("%Y-%m-%d"))
   

@app.route("/product/<int:id>/delete", methods=['GET', 'POST'])
def delete_product(id):
    if 'user_id' not in session:
        flash('Please login to continue.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if not user.is_admin:
        flash('You are not allowed to view this page.')
        return redirect(url_for('index'))

    product = Product.query.get(id)

    if not product:
        flash('Product does not exist.')
        return redirect(url_for('admin'))

    
    category_id = product.category_id

    if request.method == 'POST':
       # Mark a product as deleted

        product.is_deleted = True
        db.session.commit()

        flash('Product deleted successfully.')
        return redirect(url_for('admin'))

    
    return render_template('product/delete_product.html', user=user, product=product, category_id=category_id)


@app.route("/category/<int:id>/edit", methods=['GET', 'POST'])
def edit_category(id):
    if 'user_id' not in session:
        flash('Please login to continue.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if not user.is_admin:
        flash('You are not allowed to view this page.')
        return redirect(url_for('index'))

    category = Category.query.get(id)

    if request.method == 'POST':
        name = request.form.get('name')

        if not name:
            flash('Category name cannot be empty')
            return redirect(url_for('edit_category', id=id))

        if len(name) > 50:
            flash('Category name cannot be greater than 50 characters')
            return redirect(url_for('edit_category', id=id))

        category.name = name
        db.session.commit()
        flash('Category edited successfully.')
        return redirect(url_for('admin'))

    return render_template('category/edit_category.html', user=user, category=category)


@app.route('/category/<int:id>/delete', methods=['GET', 'POST'])
def delete_category(id):
    if 'user_id' not in session:
        flash('Please login to continue.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if not user.is_admin:
        flash('You are not allowed to view this page.')
        return redirect(url_for('index'))

    category = Category.query.get(id)

    if not category:
        flash('Category does not exist.')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        for product in category.products:
            product.is_deleted = True

        category.is_deleted = True
        db.session.commit()
        flash('Category deleted successfully.')
        return redirect(url_for('admin'))

    return render_template('category/delete_category.html', user=user, category=category)

@app.route("/")
def index():
    if 'user_id' not in session:
        flash('Please login to continue.')
        return redirect(url_for('login'))
    user=User.query.get(session['user_id'])
    if user.is_admin:
        return redirect(url_for('admin'))
    basis=request.args.get('basis')
    search=request.args.get('search')
    if not basis or not search:
        return render_template('index.html', user=user,categories=Category.query.all())
    if basis == 'category':
        categories= Category.query.filter(Category.name.ilike('%' + search + '%')).all()
        return render_template('index.html', user=user,categories=categories, search=search,basis=basis)
    if basis == 'name':
        return render_template('index.html' , user=user,categories=Category.query.all(),name=search, search=search,basis=basis)
    if basis == 'price':
        return render_template('index.html' , user=user,categories=Category.query.all(),price=float(search), search=search,basis=basis)
    if basis == 'availability':
        return render_template('index.html' , user=user,categories=Category.query.all(), search=search,basis=basis)
         
    return render_template('index.html',user=user,categories=Category.query.all())   

@app.route('/add_to_cart/<int:product_id>',methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        flash('Please login to continue.')
        return redirect(url_for('login'))
    
    q = request.form.get('quantity')
    if not q or q == " ":
        flash("Quantity cannot be empty.")
        return redirect(url_for('index'))
    if q.isdigit() == False:
        flash("Quantity should be a number.")
        return redirect(url_for('index'))
    q = int(q)
    if q <= 0:
        flash("quantity cannot be zero or less.")
        return redirect(url_for('index'))
    p = Product.query.get(product_id)
    if not p:
        flash("Product does not exist")
        return redirect(url_for('index'))
    if p.quantity < q:
        flash("Quantity should be greater than " + str(p.quantity))
        return redirect(url_for('index'))
    
    ic = Cart.query.filter_by(user_id=session['user_id']).filter_by(product_id=product_id).first()
    if ic:
        if ic.quantity + q > p.quantity:
            flash("Quantity must be greater then" + str(p.q - ic.q))
            return redirect(url_for('index'))
        ic.quantity += q
        db.session.commit()
        flash("Product added successfully.")
        return redirect(url_for('index'))
    ic= Cart(user_id=session['user_id'],product_id=product_id,quantity=q)
    db.session.add(ic)
    db.session.commit()
    flash('Product added to cart successfully.')
    return redirect(url_for('index'))

   
     
@app.route('/cart')
def cart():
    if 'user_id' not in session:
        flash('Please login to continue.')
        return redirect(url_for('login'))
    carts=Cart.query.filter_by(user_id=session['user_id']).all()
    tot = sum([cart.product.price * cart.quantity for cart in carts])
    return render_template("cart.html",user=User.query.get(session['user_id']),carts=carts,tot=tot)

@app.route("/cart/<int:product_id>/delete",methods=['POST'])
def delete_from_cart(product_id):
    if 'user_id' not in session:
        flash('Please login to continue.')
        return redirect(url_for('login'))
    c=Cart.query.filter_by(user_id=session['user_id']).filter_by(product_id=product_id).first()
    if not c:
        flash("Product not in cart")
        return redirect(url_for('cart'))
    db.session.delete(c)
    db.session.commit()
    flash("Product deleted")
    return redirect(url_for('cart'))

@app.route('/cart/order_placement',methods=['POST'])
def order_placement():
    if 'user_id' not in session:
        flash('Please login to continue.')
        return redirect(url_for('login'))
    i = Cart.query.filter_by(user_id=session['user_id']).all()
    if not i:
        flash("Cart is empty.")
        return redirect(url_for('cart'))
    for it in i:
        if it.quantity > it.product.quantity:
            flash("Quantity of " + it.product.name + " should be less than or equal to " + str(it.product.quantity))
            return redirect(url_for("cart"))
        
    payment=Payment(user_id=session['user_id'])
    for it in i:
        payment.amount = 0 
        it.product.quantity -= it.quantity
        date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        o = Order(product_id=it.product_id,quantity=it.quantity,Price=it.product.price,datetime=date,user_id=it.user_id)
        print("o.Price:", o.Price)
        print("o.quantity:", o.quantity)
        db.session.add(o)
        payment.orders.append(o)
        payment.amount += o.Price * o.quantity
        db.session.delete(it)
        db.session.add(payment)
        db.session.commit()
    flash("Order placed successfully.")
    return redirect(url_for("orders"))
    


@app.route('/orders')
def orders():
    if 'user_id' not in session:
           flash('Please login to continue.')
           return redirect(url_for('login'))
    user=User.query.get(session['user_id'])
    payments=Payment.query.filter_by(user_id=session['user_id']).all()
    return render_template('my_orders.html',user=user,payments=payments)



