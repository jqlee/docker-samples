from flask import Flask, Blueprint

app = Flask(__name__)

import demo
app.register_blueprint(demo.bp)


@app.route('/')
def hello_world():
    return 'Hello world'


from flask import jsonify
@app.route('/json')
def json():
    obj = {
        'name': 'Docker',
        'version': 13.12
    }
    return jsonify(obj)


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
