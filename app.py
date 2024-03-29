import os
from flask import (
    Flask , flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_foods")
def get_foods():
    foods = list(mongo.db.foods.find())
    return render_template("foods.html", foods=foods)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    foods = list(mongo.db.foods.find({"$text": {"$search": query}}))
    return render_template("foods.html", foods=foods)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }    
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exist in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                existing_user['password'], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(
                        request.form.get("username")))                    
                    return redirect(url_for(
                        "profile", username=session["user"]))
            else:
                #invalid password
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_food", methods=["GET", "POST"])
def add_food():
    if request.method == "POST":
        food = {
            "category_name": request.form.get("category_name"),
            "food_name": request.form.get("food_name"),
            "food_description": request.form.get("food_description"),
            "food_image": request.form.get("food_image"),
            "food_ingredients": request.form.get("food_ingredients"),
            "food_preparation": request.form.get("food_preparation"),
            "created_by": session["user"]
        }
        mongo.db.foods.insert_one(food)
        flash("Recipe Successfully Added")
        return redirect(url_for("get_foods"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_food.html", categories=categories)

@app.route("/edit_food/<food_id>", methods=["GET", "POST"])
def edit_food(food_id):
    
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name"),
            "food_name": request.form.get("food_name"),
            "food_description": request.form.get("food_description"),
            "food_image": request.form.get("food_image"),
            "food_ingredients": request.form.get("food_ingredients"),
            "food_preparation": request.form.get("food_preparation"),
            "created_by": session["user"]
        }
        mongo.db.foods.update({"_id": ObjectId(food_id)}, submit)
        flash("Recipe Successfully Updated")
       
    food = mongo.db.foods.find_one({"_id": ObjectId(food_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_food.html", food=food, categories=categories)


@app.route("/delete_food/<food_id>")
def delete_food(food_id):
    mongo.db.foods.remove({"_id": ObjectId(food_id)})
    flash("Recipe Successfully Deleted")
    return redirect(url_for("get_foods"))


# @app.route("/delete_profile/<users_id>")
# def delete_profile(users_id):
   #  mongo.db.users.remove({"_id": ObjectId(users_id)})
    # flash("Profile Successfully Deleted")
    # return redirect(url_for("get_foods"))



@app.route("/get_categories")
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")            
        }
        mongo.db.categories.insert_one(category)
        flash("New Category Added")
        return redirect(url_for("get_categories"))
    return render_template("add_category.html")


@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name")            
        }
        mongo.db.categories.update({"_id":ObjectId(category_id)}, submit)
        flash("Category Successfully Updated")
        return redirect(url_for("get_categories"))

    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)


@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.categories.remove({"_id": ObjectId(category_id)})
    flash("Category Successfully Deleted ")
    return redirect(url_for("get_categories"))


@app.route("/recipe/<food_id>")
def recipe(food_id):

    """
    Renders the recipe page that the user wants to see through
    the ObjectId.
    """

    food = mongo.db.foods.find_one({"_id": ObjectId(food_id)})
    print(food)
    return render_template("recipe.html", food=food)


@app.route("/products")
def products():    
    return render_template("products.html")


@app.route("/home")
def home():    
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
