
# TalentCircles.py
#
# A module for accessing the TalentCircles REST API
#
# @author tom@talentcircles.com
# @copyright Copyrights (c) 2017 TalentCircles Inc.

import requests
import datetime
import urllib3
import json
from requests.auth import HTTPDigestAuth

class TalentCircles:
    'A developer library for accessing a TalentCircles REST API'

    def __init__(self, domain, app_id, api_key, prefix='https://',
                 api_path='/api/v1/', environment='pro'):
        self.domain = domain
        self.app_id = app_id
        self.api_key = api_key
        self.prefix = prefix
        self.api_path = api_path
        self.environment = environment
        self.url = prefix + domain + api_path
        self.verify_ssl = True

        # if development mode
        if environment == 'dev':
            self.verify_ssl = False
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def get_resource(self, resource, resource_id):
        url = self.url + resource
        if resource_id:
            if type(resource_id) is list:
                ids_string = ','.join(str(x) for x in resource_id)
                url += "/" + str(ids_string)
            else:
                url += "/" + str(resource_id)

        response = requests.request(
                "GET", url,
                auth=HTTPDigestAuth(self.app_id, self.api_key),
                verify=self.verify_ssl)

        return json.loads(response.text)

    def get_posessions(self, resource, resource_id, possession,
                       additional_params=None):
        if not resource_id:
            return

        url = self.url + resource + '/' + str(resource_id) + '/' + possession

        if additional_params is None:
            response = requests.request(
                "GET", url,
                auth=HTTPDigestAuth(self.app_id, self.api_key),
                verify=self.verify_ssl)
        else:
            response = requests.request(
                "GET", url,
                auth=HTTPDigestAuth(self.app_id, self.api_key),
                params=additonal_params, verify=self.verify_ssl)

        if not response.text:
            return
        else:
            return json.loads(response.text)

    def create_resource(self, resource, resource_data, default_fields=None):
        url = self.url + resource
        if default_fields is None:
            payload = resource_data
        else:
            # start with resource_data's keys and values
            payload = default_fields.copy()
            payload.update(resource_data)

        response = requests.request(
            "POST", url, data=payload,
            auth=HTTPDigestAuth(self.app_id, self.api_key),
            verify=self.verify_ssl)

        return json.loads(response.text)

    def create_possession(self, resource, resource_id, possession,
                          possession_data, default_fields=None):
        url = self.url + resource + '/' + str(resource_id) + '/' + possession
        if default_fields is None:
            payload = possession_data
        else:
            # start with possession_data's keys and values
            payload = default_fields.copy()
            payload.update(possession_data)

        response = requests.request(
            "POST", url, data=payload,
            auth=HTTPDigestAuth(self.app_id, self.api_key),
            verify=self.verify_ssl)

        return json.loads(response.text)

    def search_resource(self, resource, search_params, page=1,
                        results_per_page=10):
        querystring = {
            "page":page,
            "results_per_page":results_per_page
        }

        if search_params:
            for param_name, param_value in search_params.iteritems():
                querystring[param_name] = param_value

        url = self.url + resource

        response = requests.request(
            "GET", url, auth=HTTPDigestAuth(self.app_id, self.api_key),
            params=querystring, verify=self.verify_ssl)

        return json.loads(response.text)

    def update_resource(self, resource, resource_id, resource_data):
        url = self.url + resource
        if resource_id:
            if type(resource_id) is list:
                ids_string = ','.join(str(x) for x in resource_id)
                url += "/" + str(ids_string)
            else:
                url += "/" + str(resource_id)

        response = requests.request(
            "PUT", url, data=resource_data,
            auth=HTTPDigestAuth(self.app_id, self.api_key),
            verify=self.verify_ssl)

        return json.loads(response.text)

    def validate_resource(self, resource_data, required_fields):
        for field in required_fields:
            if field not in resource_data.keys():
                raise KeyError, "Required field missing: " + field
            elif resource_data[field] is None:
                raise ValueError, "Required field is None: " + field
        return resource_data


    # JOBS
    def get_job(self, job_id):
        if not job_id:
            raise ValueError, 'Missing job_id'
        job = self.get_resource('jobs', job_id)
        return job['job']

    def get_jobs(self, job_ids):
        if not job_ids:
            raise ValueError, 'Missing job_ids'
        result = self.get_resource('jobs', job_ids)
        return result['jobs']

    def get_job_candidates(self, job_id):
        if not job_id:
            raise ValueError, 'Missing job_id'
        result = self.get_posessions('jobs', job_id, 'candidates')
        return result['candidates']

    def get_similar_jobs(self, job_id):
        if not job_id:
            raise ValueError, 'Missing job_id'
        result = self.get_posessions('jobs', job_id, 'similar_jobs')
        return result['jobs']

    def create_job(self, job_data):
        default_details = {
            'available_on':datetime.date.today().strftime("%B %-d, %Y"),
            'commitment_level':'Full-Time',
            'apply_behavior':'url redirect',
            'urlRedirect':'https://talentcircles.com'
        }

        if 'category_id' not in job_data:
            return 'Error: Category ID required'

        result = self.create_resource('jobs', job_data, default_details)
        return result['job']

    def search_jobs(self, search_params, page=1, results_per_page=10):
        result = self.search_resource(
            'jobs', search_params, page=page,
            results_per_page=results_per_page)

        return result['jobs']

    def update_job(self, job_id, job_data):
        if not job_id:
            raise ValueError, 'Missing job_id'
        result = self.update_resource('jobs', job_id, job_data)
        return result['job']

    # USERS
    def get_user(self, user_id):
        if not user_id:
            raise ValueError, 'Missing user_id'
        user = self.get_resource('users', user_id)
        return user['user']

    def get_users(self, user_ids):
        if not user_ids:
            raise ValueError, 'Missing user_ids'
        result = self.get_resource('users', user_ids)
        return result['users']

    def get_user_matching_jobs(self, user_id):
        if not user_id:
            raise ValueError, 'Missing user_id'
        result = self.get_posessions('users', user_id, 'matching_jobs')
        return result['jobs']

    def get_user_stories(self, user_id, additonal_params=None):
        if not user_id:
            raise ValueError, 'Missing user_id'
        if additonal_params is None:    
            result = self.get_posessions('users', user_id, 'stories')
        else:
            result = self.get_posessions(
                'users', user_id, 'stories', addtional_params)
        return result['stories']

    def get_similar_users(self, user_id):
        user_list = []
        if not user_id:
            raise ValueError, 'Missing user_id'
        result = self.get_posessions('users', user_id, 'similar_candidates')
        return result['users']

    def create_user(self, user_data):
        valid_data = self.validate_user_data(user_data)
        result = self.create_resource('users', valid_data)
        return result['user']

    def search_users(self, search_params, page=1, results_per_page=10):
        result = self.search_resource(
            'users', search_params, page=page,
            results_per_page=results_per_page)

        return result['users']

    def update_user(self, user_id, user_data):
        result = self.update_resource('users', user_id, user_data)
        if result:
            updated_user = self.get_user(result['user']['user_id'])
            return updated_user

    def validate_user_data(self, user_data):
        required_fields = [
            'firstname',
            'lastname',
            'email'
        ]
        validated = self.validate_resource(user_data, required_fields)
        if ('zipcode' not in validated.keys()
                and 'city' not in validated.keys()
                and 'state' not in validated.keys()):
            raise ValueError, 'Missing location data for new user. \
                Please include either a zipcode, or a city and state.'
        return validated

    # CIRCLES
    def create_circle(self, circle_data):
        valid_data = self.validate_circle_data(circle_data)
        result = self.create_resource('circles', circle_data)
        return result['circle']

    def get_circle(self, circle_id):
        if not circle_id:
            raise ValueError, 'Missing circle_id'
        result = self.get_resource('circles', circle_id)
        return result['circle']

    def get_circles(self, circle_ids):
        if not circle_ids:
            raise ValueError, 'Missing circle_id'
        elif type(circle_ids) is not list:
            raise TypeError, 'circle_ids must be a list'
        result = self.get_resource('circles', circle_ids)
        return result['circles']

    def get_circle_jobs(self, circle_id, additonal_params=None):
        if not circle_id:
            raise ValueError, 'Missing circle_id'

        if additonal_params is None:
            result = self.get_posessions('circles', circle_id, 'jobs')
        else:
            result = self.get_posessions(
                'circles', circle_id, 'jobs', additonal_params)

        return result['jobs']

    def get_cricle_members(self, circle_id):
        if not circle_id:
            raise ValueError, 'Missing circle_id'
        result = self.get_posessions('circles', circle_id, 'users')
        return result['users']

    def get_circle_stories(self, circle_id):
        if not circle_id:
            raise ValueError, 'Missing circle_id'
        result = self.get_posessions('circles', circle_id, 'stories')
        return result['stories']

    def post_circle_story(self, circle_id, story_data):
        if not circle_id:
            raise ValueError, 'Missing circle_id'
        valid_data = self.validate_story_data(story_data)
        result = self.create_possession(
            'circles', circle_id, 'stories', valid_data)
        return result['story']

    def update_circle(self, circle_id, circle_data):
        result = self.update_resource('circles', circle_id, circle_data)
        if result:
            updated_circle = self.get_circle(result['circle']['circle_id'])
            return updated_circle

    def validate_circle_data(self, circle_data):
        required_fields = [
            'circle_name'
        ]
        validated = self.validate_resource(circle_data, required_fields)
        return validated

    # STORIES
    def get_story(self, story_id):
        if not story_id:
            raise ValueError, 'Missing story_id'
        result = self.get_resource('stories', story_id)
        return result['story']

    def get_stories(self, story_ids):
        if not story_ids:
            raise ValueError, 'Missing story_ids'
        elif type(story_ids) is not list:
            raise TypeError, 'story_ids must be of type list'
        result = self.get_resource('stories', story_ids)
        return result['stories']

    def post_story(self, story_data):
        valid_data = self.validate_story_data(story_data)
        if 'circle_id' not in valid_data.keys():
            raise ValueError, 'circle_id not specified in story_data'
        result = self.create_resource('stories', story_data)
        return result['story']

    def update_story(self, story_id, story_data):
        if not story_id:
            raise ValueError, 'Missing story_id'
        result = self.update_resource('stories', story_id, story_data)
        return result['story']

    def update_stories(self, story_ids, story_data):
        if not story_ids:
            raise ValueError, 'Missing story_ids'
        elif type(story_ids) is not list:
            raise TypeError, 'story_ids must be of type list'
        result = self.update_resource('stories', story_ids, story_data)
        return result['stories']

    def validate_story_data(self, story_data):
        required_fields = [
            'title',
            'story'
        ]
        validated = self.validate_resource(story_data, required_fields)
        return validated


#################################################
############### USAGE ###########################
#################################################

# Your network's App ID
# app_id = "romeo-5931c22e4190b"

# # Used to authenticate with the API
# api_key = "Y1IgDgriOjAo5hKMzZ0RxC"

# # The specific TalentCircles network's url
# domain = "mytalentmall.talentcircles.vm"

# talent_api = TalentCircles(domain, app_id, api_key, environment='dev')

### JOBS ###
# job = talent_api.get_job(7480159)
# print(job['job_title'])

# two_jobs = talent_api.get_jobs([7480159, 8773787])
# for job in two_jobs:
#   print job['job_title']

# new_job_data = {
#   'job_title':'Extremely Excellent Accountant',
#   'available_on':'November 6, 2017',
#   'category_id': 1,
#   'zipcode':94066,
#   'description':'We need someone to teach our other accountants.',
# }
# new_job = talent_api.create_job(new_job_data)
# print(new_job['job_title'])

# update_job_data = {
#   'job_title':'Very Competent Accountant II'
# }
# updated_job = talent_api.update_job(8698598, update_job_data)
# print(updated_job['job_title'])

# job_candidates = talent_api.get_job_candidates(7480159);
# print(job_candidates)[0]['formatted_name2']

# similar_jobs = talent_api.get_similar_jobs(7480159);
# print similar_jobs[0]['job_title']

# searched_jobs = talent_api.search_jobs({"commitment_levels":1})
# print searched_jobs[0]['job_title']

### USERS ###
# user = talent_api.get_user(12770260)
# print user['formatted_name']

# two_users = talent_api.get_users([12770410, 12769405])
# for user in two_users:
#   print user['firstname']

# user_matching_jobs = talent_api.get_user_matching_jobs(12770260)
# print user_matching_jobs[0]['job_title']

# similar_users = talent_api.get_similar_users(12770260)
# print similar_users[0]['formatted_name']

# user_data = {
#   'firstname':'Tim',
#   'lastname':'Wallace',
#   'email':'twallace@synaptic.net',
#   'password':'secretpass',
#   'zipcode':78704
# }
# new_user = talent_api.create_user(user_data)
# print new_user['formatted_name']

# update_user_data = {
#   'lastname':'Flynt'
# }
# updated_user = talent_api.update_user(12770414, update_user_data)
# print updated_user['formatted_name']

# searched_users = talent_api.search_users({"commitment_levels":1})
# print searched_users[0]['formatted_name']

# user_stories = talent_api.get_user_stories(10961800)
# print user_stories[0]['title']

### CIRCLES ###
# circle = talent_api.get_circle(375)
# print circle['circle_name']

# circles = talent_api.get_circles([375,372])
# for circle in circles:
#   print circle['circle_name']

# circle_stories = talent_api.get_circle_stories(375)
# for story in circle_stories:
#   print story['title']

# cricle_members = talent_api.get_cricle_members(375)
# for user in cricle_members:
#   print user['formatted_name']

# new_circle_data = {
#   'circle_name':'Fantastically Great Circle'
# }
# new_circle = talent_api.create_circle(new_circle_data)
# print new_circle['circle_name']

# update_circle_data = {
#   'circle_name':'Awesomely Fantastically Great Circle'
# }
# updated_circle = talent_api.update_circle(385, update_circle_data)
# print updated_circle['circle_name']

# circle_jobs = talent_api.get_circle_jobs(375)
# for job in circle_jobs:
#   print job['job_title']

# circle_story_data = {
#   'title':'Great Story',
#   'story':'This story is great.'
# }
# circle_story = talent_api.post_circle_story(375, circle_story_data)
# print circle_story['title']

### STORIES ###
# story = talent_api.get_story(196)
# print story['title']

# stories = talent_api.get_stories([196,197])
# for story in stories:
#   print story['title']

# new_story_data = {
#   'title':'Great Story posted to Stories Resource',
#   'story':'This story was posted to the stories resource, \
#        rather than being posted through a circle',
#   'circle_id':375
# }
# new_story = talent_api.post_story(new_story_data)
# print new_story['title']

# updated_story_data = {
#   'title':'Story posted to Stories'
# }

# updated_story = talent_api.update_story(248, updated_story_data)
# print updated_story['title']

# multiple_updated_stories = talent_api.update_stories(
#    [247,246], updated_story_data)
# for updated_story in multiple_updated_stories:
#   print updated_story['title']