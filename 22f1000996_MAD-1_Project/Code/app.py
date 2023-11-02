import os
import re
from sqlalchemy import or_  

from flask import Flask , render_template , request , flash , redirect , url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager , login_user , logout_user , current_user , login_required , UserMixin
from flask_restful import Resource , Api
from werkzeug.sansio.response import Response
from werkzeug.security import generate_password_hash , check_password_hash
import datetime
import json
from flask_cors import CORS
current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+os.path.join(current_dir,"Grocery_db.sqlite3")

db = SQLAlchemy()
db.init_app(app)
api = Api(app)
app.app_context().push()
CORS(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


class User(db.Model , UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer , primary_key = True)
    email = db.Column(db.String , nullable = False , unique = True)
    password = db.Column(db.String , nullable = False)
    active = db.Column(db.Integer)
    fname = db.Column(db.String)
    lname = db.Column(db.String)
    contact = db.Column(db.Integer)
    role_id = db.Column(db.Integer , db.ForeignKey("role.id") , nullable = False)

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer , primary_key = True)
    name = db.Column(db.String , nullable = False)
    description = db.Column(db.String , nullable = False)



class Category(db.Model):
    __tablename__ = 'Category'
    Cat_id = db.Column(db.Integer , primary_key = True)
    Cat_name = db.Column(db.String , nullable = False , unique = True)
    is_Deleted = db.Column(db.Integer , nullable = False)
    image_link = db.Column(db.String)

class Inventory(db.Model):
    __tablename__ = 'Inventory'
    Prod_id = db.Column(db.Integer , primary_key = True)
    Prod_name = db.Column(db.String , nullable = False)
    Prod_price_rs = db.Column(db.Integer , nullable = False)
    Price_per = db.Column(db.String , nullable = False)
    Cat_id = db.Column(db.Integer , db.ForeignKey("Category.Cat_id") , nullable = False)
    Quantity = db.Column(db.Integer)
    is_Deleted = db.Column(db.Integer , nullable = False)
    Expiry_date = db.Column(db.String)
    is_Expired = db.Column(db.Integer)
    product_image = db.Column(db.String)



class Cart(db.Model):
    __tablename__ = 'Cart'
    Cart_id = db.Column(db.Integer , primary_key = True)
    user_id = db.Column(db.String , db.ForeignKey("user.id") , nullable = False)
    Total = db.Column(db.Integer , nullable = False)
    Status = db.Column(db.Integer , nullable = False)
    Buy_date = db.Column(db.String)

class Cart_details(db.Model):
    __tablename__ = 'Cart_details'
    __table_args__ = (db.PrimaryKeyConstraint('Cart_id', 'Prod_id') , )
    Cart_id = db.Column(db.Integer , db.ForeignKey("Cart.Cart_id") , nullable = False)
    Prod_id = db.Column(db.Integer , db.ForeignKey("Inventory.Prod_id") , nullable = False)
    Quantity = db.Column(db.Integer , nullable = False)
    Prod_total = db.Column(db.Integer , nullable = False)





@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))



@app.route("/user/login" , methods = ["GET" , "POST"])
def user_login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        
        existing_user = User.query.filter_by(email = email , role_id = 1).first()
        if not existing_user:
            flash('Invalid Login Please Retry')
            return render_template("user_login.html")
        
        if not check_password_hash(existing_user.password , password):
            flash('Incorrect Password')
            return render_template("user_login.html")
        
        login_user(existing_user)

        return redirect(url_for('user_dash'))

    return render_template("user_login.html")



@app.route("/manager/login" , methods = ["GET" , "POST"])
def manager_login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        
        existing_user = User.query.filter_by(email = email , role_id = 2).first()
        if not existing_user:
            flash('Invalid Login Please Retry')
            return render_template("manager_login.html")
        
        if not check_password_hash(existing_user.password , password):
            flash('Incorrect Password')
            return render_template("manager_login.html")
        
        login_user(existing_user )

        return redirect(url_for('manager_dash'))

    return render_template("manager_login.html")



@app.route("/signup" , methods = ["GET" , "POST"])
def register():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        contact = request.form.get('contact')
        confirm_password = request.form.get('password_confirm')
        if not re.match(r".+@.+\..+",email):
            flash('Invalid email id')
            return render_template("signup.html")
        
        if int(contact) < 1000000000 or int(contact) > 9999999999 :
            flash('Contact Must Be Exactly 10 digits')
            return render_template("signup.html")
        
        if re.search(r'\s' , password) or re.search(r'\s' , confirm_password):
            flash('Passwords Cannot Contain Spaces')
            return render_template("signup.html")
        
        existing = User.query.filter_by(email = email).first()
        if existing:
            flash('User Already Exists')
            return render_template("signup.html")
        
        if confirm_password != password :
            flash('Password And Confirm Password Do Not Match')
            return render_template("signup.html")
        
        
        new_user = User(email = email , password = generate_password_hash(password , method = 'scrypt') , fname = fname , lname = lname , contact = contact , role_id = 1)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('home'))
    
    return render_template("signup.html")



@app.route("/log_out" , methods = ["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))



@app.route("/" , methods = ["GET"])
def home():
    return render_template("homepage.html")



@app.route("/manager/dashboard" , methods = ["GET" , "POST"])
@login_required
def manager_dash():
    category_list = {}
    image_list = {}
    products = Inventory.query.filter(Inventory.is_Deleted == 0).all()
    for product in products:
        expiry_date = None
        category = Category.query.filter(Category.Cat_id == product.Cat_id).first()
        if category.Cat_name not in category_list:
            category_list[category.Cat_name] = []
        item_dic = {}
        item_dic['prod_id'] = product.Prod_id
        item_dic['prod_name'] = product.Prod_name
        item_dic['price'] = product.Prod_price_rs
        item_dic['per'] = product.Price_per
        item_dic['image'] = product.product_image
        if category.Cat_name not in image_list.keys():
            image_list[category.Cat_name] = category.image_link
        if product.Expiry_date and datetime.datetime.strptime(product.Expiry_date , '%Y-%m-%d').date() <= datetime.date.today():
            product.Quantity = 0
            product.is_Expired = 1
            db.session.commit()
            item_dic['expiry_date'] = 'Expired!! Please Restock Fresh and Update the Expiry Date'
        else:
            if not product.Expiry_date:
                product.is_Expired = 0
                db.session.commit()
            item_dic['expiry_date'] = product.Expiry_date
        item_dic['quantity'] = product.Quantity
        category_list[category.Cat_name].append(item_dic)
    empty_cat = Category.query.filter(Category.is_Deleted == 0).all()
    for cat in empty_cat:
        if cat.Cat_name not in category_list:
            category_list[cat.Cat_name] = []
        if category.Cat_name not in image_list.keys():
            image_list[category.Cat_name].append(category.image_link)
    return render_template("manager_dashboard.html" , category_list = category_list , image_list = image_list)



@app.route("/manager/add_category" , methods = ["GET" , "POST"])
def add_category():
    if request.method == "POST":
        Cat_name = request.form.get('Category_name')
        existing = Category.query.filter(Category.Cat_name.ilike(f'%{Cat_name}%')).first()
        if existing and existing.is_Deleted == 0:
            flash('Category already exists')
            return render_template("add_category.html" , flag = 1)
        if existing and existing.is_Deleted == 1:
            existing.is_Deleted = 0
            db.session.commit()
            return redirect(url_for('manager_dash'))
        category = Category(Cat_name = Cat_name , is_Deleted = 0)
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('manager_dash'))
    return render_template("add_category.html" , flag = 0)



@app.route("/manager/<string:category>/add_product" , methods = ["GET" , "POST"])
def add_product(category):
    if request.method == "POST":
        Prod_name = request.form["product_name"]
        Prod_price_rs = request.form["price" ]
        Price_per = request.form["price_unit"]
        Quantity = request.form["quantity"]
        date = request.form["expiryDate"]
        Cat_id = (Category.query.filter_by(Cat_name = category).first()).Cat_id
        existing_prod = Inventory.query.filter_by(Cat_id = Cat_id , Prod_name = Prod_name , is_Deleted = 0).first()
        if existing_prod:
            flash('Existing Product')
            return render_template("add_product.html" , category = category)
        if date and datetime.datetime.strptime(date , '%Y-%m-%d').date() < datetime.date.today():
            flash('Expiry Date Has to be after today')
            return render_template("add_product.html" , category = category)
        new_prod = Inventory(Prod_name = Prod_name , Prod_price_rs = Prod_price_rs , Price_per = Price_per , Quantity = Quantity , Cat_id = Cat_id , is_Deleted = 0 , Expiry_date = date , is_Expired = 0)
        db.session.add(new_prod)
        db.session.commit()
        return redirect(url_for("manager_dash"))
    return render_template("add_product.html" , category = category)



@app.route("/manager/<int:prod_id>/restock" , methods = ["GET" , "POST"])
def restock(prod_id):
    if request.method == "POST":
        product = Inventory.query.filter_by(Prod_id = prod_id).first()
        quantity = int(request.form.get('quantity'))
        product.Quantity+=quantity
        db.session.commit()
        return redirect(url_for('manager_dash'))
    return redirect(url_for('manager_dash'))


@app.route("/manager/<int:prod_id>/edit_product" , methods = ["GET" , "POST"])
def edit_product(prod_id):
    product = Inventory.query.filter_by(Prod_id = prod_id).first()
    if request.method == "POST":
        prod_name = request.form.get('product_name')
        prod_price = request.form.get('price')
        prod_quantity = request.form.get('quantity')
        prod_price_unit = request.form.get('price_unit')
        date = request.form.get('expiryDate')

        existing = Inventory.query.filter( Inventory.Cat_id == product.Cat_id ,Inventory.Prod_name.ilike(prod_name) , Inventory.is_Deleted == 0).first()
        if existing and existing.Prod_name != product.Prod_name:
            flash('This Product already exists')
            return render_template("edit_product.html" , prod = product)
        product.Prod_name = prod_name
        product.Prod_price_rs = prod_price
        product.Price_per = prod_price_unit
        product.Quantity = prod_quantity
        if date and datetime.datetime.strptime(date , '%Y-%m-%d').date() < datetime.date.today():
            flash('Expiry Date Has to be after today')
            return render_template("edit_product.html" , prod = product)
        product.Expiry_date = date
        product.is_Expired = 0
        db.session.commit()
        return redirect(url_for('manager_dash'))
    return render_template("edit_product.html" , prod = product)



@app.route("/manager/<string:category>/update" , methods = ["Get" , "POST"])
def edit_category(category):
    cat = Category.query.filter_by(Cat_name = category).first()
    if not cat:
        return redirect(url_for('manager_dash'))
    if request.method == "POST":
        new_cat_name = request.form.get('Category_name')
        existing = Category.query.filter(Category.Cat_name.ilike(new_cat_name)).first()
        if existing and existing.Cat_name != cat.Cat_name:
            flash('Category with this name already exists')
            return render_template('edit_category.html' , category = category)
        cat.Cat_name = new_cat_name
        db.session.commit()
        return redirect(url_for('manager_dash'))
    return render_template('edit_category.html' , category = category)
    




@app.route("/manager/<int:prod_id>/delete" , methods = ["GET" , "POST"])
def del_prod(prod_id):
    if request.method == "POST":
        carts = Cart.query.filter_by(Status = 1).all()
        if carts:
            for cart in carts:
                cart_product = Cart_details.query.filter_by(Cart_id = cart.Cart_id , Prod_id = prod_id).first()
                if cart_product:
                    cart.Total -= cart_product.Prod_total
                    db.session.delete(cart_product)
        
        product = Inventory.query.filter_by(Prod_id = prod_id).first()
        product.is_Deleted = 1
        db.session.commit()
        return redirect(url_for("manager_dash"))
    
    return redirect(url_for('manager_dash'))



@app.route("/manager/<string:category>/delete" , methods = ["GET" , "POST"])
def del_cat(category):
    if request.method == "POST":
        del_category = Category.query.filter_by(Cat_name = category).first()
        del_products = Inventory.query.filter_by(Cat_id = del_category.Cat_id).all()
        all_id = []
        for p in del_products:
            all_id.append(p.Prod_id)
            p.is_Deleted = 1
        active_carts = Cart.query.filter_by(Status = 1).all()
        if active_carts:
            for cart in active_carts:
                cart_details = Cart_details.query.filter_by(Cart_id = cart.Cart_id).all()
                for item in cart_details:
                    if item.Prod_id in all_id:
                        cart.Total -= item.Prod_total
                        db.session.delete(item)
        del_category.is_Deleted = 1
        db.session.commit()
        return redirect(url_for('manager_dash'))
    return redirect(url_for('manager_dash'))
        

@app.route("/user/dashboard" , methods = ["GET" , "POST"])
@login_required
def user_dash():
    category_list = {}
    image_list = {}
    results = db.session.query(Category.Cat_name , Inventory.Prod_id , Inventory.Prod_name , Inventory.Prod_price_rs , Inventory.Price_per , Inventory.Quantity , Inventory.is_Deleted , Category.image_link , Inventory.product_image).outerjoin(Inventory , Category.Cat_id == Inventory.Cat_id).filter(Category.is_Deleted == 0 , or_(Inventory.is_Deleted == 0 , Inventory.is_Deleted == 1) , Inventory.is_Expired == 0).all()
    for item in results:
        if item[0] not in category_list.keys():
            category_list[item[0]] = []
        if item[6]!=1:
            item_dic = {}
            item_dic['prod_id'] = item[1]
            item_dic['prod_name'] = item[2]
            item_dic['price'] = item[3]
            item_dic['per'] = item[4]
            item_dic['quantity'] = item[5]
            item_dic['image'] = item[8]
            category_list[item[0]].append(item_dic)
        if item[0] not in image_list.keys():
            image_list[item[0]] = item[7]


    return render_template("user_dashboard.html" , category_list = category_list , image_list = image_list)



@app.route("/user/<int:prod_id>/checkout" , methods = ["GET" , "POST"])
def checkout(prod_id ):
    my_cart = {}
    prod = Inventory.query.filter_by(Prod_id = prod_id).first()
    category = Category.query.filter_by(Cat_id = prod.Cat_id).first()
    if request.method == "POST":
        quantity = float(request.form.get('quantity'))
        prod_total = prod.Prod_price_rs * quantity
        db.session.commit()

        if request.form.get('button') == 'addtocart':
            existing_cart = Cart.query.filter_by(user_id = current_user.id , Status = 1).first()
            if existing_cart:
                existing_product = Cart_details.query.filter_by(Cart_id = existing_cart.Cart_id , Prod_id = prod_id).first()
                if existing_product:
                    if int(quantity) + int(existing_product.Quantity) > prod.Quantity:
                        flash('The asked quantity is not available in stock !! Maximum Quantity already in Cart')
                        return redirect(url_for('user_dash'))
                    existing_product.Quantity+=quantity
                    existing_product.Prod_total += prod_total
                else:
                    new_addition = Cart_details(Cart_id = existing_cart.Cart_id , Prod_id = prod_id , Quantity = quantity , Prod_total = prod_total)
                    db.session.add(new_addition)
                db.session.commit()
                existing_cart.Total+=prod_total
                db.session.commit()
                return redirect(url_for('user_dash'))
            new_cart = Cart(user_id = current_user.id , Total = prod_total , Status = 1)
            db.session.add(new_cart)
            db.session.commit()
            new_cart_addition = Cart_details(Cart_id = new_cart.Cart_id , Prod_id = prod_id , Quantity = quantity , Prod_total = prod_total)
            db.session.add(new_cart_addition)
            db.session.commit()
            return redirect(url_for('user_dash'))
        
        elif request.form.get('button') == "buy":
            new_cart = Cart(user_id = current_user.id , Total = prod_total , Status = 1)
            db.session.add(new_cart)
            db.session.commit()

            new_cart_details = Cart_details(Cart_id = new_cart.Cart_id , Prod_id = prod_id , Quantity = quantity , Prod_total = prod_total)
            db.session.add(new_cart_details)
            db.session.commit()

            prod_list = []
            prod_dic = {}
            prod_dic['prod_id'] = prod_id
            prod_dic['prod_name'] = prod.Prod_name
            prod_dic['category'] = category.Cat_name
            prod_dic['quantity'] = quantity
            prod_dic['price'] = prod_total
            prod_dic['max_quantity'] = prod.Quantity
            prod_dic['rate'] = prod.Prod_price_rs
            prod_dic['unit'] = prod.Price_per
            prod_dic['image'] = prod.product_image
            prod_list.append(prod_dic)

            my_cart['cart_id'] = new_cart.Cart_id
            my_cart['products'] = prod_list
            my_cart['total'] = new_cart.Total
            my_cart['Buy'] = 1

            return render_template("checkout.html" , my_cart = my_cart)
    return render_template("checkout.html" , my_cart = my_cart)



@app.route("/user/<int:cart_id>/proceed_to_buy" , methods = ["GET" , "POST"])
def proceed_to_buy(cart_id):
    if request.method == "POST":
        cart = Cart.query.filter_by(Cart_id = cart_id).first()
        cart_details = Cart_details.query.filter_by(Cart_id = cart_id).all()
        for item in cart_details:
            product = Inventory.query.filter_by(Prod_id = item.Prod_id).first()
            product.Quantity-=item.Quantity
        cart.Status = 0
        cart.Buy_date = datetime.date.today()
        db.session.commit()
        return render_template("Thanks.html")
    return render_template("Thanks.html")



@app.route("/user/viewcart" , methods = ["GET" , "POST"])
def viewcart():
    my_cart = {}
    cart = Cart.query.filter_by(user_id = current_user.id , Status = 1).first()
    if cart:
        my_cart['cart_id'] = cart.Cart_id
        cart_details = Cart_details.query.filter_by(Cart_id = cart.Cart_id).all()
        prod_list = []
        for product in cart_details:
            prod_dic = {}
            all_prod = db.session.query(Inventory.Prod_id , Inventory.Prod_name , Category.Cat_name , Inventory.Quantity , Inventory.Prod_price_rs , Inventory.Price_per , Inventory.is_Expired , Inventory.product_image).outerjoin(Inventory , Category.Cat_id == Inventory.Cat_id ).filter(Inventory.Prod_id == product.Prod_id , Category.is_Deleted == 0 , or_(Inventory.is_Deleted == 0 , Inventory.is_Deleted == 1)).first()
            if all_prod[6] == 1:
                cart.Total -= product.Prod_total
                db.session.delete(product)
                db.session.commit()
            else:
                prod_dic['prod_id'] = all_prod[0]
                prod_dic['prod_name'] = all_prod[1]
                prod_dic['category'] = all_prod[2]
                prod_dic['quantity'] = product.Quantity
                prod_dic['price'] = product.Prod_total
                prod_dic['max_quantity'] = all_prod[3]
                prod_dic['rate'] = all_prod[4]
                prod_dic['unit'] = all_prod[5]
                prod_dic['image'] = all_prod[7]

                prod_list.append(prod_dic)
        my_cart['products'] = prod_list
        my_cart['total'] = cart.Total
        my_cart['Buy'] = 0
        if my_cart['total'] == 0:
            db.session.delete(cart)
            db.session.commit()
            return render_template("checkout.html" , my_cart = {})
        return render_template("checkout.html" , my_cart = my_cart)
    
    return render_template("checkout.html" , my_cart = my_cart)



@app.route("/user/<int:cart_id>/back_without_buying")
def back_without_buying(cart_id):
    cart = Cart.query.filter_by(Cart_id = cart_id).first()
    cart_details = Cart_details.query.filter_by(Cart_id = cart_id).all()
    
    for item in cart_details:
        # product = Inventory.query.filter_by(Prod_id = item.Prod_id).first()
        # product.Quantity+=item.Quantity
        db.session.delete(item)
    db.session.delete(cart)
    db.session.commit()

    return redirect(url_for('user_dash'))



@app.route("/user/<int:cart_id>/<int:prod_id>/remove_from_cart" , methods = ["GET" , "POST"])
def remove_from_cart(cart_id , prod_id):
    if request.method == "POST":
        cart_details = Cart_details.query.filter_by(Cart_id = cart_id , Prod_id = prod_id).first()
        cart = Cart.query.filter_by(Cart_id = cart_id).first()
        product = Inventory.query.filter_by(Prod_id = prod_id).first()
        if request.form.get('remove'):
            # product.Quantity += cart_details.Quantity
            cart.Total -= cart_details.Prod_total
            db.session.delete(cart_details)
            db.session.commit()
            return redirect(url_for('viewcart'))
    return redirect(url_for('viewcart'))



@app.route("/user/<int:cart_id>/<int:prod_id>/change_quantity" , methods = ["GET" , "POST"])
def change_quantity(cart_id , prod_id):
    if request.method == "POST":
        cart_details = Cart_details.query.filter_by(Cart_id = cart_id , Prod_id = prod_id).first()
        cart = Cart.query.filter_by(Cart_id = cart_id).first()
        product = Inventory.query.filter_by(Prod_id = prod_id).first()

        if request.form.get('quantity_button') == 'decrease':
            cart.Total -= product.Prod_price_rs
            # product.Quantity+=1
            cart_details.Quantity-=1
            cart_details.Prod_total -= product.Prod_price_rs
            db.session.commit()
            if cart_details.Quantity == 0:
                db.session.delete(cart_details)
                db.session.commit()
                return redirect(url_for('viewcart'))
            return redirect(url_for('viewcart'))
        
        if request.form.get('quantity_button') == 'increase':
            cart.Total += product.Prod_price_rs
            # product.Quantity-=1
            cart_details.Quantity+=1
            cart_details.Prod_total += product.Prod_price_rs
            db.session.commit()
            return redirect(url_for('viewcart'))
        
        return redirect(url_for('viewcart'))
    return redirect(url_for('viewcart'))
    


@app.route("/user/search" , methods = ["GET" , "POST"])
def user_search():
    if request.method == "POST":
        search = request.form.get('search')
        
        category_list = {}
        image_list = {}
        search_results = db.session.query(Category.Cat_name , Inventory.Prod_id , Inventory.Prod_name , Inventory.Prod_price_rs , Inventory.Price_per , Inventory.Quantity , Inventory.product_image , Category.image_link).outerjoin(Inventory , Category.Cat_id == Inventory.Cat_id).filter( or_(Category.Cat_name.ilike(f'%{search}%') , Inventory.Prod_name.ilike(f'%{search}%') , db.cast(Inventory.Prod_price_rs, db.String).like(f'{search}') , db.cast(Inventory.Price_per, db.String).ilike(f'%{search}%') ) , Category.is_Deleted == 0 , Inventory.is_Deleted == 0).all()
        if not search_results:
            flash('Not Found')
            return redirect(url_for('user_dash'))
        for item in search_results:
            if item[0] not in category_list.keys() :
                category_list[item[0]] = []
            item_dic = {}
            item_dic['prod_id'] = item[1]
            item_dic['prod_name'] = item[2]
            item_dic['price'] = item[3]
            item_dic['per'] = item[4]
            item_dic['quantity'] = item[5]
            item_dic['image'] = item[6]
            if item[0] not in image_list.keys():
                image_list[item[0]] = item[7]

            category_list[item[0]].append(item_dic)

        return render_template("user_dashboard.html" , category_list = category_list , image_list = image_list)
    
    return redirect(url_for('user_dash'))



@app.route("/manager/search" , methods = ["GET" , "POST"])
def manager_search():
    if request.method == "POST":
        search = request.form.get('search')
        category_list = {}
        image_list = {}
        search_results = db.session.query(Category.Cat_name , Inventory.Prod_id , Inventory.Prod_name , Inventory.Prod_price_rs , Inventory.Price_per , Inventory.Quantity , Inventory.product_image , Category.image_link).outerjoin(Inventory , Category.Cat_id == Inventory.Cat_id).filter( or_(Category.Cat_name.ilike(f'%{search}%') , Inventory.Prod_name.ilike(f'%{search}%') , db.cast(Inventory.Prod_price_rs, db.String).ilike(f'%{search}%') , db.cast(Inventory.Price_per, db.String).ilike(f'%{search}%') ) , Category.is_Deleted == 0 , Inventory.is_Deleted == 0).all()
        if not search_results:
            flash('Not Found')
            return redirect(url_for('manager_dash'))
        for item in search_results:
            if item[0] not in category_list.keys() :
                category_list[item[0]] = []
            if item[0] not in image_list.keys():
                image_list[item[0]] = item[7]
            item_dic = {}
            item_dic['prod_id'] = item[1]
            item_dic['prod_name'] = item[2]
            item_dic['price'] = item[3]
            item_dic['per'] = item[4]
            item_dic['quantity'] = item[5]
            item_dic['image'] = item[6]
            category_list[item[0]].append(item_dic)

        return render_template("manager_dashboard.html" , category_list = category_list , image_list = image_list)
    
    return redirect(url_for('manager_dash'))



@app.route("/user/profile" , methods = ["GET" , "POST"])
def profile():
    user_carts = {}
    dates = {}
    all_carts = Cart.query.filter_by(user_id = current_user.id).all()
    for cart in all_carts:
        cart_details = Cart_details.query.filter_by(Cart_id = cart.Cart_id).all()
        prod_list = []
        prod_list.append(cart.Total)
        for product in cart_details:
            prod_dic = {}
            all_prod = db.session.query(Inventory.Prod_id , Inventory.Prod_name , Category.Cat_name , Inventory.Prod_price_rs , Inventory.Price_per , Inventory.product_image).outerjoin(Inventory , Category.Cat_id == Inventory.Cat_id ).filter(Inventory.Prod_id == product.Prod_id).first()
            prod_dic['prod_id'] = all_prod[0]
            prod_dic['prod_name'] = all_prod[1]
            prod_dic['category'] = all_prod[2]
            prod_dic['prod_price'] = all_prod[3]
            prod_dic['unit'] = all_prod[4]
            prod_dic['quantity'] = product.Quantity
            prod_dic['prod_total'] = product.Prod_total
            prod_dic['image'] = all_prod[5]
            prod_list.append(prod_dic)
        user_carts[cart.Cart_id] = prod_list
        if cart.Cart_id not in dates.keys():
            dates[cart.Cart_id] = cart.Buy_date
    return render_template("profile.html" , user_carts = user_carts , dates = dates)



from flask_restful import Resource , fields , marshal_with , reqparse
from flask import make_response
from werkzeug.exceptions import HTTPException


class Error(HTTPException):
    def __init__(self , status_code , description):
        message = {"error message" : description}
        self.response = make_response(json.dumps(message) , status_code)

class Success(HTTPException):
    def __init__(self, status_code , description):
        message = {"success message" : description}
        self.response = make_response(json.dumps(message) , status_code)

cat_output = {
    'Cat_id' : fields.Integer ,
    'Cat_name' : fields.String
}

create_category_parser = reqparse.RequestParser()
create_category_parser.add_argument('Category_name' , type=str , required = True)

update_category_parser = reqparse.RequestParser()
update_category_parser.add_argument("Category_name")


class Category_CRUD(Resource):
    @marshal_with(cat_output)
    def get(self , category):
        cat = Category.query.filter(Category.Cat_name.ilike(f'%{category}%')).first()
        if cat:
            return cat
        else:
            raise Error(status_code = 404 , description = 'Category Not Found')

    def post(self):
        args = create_category_parser.parse_args()
        cat_name = args['Category_name']
        existing = Category.query.filter(Category.Cat_name.ilike(f'%{cat_name}%')).first()
        if existing and existing.is_Deleted == 0:
            raise Error(status_code = 400 , description = 'Category Already Exists')
        if existing and existing.is_Deleted == 1: 
            existing.is_Deleted = 0
            db.session.commit()
            raise Success(status_code=201 , description='Category added successfully')
        category = Category(Cat_name = cat_name , is_Deleted = 0)
        db.session.add(category)
        db.session.commit()
        raise Success(status_code=201 , description='Category added successfully')

    def put(self , category):
        cat = Category.query.filter(Category.Cat_name.ilike(f'%{category}%')).first()
        if not cat:
            raise Error(status_code = 404 , description = 'Category Not Found')
        args = update_category_parser.parse_args()
        new_cat_name= args["Category_name"]
        existing = Category.query.filter(Category.Cat_name.ilike(new_cat_name)).first()
        if existing and existing.Cat_name != cat.Cat_name:
            raise Error(status_code=400 , description='Category Already Exists')
        cat.Cat_name = new_cat_name
        db.session.commit()
        return "Category Updated Successfully" , 201

    def delete(self , category):
        del_category = Category.query.filter(Category.Cat_name.ilike(f'%{category}%')).first()
        if not del_category or del_category.is_Deleted == 1:
            raise Error(status_code = 404 , description = 'Category Not Found')
        del_products = Inventory.query.filter_by(Cat_id = del_category.Cat_id).all()
        all_id = []
        if del_products:
            for p in del_products:
                all_id.append(p.Prod_id)
                p.is_Deleted = 1
        active_carts = Cart.query.filter_by(Status = 1).all()
        if active_carts:
            for cart in active_carts:
                cart_details = Cart_details.query.filter_by(Cart_id = cart.Cart_id).all()
                for item in cart_details:
                    if item.Prod_id in all_id:
                        cart.Total -= item.Prod_total
                        db.session.delete(item)
        del_category.is_Deleted = 1
        db.session.commit()
        return "Category Deleted Successfully" , 201

api.add_resource(Category_CRUD , '/api/manager/category/add' , '/api/manager/category/<string:category>')


prod_output = {
    'Prod_id' : fields.Integer ,
    'Prod_name' : fields.String,
    'Prod_price_rs':fields.Integer,
    'Price_per': fields.String,
    'Quantity':fields.Integer,
    'is_Expired':fields.Integer,
    'Cat_name':fields.String
}

create_product_parser = reqparse.RequestParser()
create_product_parser.add_argument('Prod_name', type=str , required = True)
create_product_parser.add_argument('Prod_price_rs',type=int , required = True)
create_product_parser.add_argument('Price_per',type= str , required = True)
create_product_parser.add_argument('Quantity',type= int ,required =True )
create_product_parser.add_argument('Expiry_date',type=str)
create_product_parser.add_argument('Cat_name',type=str , required = True)

update_product_parser = reqparse.RequestParser()
update_product_parser.add_argument("Prod_name",type=str , required = True)
update_product_parser.add_argument ("Prod_price_rs",type=int , required = True)
update_product_parser.add_argument ('Price_per',type=str , required =True)
update_product_parser.add_argument('Quantity',type=int , required = True)
update_product_parser.add_argument('Expiry_date',type=str)


class Product_CRUD(Resource):
    @marshal_with(prod_output)
    def get(self , prod_id):
        prod = db.session.query(Category.Cat_name , Inventory.Prod_id , Inventory.Prod_name , Inventory.Prod_price_rs , Inventory.Price_per , Inventory.Quantity , Inventory.is_Expired).outerjoin(Inventory , Category.Cat_id == Inventory.Cat_id).filter(Inventory.Prod_id == prod_id , Category.is_Deleted == 0 , Inventory.is_Expired == 0 , Inventory.is_Deleted == 0).first()
        if prod:
            return prod
        else:
            raise Error(status_code = 404 , description = 'Product Not Found')
        
    def post(self):
        args = create_product_parser.parse_args()
        Prod_name = args['Prod_name']
        Prod_price_rs  = args['Prod_price_rs']
        Price_per = args["Price_per"]
        Quantity  = args["Quantity"]
        date    = args["Expiry_date"]
        category = args['Cat_name']
        Cat = (Category.query.filter(Category.Cat_name.ilike(f'%{category}%')).first())
        if not Cat:
            raise Error(status_code=404 , description='Category Not Found')
        Cat_id = Cat.Cat_id
        existing_prod = Inventory.query.filter_by(Cat_id = Cat_id , Prod_name = Prod_name , is_Deleted = 0).first()
        if existing_prod:
            raise Error(status_code=400 , description='Product Already Exists')
        if date and datetime.datetime.strptime(date , '%Y-%m-%d').date() < datetime.date.today():
            raise Error(status_code=422 , description='Expiry Date Should be after today')
        new_prod = Inventory(Prod_name = Prod_name , Prod_price_rs = Prod_price_rs , Price_per = Price_per , Quantity = Quantity , Cat_id = Cat_id , is_Deleted = 0 , Expiry_date = date , is_Expired = 0)
        db.session.add(new_prod)
        db.session.commit()
        raise Success(status_code=201 , description='Product Added Successfully')
    
    def put(self , prod_id):
        product = Inventory.query.filter_by(Prod_id = prod_id).first()
        if not product:
            raise Error(status_code=400 , description='Product Not Found')
        
        args = update_product_parser.parse_args()
        prod_name = args['Prod_name']
        prod_price = args['Prod_price_rs']
        prod_price_unit = args['Price_per']
        prod_quantity = args["Quantity"]
        date = args["Expiry_date"]

        existing = Inventory.query.filter( Inventory.Cat_id == product.Cat_id ,Inventory.Prod_name.ilike(prod_name) , Inventory.is_Deleted == 0).first()
        if existing and existing.Prod_name != product.Prod_name:
            raise Error(status_code=400 , description='Product Already Exists')
        product.Prod_name = prod_name
        product.Prod_price_rs = prod_price
        product.Price_per = prod_price_unit
        product.Quantity = prod_quantity
        if date and datetime.datetime.strptime(date , '%Y-%m-%d').date() < datetime.date.today():
            raise Error(status_code=422 , description='Expiry Date Should be after today')
        product.Expiry_date = date
        product.is_Expired = 0
        db.session.commit()
        raise Success(status_code=201 , description='Product Updated Successfully')

    def delete(self , prod_id):
        product = Inventory.query.filter_by(Prod_id = prod_id).first()
        if not product:
            raise Error(status_code=400 , description='Product Not Found')
        carts = Cart.query.filter_by(Status = 1).all()
        if carts:
            for cart in carts:
                cart_product = Cart_details.query.filter_by(Cart_id = cart.Cart_id , Prod_id = prod_id).first()
                if cart_product:
                    cart.Total -= cart_product.Prod_total
                    db.session.delete(cart_product)
        product.is_Deleted = 1
        db.session.commit()
        raise Success(status_code=201 , description='Product Deleted Successfully')

api.add_resource(Product_CRUD , '/api/manager/product/add' , '/api/manager/product/<int:prod_id>')

if __name__ == '__main__':
	app.run()