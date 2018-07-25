from flask import Flask, Blueprint, request, render_template
bp = Blueprint('shop', __name__, subdomain='', url_prefix='/shop')



from models.product import Product

@bp.route('/' , methods=['GET'])
def index():

    products = []

    products.append(Product('日語五十音入門班'))
    products.append(Product('N2綜合實力養成班', 6000))
    products.append(Product('韓語入門班', 4599))
    products.append(Product('英文會話班Level E', 5800))
    products.append(Product('日語閱讀理解實力養成班', 6500))


    return render_template('shop/index.html', products=products)


