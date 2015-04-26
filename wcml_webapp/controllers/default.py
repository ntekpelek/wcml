# -*- coding: utf-8 -*-

import sig_mon_conn
import os
import zipfile
import time
import json as json_mod
import shlex
import subprocess
import tempfile

def get_setting():
    """
    Return current value of app setting from db. 
    """
    setting = db(db.setting.key == request.args[0]).select(db.setting.value)
    return setting[0]['value']

def get_surv_set():
    """
    Return survey setting value.
    """
    setting = db(db.survey.id == 1).select(db.survey[request.args[1]])
    return setting[0][request.args[1]]


def set_setting():
    """
    Set value of key in setting table according to URL:
    set_setting/key/new_value
    """
    key = request.args[0]
    value = request.args[1]
    cur_set = db(db.setting.key == key).select().first()
    cur_set.value = value
    cur_set.update_record()
    return 'OK'


def set_surv_set():
    """
    Set survey setting according to URL:
    set_surv_set/survey_id/setting_name/new_val
    """
    set_name = request.args[1]
    new_val = request.args[2]
    surv_row = db(db.survey.id == 1).select().first()
    surv_row[set_name] = new_val
    surv_row.update_record()
    return 'OK'

def reset_survey():
    """
    Clean survey data:
    - truncate db.points and AP loctation
    - remove heatmap
    - clean db values
    """
    db.point.truncate()
    surv_row = db(db.survey.id == 1).select().first()
    surv_row['ap_set'] = 'false'
    surv_row['hm_retr'] = 'false'
    surv_row.update_record()
    if os.path.exists(request.folder+"static/images/hmap.png"):    
        os.remove(request.folder+"static/images/hmap.png")
    return "OK"

def reset_app():
    """Reset app to factory defaults: empty DB and 
    sample floorplan
    """
    if os.path.exists(request.folder+"static/images/hmap.png"):    
        os.remove(request.folder+"static/images/hmap.png")
    db.point.truncate()
    db.survey.truncate()
    db.floorplan.truncate()
    db.survey.insert(name='example',ap_pos_x=0, ap_pos_y=0, ap_set='false',
                     fplan_width=0, fplan_height=0, fplan_dim_set = 'false',
                     hm_retr='false')
    db.setting.truncate()
    db.setting.insert(key='user_fplan_loaded', value='false')
    db.floorplan.insert(survey_id=1)
    redirect(URL('index'))
    return "OK"

def about():
    """
    Show about page
    """
    response.view='default/about.html'
    return dict()

def generate_deliverables():
    """
    Prepare .zip archive combining floorplan, heatmap and
    collected points in user friendly webpage.
    """
    # define templates
    PAGE_TMPL = """<html>
    <head>
    <title>WiFi Coverage Mapper
    </title>
    <style media=\"screen\" type=\"text/css\">
    div.img {
        position: absolute;
        top: 40px;
    }
    .sample, .ap {
        position: absolute;
        width: 16px;
        height: 16px;
        background-color: black;
        color: white;
        font-size: 11px;
    }
    #heatmap {
        opacity: 0.6;
    }
    
    span.btn {
	padding: 4px;
	margin: 1px;
	border: 1px solid black;
	
    }
    </style>
    <script>
    function setOp(newVal) {
        document.getElementById('heatmap').style.opacity = newVal;
    }
    </script>
    </head>
    <body>
    <script>
    var steps = ['0.2','0.4','0.6','0.8','1'];
    for ( var i=0; i<steps.length; i++ ) {
    document.writeln("<span class=\\"btn\\" onClick=\\"setOp(this.textContent)\\">"+steps[i]+"</span>");
    }
    </script>
    <div class=\"img\">
    <img id=\"floorplan\" src=\"fplan.png\" />
    </div>
    <div class=\"img\">
    <img id=\"heatmap\" src=\"hmap.png\" />
    </div>
    <div class=\"img\">
    %s
    </div>
    <div class=\"img\">
    %s
    </div>
    </body>
    </html>
    """
    POINT_TMPL = "<div class=\"sample\" alt=\"%s\" style=\"margin-left: %spx; margin-top: %spx;\">%s</div>\r\n"
    AP_TMPL = "<div class=\"ap\" alt=\"AP\" style=\"margin-left: %spx; margin-top: %spx;\">AP</div>\r\n"
    # prepare and loop on points data
    points = db.executesql('select pos_x as posX, pos_y as posY, signal_sta as signalSta from point', as_dict=True)
    meta = __prepare_meta_dict()
    pointsout = ""
    for point in points:
        pointsout += POINT_TMPL % ( point['signalSta'], int(point['posX'])-8, int(point['posY'])-8, point['signalSta'] )
    # fill AP template
    apout = AP_TMPL % ( meta['apPosX'], meta['apPosY']) 
    # fill whole page template
    htmlout = PAGE_TMPL % ( pointsout, apout )
    # write .json survey data in temp file
    data = json_mod.dumps({'survey':{'points':points,'meta':meta}})
    tmp_json = tempfile.NamedTemporaryFile(delete=False)
    with open(tmp_json.name,'w') as out_file:
        json_mod.dump(data, out_file)
    out_file.close()
    # prepare zip file
    zip_name = meta['surveyName']+'_'+meta['surveyTs']
    zipout = zipfile.ZipFile(request.folder+"static/deliverables/"+zip_name+".zip","w")
    # check if custom floorplan has been uploaded by user
    fplan_loaded = db(db.setting.key =='user_fplan_loaded').select(db.setting.value).first()['value']
    if fplan_loaded == 'true':
        floorplan = db(db.floorplan.survey_id == 1 ).select().first()
        zipout.write(request.folder+"uploads/"+floorplan.file,zip_name+"/fplan.png")
    else:
        zipout.write(request.folder+"static/images/fplan-sample.jpg",zip_name+"/fplan.png")
    zipout.write(request.folder+"static/images/hmap.png",zip_name+"/hmap.png")
    zipout.writestr(zip_name+"/survey.html",htmlout)
    zipout.write(tmp_json.name,zip_name+"/survey.json")
    zipout.close()
    os.remove(tmp_json.name)
    return zip_name
    
    
def __prepare_meta_dict():
    """Prepares dict() containing required values of 'meta' section
    in JSON communication."""
    res = dict()
    surv = db(db.survey.id == 1).select().first()
    res['floorPlanWidth'] = int(surv['fplan_width'])
    res['floorPlanHeight']= int(surv['fplan_height'])
    res['surveyTool']= 'wcmpc'
    res['surveyToolVer'] = '0.1'
    res['surveyName'] = surv['name']
    res['surveyTs'] = time.strftime("%Y-%m-%d_%H-%M-%S")
    res['signalApIncluded'] = 'false'
    res['rateIncluded'] ='false'
    res['apPosX'] = int(surv['ap_pos_x']);
    res['apPosY'] = int(surv['ap_pos_y']);
    return res
    
def generate_heatmap():
    """
    Generate heatmap. Retrieves data from db, prepare and
    call heatmap generator which save output to static/images/hmap.png.
    """
    # removes old heatmap
    if os.path.exists(request.folder+"static/images/hmap.png"):    
        os.remove(request.folder+"static/images/hmap.png")    
    # prepare data    
    meta = __prepare_meta_dict()
    points = db.executesql('select pos_x as posX, pos_y as posY, signal_sta as signalSta from point', as_dict=True)
    data = json_mod.dumps({'survey':{'points':points,'meta':meta}})
    
    # write to temp. file
    tmp_json = tempfile.NamedTemporaryFile(delete=False)
    with open(tmp_json.name,'w') as out_file:
        json_mod.dump(data, out_file)
    out_file.close()
    
    # call heatmap generator
    gen_cmd = '/opt/wcml/bin/wcml_hm_gen.py -i %s -o %s' % ( tmp_json.name, 
        request.folder+'static/images/hmap.png' )
    args = shlex.split(gen_cmd)
    res = subprocess.call(args) # call generator
    os.remove(tmp_json.name) # remove temp file
    
    # update db if succeeded
    if ( res == 0 ):
        surv_row = db( db.survey.id == 1 ).select().first()
        surv_row['hm_retr'] = 'true'
        surv_row.update_record()
        return "OK"
    else: 
        return "FAILED"


def get_signal():
    """
    Retrieves signal level from signal monitoring process.
    """
    return sig_mon_conn.get_signal()

def retrieve_survey_points():
    """
    Retrieves survey points.
    """
    points = db().select(db.point.ALL)
    return dict(points=points)

def index():
    """
    Splash page - starting page of the app.
    """
    surveys = db().select(db.survey.ALL)
    fplan_loaded = db(db.setting.key =='user_fplan_loaded').select(db.setting.value).first()['value']
    if fplan_loaded == 'true':
        floorplans = db(db.floorplan.survey_id == 1 ).select()
        return dict(surveys=surveys,fplan_loaded=fplan_loaded,floorplans=floorplans)
    else:
        return dict(surveys=surveys,fplan_loaded=fplan_loaded)

def do_survey():
    """
    Launch JS app where user can do survey.
    """
    surveys = db().select(db.survey.ALL)
    response.view='wcmljsapp.html'
    fplan_loaded = db(db.setting.key =='user_fplan_loaded').select(db.setting.value).first()['value']
    if fplan_loaded == 'true':
        floorplans = db(db.floorplan.survey_id == 1 ).select()
        return dict(surveys=surveys,fplan_loaded=fplan_loaded,floorplans=floorplans)
    else:
        return dict(surveys=surveys,fplan_loaded=fplan_loaded)

    
def set_floorplan():
    """
    Allows user change floorplan. 
    """
    response.view='default/forms.html'
    form = SQLFORM(db.floorplan,1,fields=['file'],labels={'file':'Survey floorplan'},
                   showid=False, submit_button='Save',formstyle='divs')
    if form.process().accepted:
        # unset dimensions 
        surv_row = db( db.survey.id == 1 ).select().first()
        surv_row['fplan_dim_set'] = 'false'
        surv_row.update_record()
        # mark user has loaded floorplan
        fplan_loaded_set = db(db.setting.key =='user_fplan_loaded').select().first()
        fplan_loaded_set['value'] = 'true'
        fplan_loaded_set.update_record()
        response.flash = 'form accepted'

    elif form.errors:
        response.flash = 'form has errors'
    
    return dict(form=form)


def set_survey_name():
    """
    User can change survey name here.
    """
    response.view='default/forms.html'
    form = SQLFORM(db.survey,1,fields=['name'],labels={'name':'Survey name'},
                   showid=False,submit_button='Save',formstyle='divs')
    if form.process().accepted:
        response.flash = 'form accepted'
        redirect(URL('index'))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'

    return dict(form=form)


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

@service.jsonrpc
def save_point(name,pos_x,pos_y,signal_sta):
    db.point.insert(survey_id=1,name=name,pos_x=pos_x,pos_y=pos_y,signal_sta=signal_sta)
    return 'OK'
