

from wtforms import Form, StringField, validators

class initcfg(Form):
    mgtip = StringField('mgtip', [validators.Length(min=7, max=17)])
    mgtmask = StringField('mgtmask')
    mgtgtwy = StringField('mgtgtwy')
    mgtdns = StringField('mgtdns')
    e1ip = StringField('e1ip')
    e1zone = StringField('e1zone')
    e1inttype = StringField('e1inttype')
    e1profile = StringField('e1profile')
    e2ip = StringField('e2ip')
    e2zone = StringField('e2zone')
    e2inttype = StringField('e2inttype')
    e2profile = StringField('e2profile')

