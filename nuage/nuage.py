import base64
import time
import urllib2
import ssl
import json

class NuageAPI(object):
  def __init__(self, vsdaddress, login, password, organization):
    self.vsdurl = "https://"+vsdaddress
    self.login = login
    self.authstring = base64.b64encode("%s:%s"%(login, password))
    self.organization = organization
    self.apiauthstring = None
    self.apikey_expiry = 0

    self.sslctx = None
    if hasattr(ssl, 'SSLContext'):
      self.sslctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
      self.sslctx.verify_mode = ssl.CERT_NONE

    self.last_event = None

  def __retrieve_apikey(self):
    headers = {
        "X-Nuage-Organization": self.organization,
        "Authorization": "XREST "+self.authstring
      }
    kwargs = {}
    if self.sslctx is not None:
      kwargs['context'] = self.sslctx

    req = urllib2.Request(self.vsdurl+"/nuage/api/v3_0/me", headers=headers)
    f = urllib2.urlopen(req, **kwargs)
    res = json.load(f)

    self.apiauthstring = base64.b64encode("%s:%s"%(self.login, res[0]['APIKey']))
    self.apikey_expiry = res[0]['APIKeyExpiry']

  def api_call(self, url, timeout=None):
    if time.time() > self.apikey_expiry:
      self.__retrieve_apikey()

    headers = {
      "Authorization": "Basic "+self.apiauthstring,
      "X-Nuage-Organization": self.organization
    }
    kwargs = {'timeout': timeout}
    if self.sslctx is not None:
      kwargs['context'] = self.sslctx

    req = urllib2.Request(self.vsdurl+"/nuage/api/v3_0"+url, headers=headers)
    f = urllib2.urlopen(req, **kwargs)

    try:
      res = json.load(f)
    except ValueError:
      res = []

    return res

  def list_enterprises(self):
    return self.api_call("/enterprises")

  def get_enterprise_summary(self, enterpriseid):
    return self.api_call("/enterprises/"+enterpriseid+"/summary")

  def list_enterprise_vms(self, enterpriseid):
    return self.api_call("/enterprises/"+enterpriseid+"/vms")

  def list_enterprise_domains(self, enterpriseid):
    return self.api_call("/enterprises/"+enterpriseid+"/domains")

  def list_domains(self):
    return self.api_call("/domains")

  def list_domain_policygroups(self, domainid):
    return self.api_call("/domains/"+domainid+"/policygroups")

  def list_domain_zones(self, domainid):
    return self.api_call("/domains/"+domainid+"/zones")

  def list_policygroup_vports(self, pgid):
    return self.api_call("/policygroups/"+pgid+"/vports")

  def list_vport_vminterfaces(self, vpid):
    return self.api_call("/vports/"+vpid+"/vminterfaces")

  def list_vports(self):
    return self.api_call("/vports")

  def list_zone_subnets(self, zoneid):
    return self.api_call("/zones/"+zoneid+"/subnets")

  def list_subnet_vports(self, subnetid):
    return self.api_call("/subnets/"+subnetid+"/vports")

  def nevents(self, levent=None):
    if levent:
      self.last_event = levent

    url = "/events"
    if self.last_event:
      url += "?uuid="+self.last_event

    res = self.api_call(url, timeout=300)

    self.last_event = res['uuid']
    return res['events']

def build_policygroup_image(n, pg):
  pgimg = {
    'name': pg['name'], 
    'vports': {},
    'zone': None
  }

  for vp in n.list_policygroup_vports(pg['ID']):
    vpimg = {}
    for vmi in n.list_vport_vminterfaces(vp['ID']):
      vpimg['address'] = vmi['IPAddress']
    pgimg['vports'][vp['ID']] = vpimg

  return pgimg


if __name__ == "__main__":
  import pprint

  pp = pprint.PrettyPrinter()

  image_of_nuage = {}
  zones = {}

  n = NuageAPI("10.0.20.21", "csproot", "poi@UYT098", "csp")
  
  for d in n.list_domains():
    print d['name'], d['ID']
    for z in n.list_domain_zones(d['ID']):
      zones[z['ID']] = { 'name': z['name'], 'vports': [] }
      for s in n.list_zone_subnets(z['ID']):
        for vp in n.list_subnet_vports(s['ID']):
          zones[z['ID']]['vports'].append(vp['ID'])

    for pg in n.list_domain_policygroups(d['ID']):
      pgimg = build_policygroup_image(n, pg)

      image_of_nuage[pg['ID']] = pgimg

  pp.pprint(image_of_nuage)

  while True:
    evts = n.nevents()
    for e in evts:
      if e['entityType'] != 'policygroup' or not e['type'] in ['UPDATE', 'DELETE']:
        continue
      for pg in e['entities']:
        if e['type'] == 'DELETE':
          if pg['ID'] in image_of_nuage:
            print 'pg %s deleted'%pg['ID']

            del image_of_nuage[pg['ID']]

            pp.pprint(image_of_nuage)

          continue

        if not pg['ID'] in image_of_nuage:
          pgimg = build_policygroup_image(n, pg)
          image_of_nuage[pg['ID']] = pgimg

          print 'pg %s created'%pg['ID']

          pp.pprint(image_of_nuage)

          continue

        pgimg = build_policygroup_image(n, pg)
        for vp in image_of_nuage[pg['ID']]['vports']:
          if vp not in pgimg['vports']:
            print 'vport %s deleted from pg %s'%(vp, pg['ID'])
        for vp in pgimg['vports'].keys():
          if vp not in image_of_nuage[pg['ID']]['vports']:
            print 'vport %s added to pg %s'%(vp, pg['ID'])
        image_of_nuage[pg['ID']] = pgimg
        pp.pprint(image_of_nuage)







