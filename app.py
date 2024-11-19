from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import csv
from flask import Response

app = Flask(__name__)

# 配置數據庫
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定義數據庫模型
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    message = db.Column(db.Text, nullable=False)

# 初始化數據庫
with app.app_context():
    db.create_all()

# 首頁
@app.route('/')
def home():
    return render_template('index.html')

# 顯示客戶資料
@app.route('/customers')
def customers():
    all_customers = Customer.query.all()
    return render_template('customers.html', customers=all_customers)

# 新增客戶資料
@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # 保存到數據庫
        new_customer = Customer(name=name, email=email, message=message)
        db.session.add(new_customer)
        db.session.commit()

        return redirect(url_for('customers'))
    return render_template('form.html')

# 編輯客戶資料
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    if request.method == 'POST':
        # 更新數據
        customer.name = request.form['name']
        customer.email = request.form['email']
        customer.message = request.form['message']
        db.session.commit()
        return redirect('/customers')
    return render_template('edit.html', customer=customer)

# 刪除客戶資料
@app.route('/delete/<int:id>', methods=['POST'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return redirect('/customers')


@app.route('/export')
def export():
    customers = Customer.query.all()

    # 建立 CSV 文件
    output = []
    output.append(['ID', 'Name', 'Email', 'Message'])
    for customer in customers:
        output.append([customer.id, customer.name, customer.email, customer.message])

    # 將資料轉換為 CSV
    si = "\n".join([",".join(map(str, row)) for row in output])
    response = Response(si, mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=customers.csv'
    return response

if __name__ == '__main__':
    app.run(debug=True)
