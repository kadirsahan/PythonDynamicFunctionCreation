from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
  return "<h1>Dynamicfunctionreation</h1>"



@app.route("/query")
def index():
  return "<h1>Dynamicfunctionreation</h1>"




app.run(host="0.0.0.0", port=9080, debug=False)