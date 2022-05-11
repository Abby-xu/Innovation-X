from unittest import result
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from .account_utils import *
from . import nutrition_utils
from .record_utils import record_intake,get_past_intake_days,get_past_intake
import os
from flask import Flask, request, render_template, send_from_directory
from .counter_utils import *

views = Blueprint('views', __name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@views.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return redirect(url_for("views.dashboard"))
    #return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route("/dashboard.html")
@login_required
def dashboard():
    return render_template('index.html',name=current_user.email) 


@views.route("/settings.html")
@login_required
def settings():
    current_settings=get_settings(current_user.id)["data"]
    print(current_settings.items())
    return render_template('settings.html',current_settings=current_settings.items(),name=current_user.email)

@views.route("/change_settings", methods=['POST'])
@login_required
def change_settings():
    user_id=current_user.id
    new_setting={"user_id":user_id}
    #print(request.form)
    # for i in survey_options:
    #     new_setting[i]=request.form.get(i)=="on"
    #print(new_setting)
    update_settings(current_user.id,new_setting)

    return redirect(url_for("views.settings"))

@views.route("/records.html")
@login_required
def tracking():
    return render_template('records.html',name=current_user.email)

@views.route("/analysis.html")
@login_required
def analysis():
    return render_template('analysis.html',name=current_user.email)

@views.route("/upload.html")
@login_required
def index():
    return render_template("upload.html",name=current_user.email)

@views.route("/upload", methods=["POST"])
@login_required
def upload(): # allowed user upload multiple files
    target = os.path.join(APP_ROOT, 'scanned_images/')
    print(target)

    if not os.path.isdir(target):
        os.mkdir(target)

    for file in request.files.getlist("file"):
        print(file)
        filename = file.filename
        destination = "/".join([target, filename])
        print(destination)
        file.save(destination)
    return render_template("analysis.html",name=current_user.email)

@views.route("/scan", methods=["POST"])
@login_required
def scan():
    filename = os.path.join(APP_ROOT, 'scanned_images/', request.form['file_name'])
    # return jsonify(response=filename)#process_image(filename))
    # results = process_image(filename)
    results = filename
    return render_template("analysis.html",name=current_user.email,results=results)


@views.route("/help.html")
@login_required
def help():
    return render_template('help.html',name=current_user.email)

@views.route("/profile.html")
@login_required
def profile():
    return redirect(url_for("views.settings"))

@views.route("/admin")
@login_required
def admin():
    return redirect(url_for("home"))

############ need to fix ##########

@views.route("/nutrition/get_auto_complete",methods=['POST'])
def get_auto_complete():
    #print(request.json)
    #return jsonify(response=str("\n".join(nutrition_utils.get_auto_complete(request.form.get('name')))))
    return jsonify(response=str("\n".join(nutrition_utils.get_auto_complete(request.json["name"]))))
    #return jsonify(response=str("\n".join(["fooda","foodb","foodc"])))

@views.route("/nutrition/get_quantity_label",methods=['POST'])
def get_quantity_label():
    #return nutrition_utils.get_quantity_label(request.form.get('name'))
    return nutrition_utils.get_quantity_label(request.json["name"])

#This method also input record into user's database
@login_required
@views.route("/nutrition/get_nutrition",methods=['POST'])
def get_nutrition():
    my_request=request.json
    response= nutrition_utils.get_nutrition(str(my_request['foodId']),str(my_request['measure']),int(my_request['quantity']))
    
    record_intake(
        current_user.id,
        my_request['foodName'],
        response["calories"],
        response["totalNutrients"]["CHOCDF"]["quantity"],
        response["totalNutrients"]["FAT"]["quantity"],
        response["totalNutrients"]["PROCNT"]["quantity"],
        response["totalNutrients"]["NA"]["quantity"],
    )

    return response

@login_required
@views.route("/nutrition/get_analysis",methods=['POST'])
def get_analysis():
    my_request=request.json
    return get_past_intake_days(current_user.id,str(my_request["day"]),end_date=my_request["date"])

@login_required
@views.route("/nutrition/get_analysis_7",methods=['POST'])
def get_analysis_7():
    my_request=request.json
#    return get_past_intake(current_user.id,str(my_request["day"]))
    return get_past_intake(current_user.id,str(my_request["day"]))