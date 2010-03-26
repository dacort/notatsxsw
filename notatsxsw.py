from google.appengine.ext import webapp
from google.appengine.api import urlfetch
import urllib, re, logging
from xml.dom.minidom import parseString


class MainHandler(webapp.RequestHandler):

  def get(self, request_path):
    
    form_fields = {}
    for arg in self.request.arguments():
      form_fields[arg] = self.request.get(arg)
    
    headers = {'User-Agent': self.request.headers['User-Agent']}
    if 'Authorization' in self.request.headers:
      headers['Authorization'] = self.request.headers['Authorization']
    
    form_data = urllib.urlencode(form_fields)
    url = "https://api.twitter.com/1/%s" % request_path
    
    result = urlfetch.fetch(url="%s?%s" % (url,form_data),
                            headers=headers)
    
    if result.status_code != 200:
      logging.error("Twitter error: %s\n%s" % (result.status_code, result.content))
    
    xml = result.content
    # This is all we're hijacking at the moment
    if request_path == "statuses/home_timeline.xml":
      dom = parseString(xml)
      regex = re.compile(r"#sxsw", re.I)
      statuses = dom.getElementsByTagName('status')
      logging.info("Filtering %s statuses." % len(statuses))
      for node in statuses:
        text = node.getElementsByTagName('text')[0]
        if re.search("#?sxsw", text.firstChild.data, re.I) or re.search("(I'm at|I just became the mayor|I just ousted|I just unlocked).*http:\/\/(4sq\.com|gowal\.la\/[a-z])\/\w+", text.firstChild.data) or re.search("I favorited a YouTube video.*http:\/\/youtu\.be\/\w+", text.firstChild.data):
          logging.info("Removing: %s" % text.firstChild.data)
          node.parentNode.removeChild(node)
      xml = dom.toxml()
    
    self.response.out.write(xml)

  def post(self, request_path):
    form_fields = {}
    for arg in self.request.arguments():
      form_fields[arg] = self.request.get(arg)
    
    headers = {'User-Agent': self.request.headers['User-Agent']}
    if 'Authorization' in self.request.headers:
      headers['Authorization'] = self.request.headers['Authorization']
      
    form_data = urllib.urlencode(form_fields)
    url = "https://api.twitter.com/1/%s" % request_path
    result = urlfetch.fetch(url=url,
                            payload=form_data,
                            method=urlfetch.POST,
                            headers=headers)
    
    self.response.out.write(result.content)
