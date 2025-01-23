import os
from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

uri = os.getenv("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)



class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    day = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "total": str(self.total), "day": self.day, "month": self.month}

# Routes
@app.route('/')
def index():
    if 'loggedin' in session:
        items = Item.query.order_by(Item.id.desc()).limit(10).all()
        return render_template('crud.html', items=items)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['loggedin'] = True
            session['username'] = user.username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')  # Use flash messages for feedback
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        total = request.form['total']
        day = int(request.form['day'])
        month = int(request.form['month'])
        new_item = Item(name=name, total=total, day=day, month=month)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_item.html')

@app.route('/edit_item/<int:id>', methods=['GET', 'POST'])
def edit_item(id):
    item = Item.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.total = request.form['total']
        item.day = int(request.form['day'])
        item.month = int(request.form['month'])
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_item.html', item=item)

@app.route('/delete_item/<int:id>')
def delete_item(id):
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/bulk_clone', methods=['POST'])
def bulk_clone():
    ids = request.form.getlist('item_ids')
    for id in ids:
        original_item = Item.query.get(id)
        if original_item:
            cloned_item = Item(name=original_item.name, total=original_item.total, day=original_item.day, month=original_item.month)
            db.session.add(cloned_item)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/bulk_delete', methods=['POST'])
def bulk_delete():
    ids = request.form.getlist('item_ids')
    for id in ids:
        item = Item.query.get(id)
        if item:
            db.session.delete(item)
    db.session.commit()
    return redirect(url_for('index'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
