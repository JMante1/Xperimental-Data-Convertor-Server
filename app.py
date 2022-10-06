from flask import Flask, render_template, request
import os, flask
import xperimental_data_conv.main as xdc

cwd = os.getcwd()
upload_folder = os.path.join(cwd,'public')

app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = upload_folder

@app.route('/status')
def status():
    return("The XDC Server is up and running")

@app.route('/upload')
def upload_file_template():
    return render_template('upload.html')

	
@app.route('/uploader', methods = ['POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        fj_user = request.form['fjusername']
        fj_pass = request.form['fjpwd']
        sbh_user = request.form['sbhusername']
        sbh_pass = request.form['sbhpwd']
        sbh_collec = request.form['sbhcollec']

        if 'sbhover' in request.form:
            sbh_overwrite = True
        else:
            sbh_overwrite = False

        try:
            sbol_collec_url = xdc.experimental_data_uploader(f, fj_user, fj_pass,
                                    sbh_user, sbh_pass, sbh_collec, sbh_overwrite=sbh_overwrite,
                                    fj_overwrite=True)
            sbol_collec_url = f'{sbol_collec_url}{sbh_collec}_collection/1'
            return render_template('upload_success.html', collec_uploaded=sbol_collec_url)
        except:
            return render_template('upload_failure.html', collec_uploaded=sbh_collec)