# coding: utf-8
import datetime

print 'create Logilab agent'
agent = create_entity('Agent', name=u'Logilab',
                      start_date=datetime.date(2000, 1, 1))
create_entity('PhoneNumber', number=u'05 62 17 16 42',
              reverse_phone_number=agent)
office = create_entity('AgentPlace', name=u'Toulouse', role=u'QG',
                       place_agent=agent)
create_entity('PostalAddress',
              street=u'1 av. de l\'Europe',
              postalcode=u'31400',
              city=u'Toulouse',
              reverse_place_address=office)
rql('SET A archival_role R WHERE R name in ("control", "deposit")')
rql('SET A agent_kind K WHERE K name "authority"')
commit()
