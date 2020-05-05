import os
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.abspath(os.path.dirname(__file__)) + "/img2scan"

app = Flask(__name__)
app.secret_key = "SappE1keyG422D0k3EVk3Ty4pEphfCt3wTo85dtkhyu"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
# limit to JPG images because thats all PIXELKNOT handles iirc
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])

filename = ""

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# route to API, accepts POST request with multi part form data
@app.route('/steg/detect', methods=['POST'])
def scan_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        resp = jsonify({'Error': 'No file part in the request'})
        resp.status_code = 204  # 'no content'
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'Error': 'No file selected for uploading'})
        resp.status_code = 204  # 'no content'
        return resp
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))      # save the file
        imgfile = app.config['UPLOAD_FOLDER'] + "/" + filename              # set a variable for the image location

    ####### StegCheck SCRIPT #######

    stegd = '~/stegdetect/./stegdetect -tF ' + imgfile      # This is the command we want to run.
    stream = os.popen(stegd)                                # Run it!
    output = stream.readlines()         # Grab the console output
    results = ""
    for x in output:
        results = results + x           # grab all the output from the console and store it in a var called 'results'

    resp = jsonify({'Found': 'F5'})     # temporarily set the response to the results, although we'll change it later
    if results.find("negative") != -1 and results.find("***") > 1:
        # found F5 - Very High Confidence
        resp = jsonify({'F5 Stego': 'VERY High Confidence'})
        resp.status_code = 201
        return resp
    elif results.find("negative") != -1 and results.find("**") > 1:
        # found F5 - High Confidence
        resp = jsonify({'F5 Stego': 'High Confidence'})
        resp.status_code = 201
        return resp
    elif results.find("negative") != -1 and results.find("*") > 1:
        # found F5 - High Confidence
        resp = jsonify({'F5 Stego': 'Fairly Confident'})
        resp.status_code = 201
        return resp
    elif results.find("negative") > 0:
        # did NOT find F5
        resp = jsonify({'F5 Stego': 'Not Found'})
        resp.status_code = 201
        return resp

    return resp


@app.route('/')
def index():
    # build HTML response for anyone not using the API
    html = "<html><body valign='middle'><center>"
    html = html + "<div width='40%'></div>"
    html = html + "<div style='align:center;width:20%;padding:25px;margin:50px;border-radius:20px;background:#e8e8e8;'>"
    html = html + "<center><h1>F5 Steganography Detection</h1>"
    html = html + "<h4>This is not the endpoint you're looking for...</h4><br>"
    html = html + "<br><b><em>Endpoint</em>:</b><br>" \
                  "/detect/f5 - check for F5 Steganography<br>" \
                  "<br><b>Returns (1 of 4):</b>  " \
                  "Not Found<br>Fairly Confident (<b>*</b>)<br>High Confidence (<b>**</b>)<br>VERY High Confidence (<b>***</b>)<br>" \
                  "<br>" \
                  "</center>"
    html += "</div><div width='40%'></div></center></body</html>"
    return html