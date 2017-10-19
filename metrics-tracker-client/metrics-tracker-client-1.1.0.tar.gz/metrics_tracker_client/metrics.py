import json
import yaml
import time
import getpass
from requests import post, get

def getJson():
	try:
		f = open("repository.yaml", "r")
		response = f.read()
		original = yaml.load(response)
		data = json.loads(json.dumps(original))
		f.close()
		return data
	except:
		return None

def massage(journey_metric, event):
	try:
		event['config'] = {}
		event['config']['repository_id'] = journey_metric['id'] if journey_metric.get("id") else ''
		event['config']['target_runtimes'] = journey_metric['runtimes'] if journey_metric.get("runtimes") else ''
		event['config']['target_services'] = journey_metric['services'] if journey_metric.get("services") else ''
		event['config']['event_id'] = journey_metric['event_id'] if journey_metric.get("event_id") else ''
		event['config']['event_organizer'] = journey_metric['event_organizer'] if journey_metric.get("event_organizer") else ''
	except:
		pass
	return event

def DSXtrack(metric):
	event = dict()
	event['date_sent'] = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
	event['runtime'] = 'python'
	try:
		event['space_id'] = getpass.getuser()
	except:
		pass
	try:
		link = ''.join(['https://raw.githubusercontent.com/', metric,'/master/repository.yaml'])
		response = get(link)
		original = yaml.load(response.text)
		data = json.loads(json.dumps(original))
		massage(data,event)
	except:
		print("metric not tracked")
		event['config'] = {}

	url = 'https://metrics-tracker.mybluemix.net/api/v1/track'
	headers = {'content-type': "application/json"}
	try:
		response = post(url, data=json.dumps(event), headers=headers)
	except Exception as e:
		print ('Deployment Tracker upload error: %s' % str(e))