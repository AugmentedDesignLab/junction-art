from flask import Flask, render_template
app = Flask(__name__, static_url_path="/assets", static_folder="assets")
app.config['FLASK_ENV'] = 'development'
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
def hello_world():
    return render_template('master.jinja', data = {'a': 'a', 'b': 'b'})


@app.route('/road-builder')
def roadBuilder():
    return render_template('road-builder.jinja', data = {'title': 'Road builder', 'b': 'b'})

if __name__ == '__main__':
   app.run()