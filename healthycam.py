import os
import requests
import json
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
from flask import Flask, request, redirect, url_for,send_from_directory,render_template, request
from werkzeug import secure_filename


UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                  filename=filename))
    return  render_template("app.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
   #address=send_from_directory(app.config['UPLOAD_FOLDER'],filename)
    var=os.path.abspath("uploads")
    var2=os.path.join(var, filename)
    app2 = ClarifaiApp(api_key='d85566d0480a4a42b7937ee35e07efb0')
    model = app2.models.get('food-items-v1.0')
    image = ClImage(file_obj=open(var2, 'rb'))
    response=model.predict([image])
    concepts = response['outputs'][0]['data']['concepts']
    result=' '
    for concept in concepts:
      if(concept['value']>.95):
        result="%s %s" % (result,concept['name'])


    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"

    pay1 = "{\r\n  \"query\":\""
    pay2=result
    pay3="\"\r\n  \r\n}"
    payload = pay1+pay2+pay3
        #print("org:"+payload)
    headers = {
    'x-app-id': "19b60cbc",
    'x-app-key': "f6526d97cd89cecca0c596c0ccda0c2c",
    'x-remote-user-id': "0",
    'Content-Type': "application/json",
    'cache-control': "no-cache",
    'Postman-Token': "595b6a9f-743c-4196-af70-e8eb2c30f4cb"
       }

    response = requests.request("POST", url, data=payload, headers=headers)


   #return render_template("results.html",concepts =concepts,result=result)
    json_data = json.loads(response.text)
    return render_template("results.html",json_data=json_data,concepts =concepts,result=result)



if __name__ == '__main__':
    app.run(debug=True)
