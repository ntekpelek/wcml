# -*- coding: utf-8 -*-

db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'],migrate=False)
response.generic_patterns = ['*'] if request.is_local else []

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True


db = DAL("sqlite://storage.sqlite",migrate=False)

db.define_table('survey',
    Field('name','string', requires=[IS_NOT_EMPTY(),IS_MATCH('^[a-zA-Z0-9_-]+$',error_message='bad char.')]),
    Field('ap_pos_x','integer'),
    Field('ap_pos_y','integer'),
    Field('ap_set','string'),
    Field('fplan_width','string'),
    Field('fplan_height','string'),
    Field('fplan_dim_set','string'),
    Field('hm_retr','string'),
    Field('download_name','string')
    )

db.define_table('floorplan',
    Field('survey_id','reference survey'),
    Field('file','upload'))
    
db.define_table('point',
    Field('survey_id', 'reference survey'),
    Field('name','string'),
    Field('pos_x','integer'),
    Field('pos_y','integer'),
    Field('signal_sta','integer'))

db.define_table('setting',
    Field('key','string'),
    Field('value','string'))
