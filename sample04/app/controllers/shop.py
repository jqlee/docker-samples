from flask import Flask, Blueprint, request, render_template, redirect, url_for
bp = Blueprint('shop', __name__, subdomain='', url_prefix='/shop')

import uuid
def new_uuid(input = None):
    return uuid.uuid4().hex if input == None else uuid.UUID(input).hex




from models.product import Product

@bp.route('/' , methods=['GET'])
def index():

    products = getProducts()

    return render_template('shop/index.html', products=products)


@bp.route('/add-product' , methods=['POST'])
def add_product():
    id = new_uuid()
    name = request.form.get('name', 'Undefined')
    price = request.form.get('price', 1000)

    product = Product(id, name, price)
    addProduct(product)

    return redirect(url_for('shop.index'))

@bp.route('/del-product/<id>' , methods=['POST'])
def del_product(id):
    delProduct(id)
    return redirect(url_for('shop.index'))




def addProduct(product):
    db = DB()
    db.sets_add('products', product.id)
    db.dict_set('products:'+product.id, product.__dict__)

def getProducts():
    db = DB()
    keys = db.sets_get('products')

    products = []
    for k in keys:
        print(k)
        d = db.dict_get('products:'+k)
        products.append(d)

    return products
    #product_sets = db.sets_get('products')

def delProduct(id):
    if id == None: return False
    db = DB() 
    db.sets_remove('products', id)
    db.item_delete('products:'+id)
    return True

        
from flask import current_app as app
import redis

class DB():
    def __init__(self):
        print('POOL: ', app.POOL)
        self.r = redis.StrictRedis(connection_pool=app.POOL)
    
    def sets_add(self, key, value):
        return self.r.sadd(key, value)
    
    def sets_exists(self, key):
        return self.r.exists(key)
    
    def sets_hasmember(self, key, value):
        return self.r.sismember(key, value)
    
    def sets_get(self, key):
        return self.r.smembers(key)
    
    def sets_remove(self, key, value):
        return self.r.srem(key, value)

    def item_get(self, key):
        return self.r.get(key)

    def item_set(self, key, value):
        return self.r.set(key, value)
 
    def item_delete(self, *key):
        return self.r.delete(*key)
 
    def dict_set(self, key, value):
        return self.r.hmset(key, value)
        
    def dict_get(self, key):
        d = self.r.hgetall(key)
        return d if d != {} else None
