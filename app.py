from flask import Flask, render_template, redirect, request, send_from_directory
from data import db_session
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from forms.user import RegisterForm
from forms.user import LoginForm
from data.recipes import Recipe
from data.users import User
from data.relations import Relation

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bmk8c9ug@)@)o+32--lsa+3mgc+(zn*wgzhsp3e7u$a6x+c35&'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/food.db'
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init("db/food.db")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/static/<path:filename>")
def send_static(filename):
    return send_from_directory('static', filename)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Password mismatch")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data.lower()).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="There is already such a user")
        elif db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="This Username has been already taken")
        user = User(
            name=form.name.data,
            email=form.email.data.lower(),
        )
        user.set_password(form.password.data)
        db_sess.add(user)

        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Registration', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Wrong login or password",
                               form=form)
    return render_template('login.html', title='Log In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/recipe/<recipe_id>', methods=['GET', 'POST'])
def show_recipe(recipe_id):
    if request.method == 'GET':
        db_sess = db_session.create_session()
        recipe = db_sess.get(Recipe, recipe_id)
        photos = recipe.photos.split(', ')
        steps = recipe.steps.split('+')
        if current_user.is_authenticated:
            rec = db_sess.query(Relation).filter(Relation.recipe_id == recipe_id,
                                                 Relation.user_id == current_user.id).first()
            if rec is None:  # если рецепта такого нет, значит кнопка добавить
                but = 'Добавить в избранное'
            else:
                but = 'Удалить из избранного'
            return render_template('recipe.html', recipe=recipe, photos=photos, steps=steps, k=len(steps), but=but)
        else:
            return render_template('recipe.html', recipe=recipe, photos=photos, steps=steps, k=len(steps))
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        rec = db_sess.query(Relation).filter(Relation.recipe_id == recipe_id,
                                             Relation.user_id == current_user.id).first()
        if rec is None:  # если рецепта такого нет, значит нужно добавить
            rel = Relation(recipe_id=recipe_id, user_id=current_user.id)
            db_sess.add(rel)
        else:
            db_sess.delete(rec)
        db_sess.commit()
        return redirect(f'/recipe/{recipe_id}')


@app.route('/recipes', methods=['GET', 'POST'])
def show_recipes():
    hat = 'Каталог рецептов'
    db_sess = db_session.create_session()
    recipes_all = db_sess.query(Recipe).all()
    categories = set([recipe.category for recipe in recipes_all])

    if request.method == 'GET':
        return render_template("recipes.html", recipes=[], categories=categories, message='', hat=hat)

    elif request.method == 'POST':
        min_time = int(request.form.get('min_time')) if request.form.get('min_time') else 1
        max_time = int(request.form.get('max_time')) if request.form.get('max_time') else 10 ** 3
        cat = set([category for category in categories if request.form.get(category)])
        if len(cat) == 0:
            cat = categories
        recipes = []

        for recipe in recipes_all:
            if recipe.category in cat and min_time <= recipe.time <= max_time:
                recipes.append(recipe)

        if len(recipes) > 0:
            return render_template("recipes.html", recipes=recipes, categories=categories, message='', hat=hat)

        return render_template("recipes.html", recipes=recipes, categories=categories,
                               message='К сожалению, рецепты не найдены', hat=hat)


@app.route('/fav_recipes', methods=['GET', 'POST'])
@login_required
def show_favourite_recipes():
    hat = 'Самые любимые рецепты'
    recipes_fav = current_user.recipes
    categories = set([recipe.category for recipe in recipes_fav])

    if request.method == 'GET':
        return render_template("recipes.html", recipes=recipes_fav, categories=categories, message='', hat=hat)

    elif request.method == 'POST':
        min_time = int(request.form.get('min_time')) if request.form.get('min_time') else 1
        max_time = int(request.form.get('max_time')) if request.form.get('max_time') else 10 ** 3
        cat = set([category for category in categories if request.form.get(category)])
        if len(cat) == 0:
            cat = categories
        recipes = []

        for recipe in recipes_fav:
            if recipe.category in cat and min_time <= recipe.time <= max_time:
                recipes.append(recipe)

        if len(recipes) > 0:
            return render_template("recipes.html", recipes=recipes_fav, categories=categories, message='', hat=hat)

        return render_template("recipes.html", recipes=recipes_fav, categories=categories,
                               message='К сожалению, рецепты не найдены', hat=hat)


# if __name__ == '__main__':
#     app.run()
