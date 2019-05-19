import os
from flask import jsonify, request, make_response, send_from_directory
from app import app, mongo
import logger

ROOT_PATH = os.environ.get('ROOT_PATH')
LOG = logger.get_root_logger(__name__, filename=os.path.join(ROOT_PATH, 'output.log'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if request.form['policy'] == "policy1":
            setpolicy = 1
        if request.form['policy'] == "policy2":
            setpolicy = 2
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #encrypt to provided policy
            encryptedByteArray = bytearray(encrypt(setpolicy,file))
            encryptedByteArray.save(os.path.join(app.config['ENCRYPTED_FOLDER'], filename))
            jsresp = [ { "name" : filename, "url" : url_for('uploaded_file', filename=filename)} ]
            return Response(json.dumps(jsresp),  mimetype='application/json')    #Change response to 200 OK
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)