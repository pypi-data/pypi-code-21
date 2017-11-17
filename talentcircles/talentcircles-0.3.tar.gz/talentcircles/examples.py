# examples.py
#
# Usage examples for the TalentCircles Python SDK
#
# @author tom@talentcircles.com
# @copyright Copyrights (c) 2017 TalentCircles Inc.

# Import the class
from talentcircles import TalentCircles

# Your network's App ID
app_id = "romeo-5931c22e4190b"

# Used to authenticate with the API
api_key = "Y1IgDgriOjAo5hKMzZ0RxC"

# The specific TalentCircles network's url
domain = "mytalentmall.talentcircles.vm"

# Initialize the object
talent_api = TalentCircles(domain, app_id, api_key)

# Functions by resource:

### JOBS ###
job = talent_api.get_job(7480159)
print(job['job_title'])

# two_jobs = talent_api.get_jobs([7480159, 8773787])
# for job in two_jobs:
# 	print job['job_title']

# new_job_data = {
# 	'job_title':'Extremely Excellent Accountant',
# 	'available_on':'November 6, 2017',
# 	'category_id': 1,
# 	'zipcode':94066,
# 	'description':'We need someone to teach our other accountants.',
# }
# new_job = talent_api.create_job(new_job_data)
# print(new_job['job_title'])

# update_job_data = {
# 	'job_title':'Very Competent Accountant II'
# }
# updated_job = talent_api.update_job(8698598, update_job_data)
# print(updated_job['job_title'])

# job_candidates = talent_api.get_job_candidates(7480159);
# for candidate in job_candidates:
# 	print candidate['user']['formatted_name'] + " - Score: " + str(candidate['score'])

# similar_jobs = talent_api.get_similar_jobs(7480159);
# for job in similar_jobs:
# 	print job['job']['job_title'] + " - Score: " + str(job['score'])

# searched_jobs = talent_api.search_jobs({"commitment_levels":1})
# for job in searched_jobs:
#     print job['job']['job_title'] + " - Score: " + str(job['score'])

### USERS ###
# user = talent_api.get_user(12770410)
# print user['firstname']

# two_users = talent_api.get_users([12770410, 12769405])
# for user in two_users:
# 	print user['firstname']

# user_matching_jobs = talent_api.get_user_matching_jobs(12770260)
# for job in user_matching_jobs:
# 	print(job['job']['job_title'] + " - Score: " + str(job['score']))

# similar_users = talent_api.get_similar_users(12770260)
# for user in similar_users:
# 	print user['user']['formatted_name'] + " - Score: " + str(user['score'])

# user_data = {
# 	'firstname':'Tim',
# 	'lastname':'Wallace',
# 	'email':'twallace@synaptic.net',
# 	'password':'secretpass',
# 	'zipcode':78704
# }
# new_user = talent_api.create_user(user_data)
# print new_user['formatted_name']

# update_user_data = {
# 	'lastname':'Flynt'
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
# 	print circle['circle_name']

# circle_stories = talent_api.get_circle_stories(375)
# for story in circle_stories:
# 	print story['title']

# cricle_members = talent_api.get_cricle_members(375)
# for user in cricle_members:
# 	print user['formatted_name']

# new_circle_data = {
# 	'circle_name':'Fantastically Great Circle'
# }
# new_circle = talent_api.create_circle(new_circle_data)
# print new_circle['circle_name']

# update_circle_data = {
# 	'circle_name':'Awesomely Fantastically Great Circle'
# }
# updated_circle = talent_api.update_circle(385, update_circle_data)
# print updated_circle['circle_name']

# circle_jobs = talent_api.get_circle_jobs(375)
# for job in circle_jobs:
# 	print job['job_title']

# circle_story_data = {
# 	'title':'Great Story',
# 	'story':'This story is great.'
# }
# circle_story = talent_api.post_circle_story(375, circle_story_data)
# print circle_story['title']

### STORIES ###
# story = talent_api.get_story(196)
# print story['title']

# stories = talent_api.get_stories([196,197])
# for story in stories:
# 	print story['title']

# new_story_data = {
# 	'title':'Great Story posted to Stories Resource',
# 	'story':'This story was posted to the stories resource, rather than being posted through a circle',
# 	'circle_id':375
# }
# new_story = talent_api.post_story(new_story_data)
# print new_story['title']

# updated_story_data = {
# 	'title':'Story posted to Stories'
# }

# updated_story = talent_api.update_story(248, updated_story_data)
# print updated_story['title']

# multiple_updated_stories = talent_api.update_stories([247,246], updated_story_data)
# for updated_story in multiple_updated_stories:
# 	print updated_story['title']