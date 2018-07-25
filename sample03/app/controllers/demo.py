from flask import Flask, Blueprint, request, render_template
bp = Blueprint('demo', __name__, subdomain='', url_prefix='/demo')

@bp.route('/' , methods=['GET'])
def index():
    return render_template('demo/index.html')