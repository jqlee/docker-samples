from flask import Flask, Blueprint

app = Flask(__name__, template_folder='views')

# import demo
# app.register_blueprint(demo.bp)

@app.route('/')
def hello_world():
    return 'Hello world'



# /* --
import imp
import os
ctl_path = 'controllers'

controllers = [file for file in os.listdir(ctl_path) if file.endswith(".py")]
for m in controllers: # (x[0:-3] for x in os.listdir("controllers") if x.endswith(".py")):
    path = os.path.join(ctl_path,m)
    name = m[0:-3]
    
    #print('name: ', name)
    print('load controller: ', name)
    fp, pathname, description = imp.find_module(name , [ctl_path])
    mod = imp.load_module(name, fp, pathname, description)
    app.register_blueprint(getattr(mod, 'bp'))

# */



import redis
app.POOL = redis.ConnectionPool(host='redis', port=6379, db=0, decode_responses=True)



if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
