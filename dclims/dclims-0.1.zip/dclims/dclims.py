'''
This is the preliminary work for an API wrapper.  This API wrapper will call the
D.C. LIMS API system, streamlining the calls.

Dependencies: Requests;
API help from DC Council Website:http://lims.dccouncil.us/api/Help


|Signature-------------------------------------------|
|Written for DC Policy Center by Michael Watson; 2017|
|www.DCPolicyCenter.org / DC-Policy-Center.github.io |
|github:M-Watson & MW-DC-Policy-Center               |
|----------------------------------------------------|
'''

#Requests is used for all of the API calls.
import requests, json

def topLevelTest(toPrint):
    print(toPrint)
    return(toPrint)

class get:
#*****************************************************************************#
    def latestLaws(rowLimit,**kwargs):
        '''GETs latest legislation that have been made into official laws'''

        q = {}
        verbose = kwargs.get('verbose',False)
        head = {'content-type':'application/json'}


        website = 'http://lims.dccouncil.us/api/v1/Legislation/LatestLaws?%s'%(rowLimit)
        if(verbose == True):print('GET- Latest Laws')
        response = requests.get(website,data=json.dumps(q),headers=head)
        if(verbose == True):print('RESPONSE: '+ str(response))
        return(response)


        
#*****************************************************************************#
    def mostVisited(rowLimit,**kwargs):
        '''GETs most popular legislation. Count determines the number of
        legislation to be returned'''

        verbose = kwargs.get('verbose',False)
        q = {}
        head = {'content-type':'application/json'}


        website = 'http://lims.dccouncil.us/api/v1/Legislation/MostVisited?%s'%(rowLimit)
        if(verbose == True):print('GET- Most Visited')
        response = requests.get(website,data=json.dumps(q),headers=head)
        print('RESPONSE: '+ str(response))
        return(response)



#*****************************************************************************#
    def details(legislationNumber,**kwargs):
        '''When passed a complete Legislation number e.g., B21-1023, PR20-0300,
        returns the details of the Legislation. Legislation details has
        basic Legislation information, Hearing, Committee Markup,
        Voting Summary, Mayor Review, Congress Review, Council Review,
        Other Documents, and Linked Legislation'''

        verbose = kwargs.get('verbose',False)
        q = {}
        head = {'content-type':'application/json'}
        website = 'http://lims.dccouncil.us/api/v1/Legislation/Details?legislationNumber=%s'%(legislationNumber)
        if(verbose == True):print('GET- Details')
        response = requests.get(website,data=json.dumps(q),headers=head)
        if(verbose == True):print('RESPONSE: '+ str(response))
        return(response)



#*****************************************************************************#
    def requestOf(councilPeriod,**kwargs):
        '''Returns all the RequestOf entries by Council period'''

        verbose = kwargs.get('verbose',False)
        q = {}
        head = {'content-type':'application/json'}
        website = 'http://lims.dccouncil.us/api/v1/Legislation/RequestOf?councilPeriod=%s'%(councilPeriod)
        if(verbose == True):print('GET- Details')
        response = requests.get(website,data=json.dumps(q),headers=head)
        if(verbose == True):print('RESPONSE: '+ str(response))
        return(response)



#*****************************************************************************#
class post:



#*****************************************************************************#
    def search(**kwargs):
        '''Basic search on keyword and category.
        The results include all Legislation that have matched the search criteria.
        RowLimit limits the number of results.
        OffSet defines the starting record in the result record set.'''

        verbose = kwargs.get('verbose',False)
        try: kwargs.pop('verbose')
        except: pass
        rowLimit = kwargs.get('rowLimit')
        try: kwargs.pop('rowLimit')
        except: pass
        offSet = kwargs.get('offSet')
        try: kwargs.pop('offSet')
        except: pass
        #Building Request
        q = kwargs
        head = {'content-type':'application/json'}     #Requests JSON response
        #Building API call from request building
        website = 'http://lims.dccouncil.us/api/v1/Legislation/Search?%s'%(rowLimit)
        #Sending POST request
        response = requests.post(website,data=json.dumps(q),headers=head)
        if(verbose == True):print('RESPONSE: '+ str(response))
        return(response)



#*****************************************************************************#
    def advancedSearch(**kwargs):
        '''Advanced search into Legislation. Expects a LegislationSearchCriteria in the
        request body. The search criteria can include various combinations to search for
        Legislation that match. RowLimit limits the number of results. Offset defines
        the starting record in the result recordset.'''



        verbose = kwargs.get('verbose',False)
        try: kwargs.pop('verbose')
        except: pass
        rowLimit = kwargs.get('rowLimit')
        try: kwargs.pop('rowLimit')
        except: pass
        offSet = kwargs.get('offSet')
        try: kwargs.pop('offSet')
        except: pass


        q = kwargs
        head = {'content-type':'application/json'}     #Requests JSON response
        #Building API call from request building
        website = 'http://lims.dccouncil.us/api/v1/Legislation/AdvancedSearch?%s'%(rowLimit)
        if(verbose == True):print('WEBSITE: '+ str(website))
        #Sending POST request
        response = requests.post(website,data=json.dumps(q),headers=head)
        if(verbose == True):print('RESPONSE: '+ str(response))
        return(response)



#*****************************************************************************#
    def votingSearch(**kwargs):
        '''Voting search by using VoteSearchCriteria
        http://lims.dccouncil.us/api/Help/Api/POST-v1-Voting-Search_rowLimit_offSet'''

        verbose = kwargs.get('verbose',False)
        try: kwargs.pop('verbose')
        except: pass
        rowLimit = kwargs.get('rowLimit')
        try: kwargs.pop('rowLimit')
        except: pass
        offSet = kwargs.get('offSet')
        try: kwargs.pop('offSet')
        except: pass

        q = kwargs
        head = {'content-type':'application/json'}     #Requests JSON response
        #Building API call from request building
        website = 'http://lims.dccouncil.us/api/v1/Voting/Search?%s'%(rowLimit)
        #Sending POST request
        response = requests.post(website,data=json.dumps(q),headers=head)
        if(verbose == True):print('RESPONSE: '+ str(response))
        return(response)



#*****************************************************************************#
class masters:



#*****************************************************************************#
        def limsLookUps(**kwargs):
            verbose = kwargs.get('verbose',False)
            q = {}
            head = {'content-type':'application/json'}
            website = 'http://lims.dccouncil.us/api/v1/masters/LIMSLookUps'
            if(verbose == True):print('GET- Details')
            response = requests.get(website,data=json.dumps(q),headers=head)
            if(verbose == True):print('RESPONSE: '+ str(response))
            return(response)



#*****************************************************************************#
        def members(councilPeriod,**kwargs):
            verbose = kwargs.get('verbose',False)
            q = {}
            head = {'content-type':'application/json'}
            website = 'http://lims.dccouncil.us/api/v1/masters/Members?councilPeriod=%s'%(councilPeriod)
            if(verbose == True):print('GET- Details')
            response = requests.get(website,data=json.dumps(q),headers=head)
            if(verbose == True):print('RESPONSE: '+ str(response))
            return(response)



#*****************************************************************************#
        def committees(councilPeriod,**kwargs):
            verbose = kwargs.get('verbose',False)
            q = {}
            head = {'content-type':'application/json'}
            website = 'http://lims.dccouncil.us/api/v1/masters/Committees?councilPeriod=%s'%(councilPeriod)
            if(verbose == True):print('GET- Details')
            response = requests.get(website,data=json.dumps(q),headers=head)
            if(verbose == True):print('RESPONSE: '+ str(response))
            return(response)



#*****************************************************************************#
        def hearingTypes(councipPeriod,**kwargs):
            verbose = kwargs.get('verbose',False)
            q = {}
            head = {'content-type':'application/json'}
            website = 'http://lims.dccouncil.us/api/v1/masters/HearingTypes?councilPeriod=%s'%(councilPeriod)
            if(verbose == True):print('GET- Details')
            response = requests.get(website,data=json.dumps(q),headers=head)
            if(verbose == True):print('RESPONSE: '+ str(response))
            return(response)



#*****************************************************************************#
        def councilPeriods(councilPeriods,**kwargs):
            verbose = kwargs.get('verbose',False)
            q = {}
            head = {'content-type':'application/json'}
            website = 'http://lims.dccouncil.us/api/v1/masters/CouncilPeriods?councilPeriod=%s'%(councilPeriod)
            if(verbose == True):print('GET- Details')
            response = requests.get(website,data=json.dumps(q),headers=head)
            if(verbose == True):print('RESPONSE: '+ str(response))
            return(response)



#*****************************************************************************#
        def legislationCategories(**kwargs):
            verbose = kwargs.get('verbose',False)
            q = {}
            head = {'content-type':'application/json'}
            website = 'http://lims.dccouncil.us/api/v1/masters/LegislationCategories'
            if(verbose == True):print('GET- Details')
            response = requests.get(website,data=json.dumps(q),headers=head)
            if(verbose == True):print('RESPONSE: '+ str(response))
            return(response)


#*****************************************************************************#
        def legislationTypes(**kwargs):
            ''' List of all Legislation tpyes (legislation sub categories).
            Returns Id, Name, Legislation Prefix, Legislation Category
            and Sort Order of each Legislation type '''
            verbose = kwargs.get('verbose',False)
            q = {}
            head = {'content-type':'application/json'}
            website = 'http://lims.dccouncil.us/api/v1/masters/LegislationTypes'
            if(verbose == True):print('GET- Details')
            response = requests.get(website,data=json.dumps(q),headers=head)
            if(verbose == True):print('RESPONSE: '+ str(response))
            return(response)




#*****************************************************************************#
        def placeRead(**kwargs):
            ''' List of all places where a Legislation could be introduced. Returns Id, Name, and Sort Order of each place read '''
            verbose = kwargs.get('verbose',False)
            q = {}
            head = {'content-type':'application/json'}
            website = 'http://lims.dccouncil.us/api/v1/masters/placeRead'
            if(verbose == True):print('GET- Details')
            response = requests.get(website,data=json.dumps(q),headers=head)
            if(verbose == True):print('RESPONSE: '+ str(response))
            return(response)


#*****************************************************************************#
        def places(**kwargs):

            verbose = kwargs.get('verbose',False)
            q = {}
            head = {'content-type':'application/json'}
            website = 'http://lims.dccouncil.us/api/v1/masters/Places'
            if(verbose == True):print('GET- Details')
            response = requests.get(website,data=json.dumps(q),headers=head)
            if(verbose == True):print('RESPONSE: '+ str(response))
            return(response)



#*****************************************************************************#
        def voteResponses(**kwargs):
            ''' List of all vote responses. returns Id, Name, and Sort Order of each vote response '''
            verbose = kwargs.get('verbose',False)
            q = {}
            head = {'content-type':'application/json'}
            website = 'http://lims.dccouncil.us/api/v1/masters/VoteResponses'
            if(verbose == True):print('GET- Details')
            response = requests.get(website,data=json.dumps(q),headers=head)
            if(verbose == True):print('RESPONSE: '+ str(response))
            return(response)


#*****************************************************************************#
        def voteTypes(**kwargs):
            ''' Get all Vote by Types '''
            verbose = kwargs.get('verbose',False)
            q = {}
            head = {'content-type':'application/json'}
            website = 'http://lims.dccouncil.us/api/v1/masters/VoteTypes'
            if(verbose == True):print('GET- Details')
            response = requests.get(website,data=json.dumps(q),headers=head)
            if(verbose == True):print('RESPONSE: '+ str(response))
            return(response)



#*****************************************************************************#
        def legislationStatus(**kwargs):
            ''' Get all Legislation Status '''
            verbose = kwargs.get('verbose',False)
            q = {}
            head = {'content-type':'application/json'}
            website = 'http://lims.dccouncil.us/api/v1/masters/LegislationStatus'
            if(verbose == True):print('GET- Details')
            response = requests.get(website,data=json.dumps(q),headers=head)
            if(verbose == True):print('RESPONSE: '+ str(response))
            return(response)

'''  *****************        APPENDICES   *************************
                    I.Changes to look into or needed
1) Should I use a python core HTML request system
2) Continue adding the rest of the API basic calls
        - Finished adding in masters calls now (4/12)
        - Masters calls untested/unverified (4/12)
        - Finish documenting Masters
        - TODO remove this comment by May 18th, 2017 after testing all basic API calls
3) Decide on how to handle query statements, maybe through kwargs
         - I am using kwargs with the postAdvancedSearch and it seems to work well
         - Downside, the user needs to input all of the options in one dictionary
          * Example:
                 query = {'rowLimit':100,'verbose':True,'StartDate':'01/01/2017'}
            Call this query using:
                 dcLegislation.post.advancedSearc(**query)
            Note the ** to make your dictionary a kwarg or key word argument
            This search will use advanced search to find legislation since 01/01/2017
            while printing out in verbose mode and limiting to 100 rows


                    II.
                    III.
                    IV.

*****************        END APPENDICES   *************************'''
