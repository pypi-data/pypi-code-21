__author__ = 'pvde'

from lxml import etree

import logging, json, os, traceback

from jsonschema import validate

"""
To Do:
-  Copy certificates to PMode parameters
"""


"""
Namespaces
"""

NSMAP = {'cppa': 'http://docs.oasis-open.org/ebcore/ns/cppa/v3.0',
         'ds': 'http://www.w3.org/2000/09/xmldsig#',
         'xml': 'http://www.w3.org/XML/1998/namespace' }

"""
URIs defined in ebMS3
"""

uri_oneway = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/oneWay'
uri_twoway = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/twoWay'

uri_push = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/push'
uri_pull = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/pull'

uri_sync = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/sync'
uri_pushandpush = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/pushAndPush'
uri_pushandpull = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/pushAndPull'
uri_pullandpush = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/pullAndPush'
uri_pullandpull = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/pullAndPull'

# for internal use
uri_syncresponse = 'urn:syncresponse'

"""
XPath expressions and functions that use them to search and select.
Defined here for readability.
"""

xp_partyinfo = 'child::cppa:PartyInfo[cppa:PartyName/text()="{}"]'
xp_partyinfo2 = 'child::cppa:PartyInfo'
xp_party_id = 'child::cppa:PartyId'
def party_identifier(cpa):
    return cpa.xpath(xp_party_id, namespaces=NSMAP)

xp_partyrole = 'child::cppa:PartyRole/@name'

xp_counterpartyinfo = 'child::cppa:CounterPartyInfo[cppa:PartyName/text()!="{}"]'
xp_counterpartyinfo2 = 'child::cppa:CounterPartyInfo'
xp_counterpartyrole = 'child::cppa:CounterPartyRole/@name'

xp_agreement_id = 'child::cppa:AgreementInfo/cppa:AgreementIdentifier/text()'
def agreement_identifier(cpa):
    return cpa.xpath(xp_agreement_id, namespaces=NSMAP)[0]

xp_servicespecificationL = 'child::cppa:ServiceSpecification'
xp_servicebindingL = 'child::cppa:ServiceBinding'

xp_service = 'child::cppa:Service/text()'
def service(servicebinding):
    return servicebinding.xpath(xp_service, namespaces=NSMAP)

xp_leg_one = 'child::cppa:ActionBinding[not(@replyTo)]'
def actionbinding_request(servicebinding):
    return servicebinding.xpath(xp_leg_one, namespaces=NSMAP)

xp_response_leg = 'child::cppa:ActionBinding[@replyTo="{}"]'

def actionatt(actionbinding):
    return actionbinding.get('action')

def sendorreceiveatt(actionbinding):
    return actionbinding.get('sendOrReceive')

def legid(leg):
    return leg.get('id')


xp_properties = 'child::cppa:Property'

xp_channel_id = 'child::cppa:ChannelId/text()'
def channelidtext(actionbinding):
    return actionbinding.xpath(xp_channel_id, namespaces=NSMAP)[0]

xp_payload_profile_id = 'child::cppa:PayloadProfileId/text()'
def payload_profile_id_list(actionbinding):
    return actionbinding.xpath(xp_payload_profile_id, namespaces=NSMAP)

xp_payload_profile = 'child::cppa:PayloadProfile[@id="{}"]'
def payload_profile(cpa, actionbinding):
    payload_profile_ids = payload_profile_id_list(actionbinding)
    if payload_profile_ids != []:
        payload_profile_list = cpa.xpath(xp_payload_profile.format(payload_profile_ids[0]),
                                         namespaces=NSMAP)
        if len(payload_profile_list) > 0:
            return payload_profile_list[0]
        else:
            return None
    else:
        return None

xp_payload_part = 'child::cppa:PayloadPart'

xp_payload_partname = 'child::cppa:PartName/text()'
def partname(partprofile):
    return return_if_present_else_none(partprofile,
                                       xp_payload_partname)

xp_mime_content_type = 'child::cppa:MIMEContentType/text()'
def mime_content_type(partprofile):
    return return_if_present_else_none(partprofile,
                                       xp_mime_content_type)

xp_channel = 'child::cppa:ebMS3Channel[@id="{}"]'
def channelL(cpa,id):
    return cpa.xpath(xp_channel.format(id), namespaces=NSMAP)

def channel(cpa,id):
    return cpa.xpath(xp_channel.format(id), namespaces=NSMAP)[0]

def mpc(channel):
    return channel.get('mpc')


xp_pullchannel = 'child::cppa:PullHandling/cppa:PullChannelId'
def references_pull_channel(ebms3binding):
    pullchannels = ebms3binding.xpath(xp_pullchannel, namespaces=NSMAP)
    if len(pullchannels) == 0:
        return False
    else:
        return True

xp_pullchannel_id = 'child::cppa:PullHandling/cppa:PullChannelId/text()'

xp_soapversion = 'child::cppa:SOAPVersion/text()'
def soapversion(binding):
    return binding.xpath(xp_soapversion, namespaces=NSMAP)[0]

xp_transport = 'child::*[@id="{}"]'
def transport(cpa,id):
    return cpa.xpath(xp_transport.format(id), namespaces=NSMAP)[0]

xp_endpoint = 'child::cppa:Endpoint/text()'
def endpoint(transport):
    return return_if_present_else_none(transport, xp_endpoint)

xp_errorhandling = 'child::cppa:ErrorHandling'
def errorhandling(binding):
    return return_if_present_else_none(binding, xp_errorhandling)

xp_process_error_notify_producer = 'child::cppa:ProcessErrorNotifyProducer/text()'
def process_error_notify_producer(errhandl):
    return return_if_present_else_none(errhandl,xp_process_error_notify_producer)

xp_process_error_notify_consumer = 'child::cppa:ProcessErrorNotifyConsumer/text()'
def process_error_notify_consumer(errhandl):
    return return_if_present_else_none(errhandl,xp_process_error_notify_consumer)

xp_delivery_failures_notify_producer = 'child::cppa:DeliveryFailuresNotifyProducer/text()'
def delivery_failures_notify_producer(errhandl):
    return return_if_present_else_none(errhandl,xp_delivery_failures_notify_producer)

xp_receiver_errors_report_channel_id = 'child::cppa:ReceiverErrorsReportChannelId/text()'
def receiver_errors_report_channel_id(errhandl):
    return return_if_present_else_none(errhandl,xp_receiver_errors_report_channel_id)

xp_sender_errors_report_channel_id = 'child::cppa:SenderErrorsReportChannelId/text()'
def sender_errors_report_channel_id(errhandl):
    return return_if_present_else_none(errhandl,xp_sender_errors_report_channel_id)

xp_swapackage = 'child::cppa:SOAPWithAttachmentsEnvelope[@id="{}"]'
def swapackage(cpa,id):
    return return_if_present_else_none(cpa, xp_swapackage.format(id))

xp_as4_compressed_mimepart = 'child::cppa:CompressedSimpleMIMEPart[@CompressionType="application/gzip"]'
def as4compressedmimepart(package):
    return return_if_present_else_none(package, xp_as4_compressed_mimepart)

xp_as4_compression_feature = 'child::cppa:Compression'
def as4_compression(channel):
    return return_if_present_else_none(channel, xp_as4_compression_feature)

xp_as4_compression_algorithm = 'child::cppa:Compression/cppa:CompressionAlgorithm/text()'
def as4_compression_algorithm(channel):
    return return_if_present_else_none(channel, xp_as4_compression_algorithm)



xp_receptionawareness = 'child::cppa:AS4ReceptionAwareness'
def receptionawareness(binding):
    return return_if_present_else_none(binding, xp_receptionawareness)

xp_duplicate_handling = 'child::cppa:DuplicateHandling'
def duplicate_handling(receptionawareness_config):
    return return_if_present_else_none(receptionawareness_config, xp_duplicate_handling)

xp_duplicate_elimination = 'child::cppa:DuplicateElimination/text()'
def duplicate_elimination(duplicatehandling_config):
    return return_if_present_else_none(duplicatehandling_config, xp_duplicate_elimination)

xp_persist_duration = 'child::cppa:PersistDuration/text()'
def persistduration(duplicatehandling_config):
    return return_if_present_else_none(duplicatehandling_config, xp_persist_duration)

xp_message_retry = 'child::cppa:RetryHandling'
def message_retry(receptionawareness_config):
    return return_if_present_else_none(receptionawareness_config, xp_message_retry)

xp_retries = 'child::cppa:Retries/text()'
def retries(messageretry_config):
    return return_if_present_else_none(messageretry_config, xp_retries)

xp_retryinterval = 'child::cppa:RetryInterval/text()'
def retryinterval(messageretry_config):
    return return_if_present_else_none(messageretry_config, xp_retryinterval)

xp_receipt_handling = 'child::cppa:ReceiptHandling'
def receipthandling(binding):
    return return_if_present_else_none(binding, xp_receipt_handling)

xp_receipt_format = 'child::cppa:ReceiptFormat'
def receiptformat(receiptconfig):
    return return_if_present_else_none(receiptconfig, xp_receipt_format)

xp_receiver_channel_id = 'child::cppa:ReceiptChannelId/text()'
def receiver_channel_id(receiptconfig):
    return return_if_present_else_none(receiptconfig,xp_receiver_channel_id)

xp_security = 'child::cppa:WSSecurityBinding'
def security(binding):
    return return_if_present_else_none(binding, xp_security)

xp_wssversion = 'child::cppa:WSSVersion/text()'
def wssversion(security):
    return return_if_present_else_none(security, xp_wssversion, '1.1')

xp_signature = 'child::cppa:Signature'
def signature(security):
    return return_if_present_else_none(security, xp_signature)

xp_signaturealgorithm = 'child::cppa:SignatureAlgorithm/text()'
def signaturealgorithm(signing):
    return return_if_present_else_none(signing,xp_signaturealgorithm)

xp_digestalgorithm = 'child::cppa:DigestAlgorithm/text()'
def digestalgorithm(signing):
    return return_if_present_else_none(signing,xp_digestalgorithm)

xp_signing_certificate_ref = 'cppa:SigningCertificateRef/@certId'
def signing_certificate_ref(signing):
    return return_if_present_else_none(signing, xp_signing_certificate_ref)

xp_encryption = 'child::cppa:Encryption'
def encryption(security):
    return return_if_present_else_none(security, xp_encryption)

xp_encryptionalgorithm = 'child::cppa:EncryptionAlgorithm/text()'
def encryptionalgorithm(security):
    return return_if_present_else_none(security, xp_encryptionalgorithm)

xp_encryption_certificate_ref = 'cppa:EncryptionCertificateRef/@certId'
def encryption_certificate_ref(encryptionel):
    return return_if_present_else_none(encryptionel, xp_encryption_certificate_ref)

xp_userauth = 'child::cppa:UserAuthentication'

xp_username = 'child::cppa:Username/text()'
def username(userauth):
    return return_if_present_else_none(userauth,xp_username)

xp_password = 'child::cppa:Password/text()'
def password(userauth):
    return return_if_present_else_none(userauth,xp_password)

xp_digest = 'child::cppa:Digest/text()'
def digest(userauth):
    return return_if_present_else_none(userauth,xp_digest)

xp_nonce = 'child::cppa:Nonce/text()'
def nonce(userauth):
    return return_if_present_else_none(userauth,xp_nonce)

xp_created = 'child::cppa:Created/text()'
def created(userauth):
    return return_if_present_else_none(userauth,xp_created)

xp_authorization = 'child::cppa:WSSecurityBinding[@actorOrRole="ebms"]'
def authorization(binding):
    return return_if_present_else_none(binding, xp_security)

def return_if_present_else_none(element, xpathexpr, default=None):
    exprL = element.xpath(xpathexpr, namespaces=NSMAP)
    if len(exprL) == 0:
        if default != None:
            logging.debug('No {}, returning default {}'.format(xpathexpr,default))
            return default
        else:
            return None
    else:
        return exprL[0]

def channel_transport_address(cpa, chid):
    ch = channel(cpa, chid)
    trid = ch.get('transport')
    tr = transport(cpa,trid)
    return return_if_present_else_none(tr,
                                       xp_endpoint)

"""

JSON Schema for PMODE JSON representations.
http://json-schema.org/latest/json-schema-validation.html
https://tools.ietf.org/id/draft-zyp-json-schema-04.html

Used to validate generated PMode representations.

"""

pmode_json_schema = {
	"title" : "JSON Schema for PMODE JSON representation",
    "type" : "array",
    "items" : {
        "type" : "object",
        "properties" : {
            "ID" : { "type" : "string"},
            "Agreement" : {"type" : "string"},
            "MEP" : {"type": "string"},
            "MEPBinding" : {"type": "string"},
            "Initiator" : {"$ref" : "#definitions/partytype"},
            "Responder" : {"$ref" : "#definitions/partytype"},
            "1" : {"$ref" : "#definitions/legtype"},
            "2" : {"$ref" : "#definitions/legtype"}
        },
        "additionalProperties" : False,
        "required" : ["MEP",
                      "MEPBinding",
                      "Initiator",
                      "Responder",
                      "1" ]
    },
    "definitions" : {
        "legtype" : {
            "type" : "object",
            "properties": {
                "Protocol" : {"type" : "object",
                              "properties" : {
                                  "SOAPVersion" : {
                                      "type" : "string"
                                  },
                                  "Address" : {
                                      "type" : "string"
                                  }
                              },
                              "required" : ["SOAPVersion"]
                },
                "BusinessInfo" : {"type" : "object",
                                  "properties" : {
                                      "Service" : {
                                          "type" : "string"
                                      },
                                      "Action" : {
                                          "type" : "string"
                                      },
                                      "MPC" : {
                                          "type" : "string"
                                      },
                                      "PayloadProfile" : {
                                          "type" : "array"
                                      },
                                      "Properties" : {
                                          "type" : "array"
                                      }
                                  },
                                  "additionalProperties" : False
                },
                "ErrorHandling" : {"type" : "object",
                                   "properties" : {
                                       "Report" : {
                                           "type" : "object",
                                           "properties" : {
                                               "AsResponse" : {
                                                   "type": "boolean"
                                               },
                                               "DeliveryFailuresNotifyProducer" : {
                                                  "type": "boolean"
                                               },
                                               "ProcessErrorNotifyProducer" : {
                                                   "type": "boolean"
                                               },
                                               "ProcessErrorNotifyConsumer" : {
                                                   "type": "boolean"
                                               },
                                               "ReceiverErrorsTo" : {
                                                   "type" : "string"
                                               }
                                           },
                                           "additionalProperties" : False
                                       }
                                   },
                                   "required" : ["Report"],
                                   "additionalProperties" : False
                },
                "ReceptionAwareness" : {
                    "type" : "object"
                },
                "Security" : {"type" : "object",
                              "properties" : {
                                  "WSSVersion" : {
                                      "type" : "string"
                                  },
                                  "PModeAuthorize" : {
                                      "type" : "boolean"
                                  },
                                  "X509" : {
                                      "type" : "object",
                                      "properties" : {
                                          "Sign" : {
                                              "type" : "object",
                                              "properties" : {
                                                  "Algorithm" : {
                                                      "type" : "string"
                                                  },
                                                  "HashFunction" : {
                                                      "type" : "string"
                                                  },
                                                  "Certificate" : {
                                                      "type" : "array"
                                                  }
                                              },
                                              "additionalProperties" : False
                                          },
                                          "Encryption" : {
                                              "type" : "object",
                                              "properties" : {
                                                  "Algorithm" : {
                                                      "type" : "string"
                                                  },
                                                  "Certificate" : {
                                                      "type" : "array"
                                                  }

                                              },
                                              "additionalProperties" : False
                                          },
                                      },
                                      "additionalProperties" : False
                                  },
                                  "UsernameToken" : {
                                      "type" : "object",
                                      "properties" : {
                                          "username" : {
                                              "type" : "string"
                                          },
                                          "password" : {
                                              "type" : "string"
                                          },
                                          "Digest" : {
                                              "type" : "string"
                                          },
                                          "Created" : {
                                              "type" : "string"
                                          }
                                      },
                                      "additionalProperties" : False
                                  },
                                  "SendReceipt" : {
                                      "type" : "object",
                                      "properties" : {
                                          "NonRepudiation" : {
                                              "type" : "boolean"
                                          },
                                          "ReplyPattern" : {
                                              "type" : "string"
                                          },
                                          "ReplyTo" : {
                                              "type" : "string"
                                          }

                                      },
                                      "additionalProperties" : False
                                  }
                              },
                              "required" : [# "WSSVersion",
                                            "PModeAuthorize"],
                              "additionalProperties" : False
                },
                "PayloadService" : {
                    "type" : "object",
                    "properties" : {
                        "CompressionType" : {
                            "type" : "string"
                        }
                    },
                    "additionalProperties" : False
                }
            },
            "required" : ["Protocol",
                          "BusinessInfo"],
            "additionalProperties" : False
        },
        "partytype" : {
            "type" : "object",
            "properties": {
                "Party" : {
                    #"type" : "array"
                    "$ref" : "#definitions/partyidtype"
                },
                "Role" : {
                    "type": "string"
                },
                "Authorization" : {
                    "$ref" : "#definitions/authorizationtype"
                }
            },
            "required" : ["Party", "Role"],
            "additionalProperties" : False
        },
        "partyidtype" : {
            "type" : "array",
            "item" : [
                {  "type" : "object",
                   "properties" : {
                       "ID" : {"type" : "string"},
                       "type" : {"type" : "string"}
                   },
                   "required" : "ID"
                }
            ]
        },
        "authorizationtype" : {
            "type" : "object",
            "properties" : {
                "username" : {
                    "type" : "string"
                },
                "password" : {
                    "type" : "string"
                }
            },
            "additionalProperties" : False
        }
    }
}

def validate_pmode(pmodes):
    return validate(pmodes, pmode_json_schema)


"""

"""

def load_pmodes_from_cpaf(cpafile, partyname=None, partyid=None):
    cpa = etree.parse(cpafile)
    return load_pmodes_from_cpa(cpa, partyname, partyid)

def load_pmodes_from_cpas(str, partyname=None, partyid=None):
    cpa = etree.fromstring(str)
    return load_pmodes_from_cpa(cpa, partyname, partyid)

def load_pmodes_from_cpa(cpa, partyname=None, partyid=None):
    if partyname != None:
        partyinfoL = cpa.xpath(xp_partyinfo.format(partyname),
                               namespaces=NSMAP)
        counterpartyinfoL = cpa.xpath(xp_counterpartyinfo.format(partyname),
                                      namespaces=NSMAP)

        if len(partyinfoL) + len(counterpartyinfoL) == 0:
            logging.info("Skipping CPA, not about selected party {}".format(partyname))
            return []

    else:
        pmodes = []
        partyinfoL = cpa.xpath(xp_partyinfo2,
                               namespaces=NSMAP)
        counterpartyinfoL = cpa.xpath(xp_counterpartyinfo2,
                                      namespaces=NSMAP)

        partyinfo = partyinfoL[0]
        counterpartyinfo = counterpartyinfoL[0]

        agreementref = agreement_identifier(cpa)

        for (acounter, servicespecification) in enumerate( cpa.xpath(xp_servicespecificationL,
                                                           namespaces=NSMAP),
                                                           start=1):
            process_service_specification(cpa,
                                          party_identifier(partyinfo),
                                          party_identifier(counterpartyinfo),
                                          agreementref,
                                          servicespecification,
                                          acounter,
                                          pmodes)
        try:
            validate_pmode(pmodes)
            logging.info('JSON schema validation passed')
            cpa = None
        except:
            exception = traceback.format_exc()
            logging.error("JSON schema validation failed: {}".format(exception))
            return pmodes
        else:
            return pmodes

def process_service_specification(cpa,
                                  partyidL,
                                  counterpartyidL,
                                  agreementref,
                                  servicespecification,
                                  acounter,
                                  pmodes):
    partyrole = servicespecification.xpath(xp_partyrole,
                                           namespaces=NSMAP)[0]
    counterpartyrole = servicespecification.xpath(xp_counterpartyrole,
                                                  namespaces=NSMAP)[0]
    logging.info('{} + {}'.format(partyrole, counterpartyrole))
    for (bcounter, servicebinding) in enumerate( servicespecification.xpath(xp_servicebindingL,
        namespaces=NSMAP), start=1):
        process_servicebinding(cpa,
                               partyidL,
                               counterpartyidL,
                               agreementref,
                               partyrole,
                               counterpartyrole,
                               servicebinding,
                               acounter,
                               bcounter,
                               pmodes)

def process_servicebinding(cpa,
                           partyidL,
                           counterpartyidL,
                           agreementref,
                           partyrole,
                           counterpartyrole,
                           servicebinding,
                           acounter,
                           bcounter,
                           pmodes):
    service = servicebinding.xpath(xp_service, namespaces=NSMAP)[0]
    for leg in actionbinding_request(servicebinding):
        pmode = {}
        id =  legid(leg)
        action = actionatt(leg)
        send_or_receive = sendorreceiveatt(leg)
        channelid = channelidtext(leg)
        payload_profile_config = payload_profile(cpa, leg)

        process_businessinfo('1', pmode, service, action, leg, payload_profile_config)
        process_channel(cpa, pmode, '1', channelid, agreementref)

        if is_oneway(cpa,id,servicebinding):
            pmode['MEP'] = uri_oneway
            pmode['MEPBinding'] = mep_binding(cpa, channel(cpa,channelid))

        else:
            responseleg = actionbinding_response(id,servicebinding)
            responseaction = actionatt(responseleg)
            responsechannelid = channelidtext(responseleg)
            response_payload_profile_config = payload_profile(cpa, leg)
            process_businessinfo('2', pmode, service, responseaction, responseleg,
                                 response_payload_profile_config)
            pmode['MEP'] = uri_twoway
            pmode['MEPBinding'] = two_way_mep_binding(cpa,
                                                      channel(cpa,channelid),
                                                      channel(cpa,responsechannelid),
                                                      send_or_receive)
            process_channel(cpa, pmode, '2', responsechannelid, agreementref)
            process_ebms_authorization(cpa, responsechannelid, '2', 'Responder', pmode)

        process_partyinfo(partyidL,
                          partyrole,
                          counterpartyidL,
                          counterpartyrole,
                          pmode,
                          send_or_receive)
        process_ebms_authorization(cpa, channelid, '1', 'Initiator', pmode)

        pmodes.append(pmode)
        #outfile = os.path.join(self.testdir,'pmode_{}_{}_{}.json'.format(testid,acounter,bcounter))
        #fd = open(outfile, 'wb')
        #fd.write(json.dumps(pmode, sort_keys=True, indent=4))
        #fd.close()

def actionbinding_response(id, servicebinding):
    responselegs = servicebinding.xpath(xp_response_leg.format(id),
                                        namespaces=NSMAP)
    # for now assume there is at most one response
    if len(responselegs) > 0:
        return responselegs[0]
    else:
        return None

def is_oneway(cpa,id,servicebinding):
    responselegs = servicebinding.xpath(xp_response_leg.format(id),
                                        namespaces=NSMAP)
    if len(responselegs) > 0:
        return False
    else:
        return True

def process_partyinfo(partyidL,
                      partyrole,
                      counterpartyidL,
                      counterpartyrole,
                      pmode,
                      send_or_receive):
    if send_or_receive == 'send':
        first_sender_party_idL = partyidL
        first_sender_party_role = partyrole
        first_receiver_party_idL = counterpartyidL
        first_receiver_party_role = counterpartyrole
    else:
        first_sender_party_idL = counterpartyidL
        first_sender_party_role = counterpartyrole
        first_receiver_party_idL = partyidL
        first_receiver_party_role = partyrole

    if 'Initiator' not in pmode:
        pmode['Initiator'] = {}
    if 'Responder' not in pmode:
        pmode['Responder'] = {}
    if pmode['MEP'] == uri_oneway:
        if pmode['MEPBinding'] == uri_push:
            #pmode['Initiator']['Party'] = partyidL
            process_party_identifier_and_type(pmode['Initiator'],
                                              first_sender_party_idL)
            pmode['Initiator']['Role'] = first_sender_party_role
            #pmode['Responder']['Party'] = counterpartyidL
            process_party_identifier_and_type(pmode['Responder'],
                                              first_receiver_party_idL)
            pmode['Responder']['Role'] = first_receiver_party_role
        else:
            #pmode['Initiator']['Party'] = counterpartyidL
            process_party_identifier_and_type(pmode['Initiator'],
                                              first_receiver_party_idL)
            pmode['Initiator']['Role'] = first_receiver_party_role
            #pmode['Responder']['Party'] = partyidL
            process_party_identifier_and_type(pmode['Responder'],
                                              first_sender_party_idL)
            pmode['Responder']['Role'] = first_sender_party_role
    elif pmode['MEP'] == uri_twoway:
        if pmode['MEPBinding'] in (uri_pushandpush,
            uri_pushandpull,
            uri_sync):
            #pmode['Initiator']['Party'] = partyidL
            process_party_identifier_and_type(pmode['Initiator'],
                                              first_sender_party_idL)
            pmode['Initiator']['Role'] = first_sender_party_role
            #pmode['Responder']['Party'] = counterpartyidL
            process_party_identifier_and_type(pmode['Responder'],
                                              first_receiver_party_idL)
            pmode['Responder']['Role'] = first_receiver_party_role
        else:
            #pmode['Initiator']['Party'] = counterpartyidL
            process_party_identifier_and_type(pmode['Initiator'],
                                              first_receiver_party_idL)
            pmode['Initiator']['Role'] = first_receiver_party_role
            #pmode['Responder']['Party'] = partyidL
            process_party_identifier_and_type(pmode['Responder'],
                                              first_sender_party_idL)
            pmode['Responder']['Role'] = first_sender_party_role

def process_party_identifier_and_type(parent, party_list):
    parent['Party'] = []
    for party in party_list:
        partytype = party.get('type')
        if partytype != None:
            parent['Party'].append({'ID' : party.text,
                                    'type' : partytype })
        else:
            parent['Party'].append({'ID' : party.text})




def process_businessinfo(legno, pmode, service, action, leg, payloadprofile):
    if legno not in pmode:
        pmode[legno] = {}
    leginfo = pmode[legno]
    if not 'BusinessInfo' in pmode[legno]:
        leginfo['BusinessInfo'] = {}
    businessinfo = leginfo['BusinessInfo']
    businessinfo['Service'] = service
    businessinfo['Action'] = action
    process_properties(leg, businessinfo)
    process_payload_profile(leg, businessinfo, payloadprofile)

def process_properties(leg, businessinfo):
    property_list = leg.xpath(xp_properties, namespaces=NSMAP)
    if len(property_list) > 0:
        businessinfo['Properties'] = []
        for prop in property_list:
            pname = prop.get('name')
            minoccurs = prop.get('minOccurs')
            if minoccurs > 0:
                isrequired = 'true'
            else:
                isrequired = 'false'
            businessinfo['Properties'].append( { 'name': pname,
                                                 'required' : isrequired})

def process_payload_profile(leg, businessinfo, payloadprofile):
    if payloadprofile != None:
        businessinfo['PayloadProfile'] = []
        payloadpart_config_list = businessinfo['PayloadProfile']
        for payloadpart in payloadprofile.xpath(xp_payload_part,
                                                namespaces=NSMAP):

            payloadpart_config = {}
            set_pmode_parameter_if_not_none(payloadpart_config,
                                            'PartName',
                                            partname(payloadpart))
            set_pmode_parameter_if_not_none(payloadpart_config,
                                            'MIMEContentType',
                                            mime_content_type(payloadpart))

            payloadpart_config_list.append(payloadpart_config)




def process_channel(cpa, pmode, leg, channelid, agreementref):
    channels = channelL(cpa,channelid)
    if len(channels) == 1:
        channel = channels[0]
        if include_agreementref(channel):
            pmode['Agreement'] = agreementref
        if include_pmodeid(channel):
            pmode['ID'] =  '{}_{}'.format(agreementref,channelid)

        if leg not in pmode:
            pmode[leg] = {}

        set_pmode_parameter_if_not_none(pmode[leg]['BusinessInfo'],
                                        'MPC',
                                        mpc(channel))
        process_soapversion(cpa, pmode, leg, channel)
        process_transport(cpa, pmode, leg, channel)
        process_errorhandling(cpa, pmode, leg, channel)
        process_reliability(cpa, pmode, leg, channel)
        process_payloadservice(cpa, pmode, leg, channel)
        process_reception_awareness(cpa, pmode, leg, channel)
        process_receipt_handling(cpa, pmode, leg, channel)
        process_security(cpa, pmode, leg, channel)

    else:
        logging.info('No channels for {}, not an ebMS3 binding?'.format(channelid))

def process_soapversion(cpa, pmode, leg, channel):
        if not 'Protocol' in pmode[leg]:
            pmode[leg]['Protocol'] = {}
        pmode[leg]['Protocol']['SOAPVersion'] = soapversion(channel)

def process_transport(cpa, pmode, leg, ebms3channel):
    if not 'Protocol' in pmode[leg]:
        pmode[leg]['Protocol'] = {}
    if references_pull_channel(ebms3channel):
        pullchannelid = return_if_present_else_none(ebms3channel,
                                                    xp_pullchannel_id)
        pullchannel = channel(cpa, pullchannelid)
        transportid = pullchannel.get('transport')
    else:
        transportid = ebms3channel.get('transport')
    if transportid != None:
        transportdef = transport(cpa,transportid)
        set_pmode_parameter_if_not_none(pmode[leg]['Protocol'],
                                        'Address',
                                        endpoint(transportdef))

def process_errorhandling(cpa, pmode, leg, ebmschannel):
    errhandl = errorhandling(ebmschannel)
    if errhandl != None:
        pmode[leg]['ErrorHandling'] = { 'Report' : {}}
        set_boolean_pmode_parameter_if_not_none(pmode[leg]['ErrorHandling']['Report'],
                                        'ProcessErrorNotifyProducer',
                                        process_error_notify_producer(errhandl))
        set_boolean_pmode_parameter_if_not_none(pmode[leg]['ErrorHandling']['Report'],
                                        'ProcessErrorNotifyConsumer',
                                        process_error_notify_consumer(errhandl))
        set_boolean_pmode_parameter_if_not_none(pmode[leg]['ErrorHandling']['Report'],
                                        'DeliveryFailuresNotifyProducer',
                                        delivery_failures_notify_producer(errhandl))
        process_receiver_error_channel(cpa,pmode,leg,errhandl)
        process_sender_error_channel(cpa,pmode,leg,errhandl)


def process_receiver_error_channel(cpa, pmode, leg, errhandl):
    receivererrchannelid = receiver_errors_report_channel_id(errhandl)
    if receivererrchannelid != None:
        receivererrch = channel(cpa,receivererrchannelid)
        if mep_binding(cpa, receivererrch) == uri_syncresponse:
            pmode[leg]['ErrorHandling']['Report']['AsResponse'] = True
        else:
            addr = channel_transport_address(cpa, receivererrchannelid)
            pmode[leg]['ErrorHandling']['Report']['ReceiverErrorsTo'] = addr

def process_sender_error_channel(cpa, pmode, leg, errhandl):
    sendererrchannelid = sender_errors_report_channel_id(errhandl)
    if sendererrchannelid != None:
        sendererrch = channel(cpa,sendererrchannelid)
        addr = channel_transport_address(cpa, sendererrchannelid)
        pmode[leg]['ErrorHandling']['Report']['SenderErrorsTo']


def process_reliability(cpa, pmode, leg, channel):
    pass

def process_payloadservice(cpa, pmode, leg, channel):
    """
    CPPA has allows for fine-grained modeling of message packaging,
    so the information cannot be mapped without loss of information.
    For ebMS3/AS4 PModes, we simplify the mapping by checking for presence
    of any compressed MIME parts and, if yes, setting the payload service.
    """
    if as4_compression(channel) != None:
        pmode[leg]['PayloadService'] = {
            'CompressionType' : as4_compression_algorithm(channel)
        }
    else:
        logging.info('No Compression feature used in in channel {}'.format(channel.get('id')))



    """
    package_id = channel.get('package')
    if package_id != None:
        swapackage_config = swapackage(cpa, package_id)
        if swapackage_config != None:
            as4compressedparts = as4compressedmimepart(swapackage_config)
            if as4compressedparts != None:
                pmode[leg]['PayloadService'] = {
                    'CompressionType' : 'application/gzip'
                }
            else:
                logging.info('No payloadservice in package {}'.format(package_id))

    """

def process_reception_awareness(cpa, pmode, leg, channel):
    receptionawareness_config = receptionawareness(channel)
    if receptionawareness_config != None:
        if 'ReceptionAwareness' not in pmode[leg]:
            pmode[leg]['ReceptionAwareness'] = {}
        process_duplicate_handling(cpa,pmode,leg,receptionawareness_config)
        process_message_retry(cpa,pmode,leg,receptionawareness_config)

def process_duplicate_handling(cpa, pmode, leg, receptionawareness_config):
    duplicatehandling_config = duplicate_handling(receptionawareness_config)
    if duplicatehandling_config  != None:
        pmode[leg]['ReceptionAwareness']['DuplicateDetection'] = { }
        pmode[leg]['ReceptionAwareness']['DuplicateDetection']['Parameters'] = {}
        set_pmode_parameter_if_not_none(pmode[leg]['ReceptionAwareness']['DuplicateDetection'],
                                        'DetectDuplicates',
                                        duplicate_elimination(duplicatehandling_config))
        set_pmode_parameter_if_not_none(pmode[leg]['ReceptionAwareness']['DuplicateDetection']['Parameters'],
                                        'PersistDuration',
                                        persistduration(duplicatehandling_config))

def process_message_retry(cpa, pmode, leg, receptionawareness_config):
    message_retry_config = message_retry(receptionawareness_config)
    if message_retry_config != None:
        pmode[leg]['ReceptionAwareness']['MessageRetry'] = {}
        pmode[leg]['ReceptionAwareness']['MessageRetry']['Retry'] = True
        pmode[leg]['ReceptionAwareness']['MessageRetry']['Parameters'] = {}
        set_pmode_parameter_if_not_none(pmode[leg]['ReceptionAwareness']['MessageRetry']['Parameters'],
                                        'Retries',
                                        retries(message_retry_config))
        set_pmode_parameter_if_not_none(pmode[leg]['ReceptionAwareness']['MessageRetry']['Parameters'],
                                        'RetryInterval',
                                        retryinterval(message_retry_config))


def process_receipt_handling(cpa, pmode, leg, channel):
    receipt_handling_config = receipthandling(channel)
    if receipt_handling_config != None:
        if not 'Security' in pmode[leg]:
            pmode[leg]['Security'] = {}
        pmode[leg]['Security']['SendReceipt'] = {}
        process_receipt_format(cpa, pmode, leg, receipt_handling_config)
        process_receiver_channel(cpa, pmode, leg, receipt_handling_config)

def process_receipt_format(cpa, pmode, leg, receipt_handling_config):
    format = receiptformat(receipt_handling_config)
    context = pmode[leg]['Security']['SendReceipt']
    if format == 'NonRepudiationInformation':
        context['NonRepudiation'] = True
    else:
        # Note:  absence of element defaults to reception awareness
        context['NonRepudiation'] = False

def process_receiver_channel(cpa, pmode, leg, receipt_handling_config):
    recvchannelid = receiver_channel_id(receipt_handling_config)
    if recvchannelid != None:
        recvchannel = channel(cpa,recvchannelid)
        if mep_binding(cpa, recvchannel) == uri_syncresponse:
            pmode[leg]['Security']['SendReceipt']['ReplyPattern'] = 'response'
        else:
            addr = channel_transport_address(cpa, recvchannelid)
            pmode[leg]['Security']['SendReceipt']['ReplyPattern'] = 'callback'
            pmode[leg]['Security']['SendReceipt']['ReplyTo'] = addr


def process_security(cpa, pmode, leg, channel):
    security_config= security(channel)
    if security_config != None:
        pmode[leg]['Security'] = {}
        set_pmode_parameter_if_not_none(pmode[leg]['Security'],
                                        'WSSVersion',
                                        wssversion(security_config))
        process_signature(cpa, pmode, leg, security_config)
        process_encryption(cpa, pmode, leg, security_config)
        process_usernametoken(cpa, pmode, leg, security_config)

def retrieve_certificate(cpa, certid):
    certtext = cpa.xpath('//cppa:Certificate[@id="{}"]//ds:X509Certificate/text()'.format(certid),
                     namespaces=NSMAP)
    return certtext

def process_signature(cpa, pmode, leg, security_config):
    xmlsignature = return_if_present_else_none(security_config,xp_signature)
    if xmlsignature != None:
        if 'X509' not in pmode[leg]['Security']:
            pmode[leg]['Security']['X509'] = {}
        pmode[leg]['Security']['X509']['Sign'] = {}
        set_pmode_parameter_if_not_none(pmode[leg]['Security']['X509']['Sign'],
                                        'Algorithm',
                                        signaturealgorithm(xmlsignature))
        set_pmode_parameter_if_not_none(pmode[leg]['Security']['X509']['Sign'],
                                        'HashFunction',
                                        digestalgorithm(xmlsignature))
        signing_cert = signing_certificate_ref(xmlsignature)
        if signing_cert != None:
            pmode[leg]['Security']['X509']['Sign']['Certificate'] = retrieve_certificate(cpa,
                                                                                         signing_cert)

def process_encryption(cpa, pmode,leg,security_config):
    xmlencryption = return_if_present_else_none(security_config,xp_encryption)
    if xmlencryption != None:
        if 'X509' not in pmode[leg]['Security']:
            pmode[leg]['Security']['X509'] = {}
        pmode[leg]['Security']['X509']['Encryption'] = {}
        set_pmode_parameter_if_not_none(pmode[leg]['Security']['X509']['Encryption'],
                                        'Algorithm',
                                        encryptionalgorithm(xmlencryption))
        encryption_cert = encryption_certificate_ref(xmlencryption)
        if encryption_cert != None:
            pmode[leg]['Security']['X509']['Encryption']['Certificate'] = retrieve_certificate(cpa,
                                                                                         encryption_cert)


def process_usernametoken(cpa, pmode,leg,wssec):
    userauth = return_if_present_else_none(wssec,xp_userauth)
    if userauth != None:
        if 'UsernameToken' not in pmode[leg]['Security']:
            pmode[leg]['Security']['UsernameToken'] = {}
        process_usernametoken_params(pmode[leg]['Security']['UsernameToken'],
                                     userauth)

def process_ebms_authorization(cpa, channelid, legno, bindingrole, pmode):
    userchannel = channel(cpa, channelid)
    if 'Security' not in pmode[legno]:
        pmode[legno]['Security'] = {}
    if references_pull_channel(userchannel):
        pullchannelid = return_if_present_else_none(userchannel,
                                                    xp_pullchannel_id)
        pullchannel = channel(cpa, pullchannelid)
        authorization_config = authorization(pullchannel)
        if authorization_config != None:
            userauth = return_if_present_else_none(authorization_config, xp_userauth)
            if userauth != None:
                if not bindingrole in pmode:
                    pmode[bindingrole]={}
                pmode[bindingrole]['Authorization'] = {}
                process_usernametoken_params(pmode[bindingrole]['Authorization'], userauth)
                pmode[legno]['Security']['PModeAuthorize'] = True
        else:
            pmode[legno]['Security']['PModeAuthorize'] = False
    else:
        pmode[legno]['Security']['PModeAuthorize'] = False



def process_usernametoken_params(context, userauth):
    set_pmode_parameter_if_not_none(context,
                                    'username',
                                    username(userauth))
    set_pmode_parameter_if_not_none(context,
                                    'password',
                                    password(userauth))
    set_pmode_parameter_if_not_none(context,
                                    'Digest',
                                    digest(userauth))
    set_pmode_parameter_if_not_none(context,
                                    'Created',
                                    created(userauth))


def set_pmode_parameter_if_not_none(context, param, value, default=None):
    if value != None:
        context[param] = value
    elif default != None:
        context[param] = default

def set_boolean_pmode_parameter_if_not_none(context, param, value, default=None):
    if value != None:
        if value in ['true', '1', 'True']:
            context[param] = True
        else:
            context[param] = True
    elif default != None:
        context[param] = default

def mep_binding(cpa, ebms3channel):
    asresponse = ebms3channel.get('asResponse')
    # to be enhanced for other situations e.g. multi-hop
    if true(asresponse):
        if references_pull_channel(ebms3channel):
            return uri_pull
        else:
            # this will only occur in Two Way MEP
            return uri_syncresponse
    else:
        return uri_push


def two_way_mep_binding(cpa, firstchannel, secondchannel, direction):
    if direction == 'send':
        requestbinding = mep_binding(cpa, firstchannel)
        responsebinding = mep_binding(cpa, secondchannel)
    else:
        requestbinding = mep_binding(cpa, secondchannel)
        responsebinding = mep_binding(cpa, firstchannel)
    if requestbinding == uri_push:
        if responsebinding == uri_push:
            return uri_pushandpush
        elif responsebinding == uri_pull:
            return uri_pushandpull
        elif responsebinding == uri_syncresponse:
            return uri_sync
        else:
            raise Exception('Failed to determine MEP Binding')
    elif requestbinding == uri_pull:
        if responsebinding == uri_push:
            return uri_pullandpush
        elif responsebinding == uri_pull:
            return uri_pullandpull
        else:
            raise Exception('Failed to determine MEP Binding')
    elif requestbinding == uri_syncresponse:
        if responsebinding == uri_push:
            return uri_sync
        else:
            raise Exception('Failed to determine MEP Binding')



def include_agreementref(ebms3channel):
    value = ebms3channel.get('includeAgreementRef')
    if true(value) or none(value):
        return True

def include_pmodeid(ebms3channel):
    if include_agreementref(ebms3channel):
        value = ebms3channel.get('includePmode')
        if true(value):
            return True
        else:
            return False
    else:
        return False

def true(value):
    if value == 'true' or value == '1':
        return True
    else:
        return False

def true_or_none(value):
    if true(value) or none(value):
        return True
    else:
        return False

def false(value):
    return not(true(value))

def false_or_none(value):
    if false(value) or none(value):
        return True
    else:
        return False

def none(value):
    if value == None:
        return True
    else:
        return False