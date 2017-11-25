
import lxml.etree, logging

_NSMAP = { 'cppa': 'http://docs.oasis-open.org/ebcore/ns/cppa/v3.0',
           'pycppa3' : 'https://pypi.python.org/pypi/cppa3'}

_NSMAP2 = { 'cppa': 'http://docs.oasis-open.org/ebcore/ns/cppa/v3.0' }



def cppa(el):
    return '{{{}}}{}'.format(_NSMAP['cppa'], el)

cppa3_content_model = {

    cppa('NamedChannel') : [cppa('Description'),
                            cppa('ChannelProfile'),
                            cppa('MaxSize'),
                            cppa('ChannelName'),
                            cppa('SigningCertificateRef'),
                            cppa('SigningCertificateRequired'),
                            cppa('SigningTrustAnchorSetRef'),
                            cppa('SigningCertificatePolicySetRef'),
                            cppa('EncryptionCertificateRef'),
                            cppa('EncryptionCertificateRequired'),
                            cppa('EncryptionCertificateRefType'),
                            cppa('EncryptionTrustAnchorSetRef'),
                            cppa('EncryptionCertificatePolicySetRef'),
                            cppa('Param')],

    cppa('AS1Channel') : [cppa('Description'),
                          cppa('ChannelProfile'),
                          cppa('MaxSize'),
                          cppa('Signature'),
                          cppa('Encryption'),
                          cppa('ErrorHandling'),
                          cppa('ReceiptHandling'),
                          cppa('Compression')],

    cppa('AS2Channel') : [cppa('Description'),
                          cppa('ChannelProfile'),
                          cppa('MaxSize'),
                          cppa('Signature'),
                          cppa('Encryption'),
                          cppa('ErrorHandling'),
                          cppa('ReceiptHandling'),
                          cppa('Compression')],

    cppa('AS3Channel') : [cppa('Description'),
                          cppa('ChannelProfile'),
                          cppa('MaxSize'),
                          cppa('Signature'),
                          cppa('Encryption'),
                          cppa('ErrorHandling'),
                          cppa('ReceiptHandling'),
                          cppa('Compression')],

    cppa('ebMS2Channel') : [cppa('Description'),
                            cppa('ChannelProfile'),
                            cppa('MaxSize'),
                            cppa('ErrorHandling'),
                            cppa('ReceiptHandling'),
                            cppa('ebMS2ReliableMessaging'),
                            cppa('ebMS2SecurityBinding') ],

    cppa('ebMS2SecurityBinding') : [cppa('Signature'),
                                    cppa('Encryption')],

    cppa('ebMS2ReliableMessaging') : [ cppa('DuplicateHandling'),
                                       cppa('RetryHandling') ],

    cppa('ebMS3Channel') : [cppa('Description'),
                            cppa('ChannelProfile'),
                            cppa('SOAPVersion'),
                            cppa('FaultHandling'),
                            cppa('Addressing'),
                            cppa('WSSecurityBinding'),
                            cppa('AS4ReceptionAwareness'),
                            cppa('ErrorHandling'),
                            cppa('ReceiptHandling'),
                            cppa('PullHandling'),
                            cppa('Compression'),
                            cppa('Bundling'),
                            cppa('Splitting'),
                            cppa('AlternateChannel')],

    cppa('AMQPChannel') : [cppa('Description'),
                           cppa('AMQPSecurity')],

    cppa('PullHandling') : [cppa('PullChannelId')],

    cppa('Compression') : [cppa('CompressionAlgorithm')],

    cppa('WSSecurityBinding') : [ cppa('WSSVersion'),
                                  cppa('SecurityPolicy'),
                                  cppa('SAMLKeyConfirmedSubjectToken'),
                                  cppa('Signature'),
                                  cppa('Encryption'),
                                  cppa('UserAuthentication')],

    cppa('UserAuthentication') : [ cppa('Username'),
                                   cppa('Password'),
                                   cppa('Digest'),
                                   cppa('Nonce'),
                                   cppa('Created')],

    cppa('AS4ReceptionAwareness') : [ cppa('DuplicateHandling'),
                                      cppa('RetryHandling') ],


    cppa('DuplicateHandling') : [ cppa('DuplicateElimination'),
                                  cppa('PersistDuration') ],

    cppa('RetryHandling') : [ cppa('Retries'),
                              cppa('ExponentialBackoff'),
                              cppa('RetryInterval')],

    cppa('Signature') : [ cppa('SignatureFormat'),
                          cppa('SignatureAlgorithm'),
                          cppa('DigestAlgorithm'),
                          cppa('CanonicalizationMethod'),
                          cppa('SignatureTransformation'),
                          cppa('SigningCertificateRef'),
                          cppa('SigningCertificateRequired'),
                          cppa('SigningCertificateRefType'),
                          cppa('SigningTrustAnchorSetRef'),
                          cppa('SigningCertificatePolicySetRef'),
                          cppa('SAMLTokenRef'),
                          cppa('SignElements'),
                          cppa('SignAttachments'),
                          cppa('SignExternalPayloads')],

    cppa('Encryption') : [ cppa('KeyEncryption'),

                           cppa('EncryptionAlgorithm'),
                           cppa('EncryptElements'),
                           cppa('EncryptAttachments'),
                           cppa('EncryptExternalPayloads'),

                           cppa('EncryptionCertificateRef'),
                           cppa('EncryptionCertificateRequired'),
                           cppa('EncryptionCertificateRefType'),
                           cppa('EncryptionTrustAnchorSetRef'),
                           cppa('EncryptionCertificatePolicySetRef')],

    cppa('KeyEncryption') : [ cppa('EncryptionAlgorithm'),
                              cppa('MaskGenerationFunction'),
                              cppa('DigestAlgorithm')],


    #cppa('DataEncryption') : [ cppa('EncryptionAlgorithm'),
    #                           cppa('EncryptElements'),
    #                           cppa('EncryptAttachments'),
    #                           cppa('EncryptExternalPayloads')],

    cppa('ErrorHandling') : [ cppa('DeliveryFailuresNotifyProducer'),
                              cppa('ProcessErrorNotifyConsumer'),
                              cppa('ProcessErrorNotifyProducer'),
                              cppa('SenderErrorsReportChannelId'),
                              cppa('ReceiverErrorsReportChannelId')],

    cppa('ReceiptHandling') : [ cppa('ReceiptFormat'),
                                cppa('ReceiptChannelId')],

    cppa('HTTPTransport') : [ cppa('Description'),
                              cppa('ClientIPv4'),
                              cppa('ClientIPv6'),
                              cppa('ServerIPv4'),
                              cppa('ServerIPv6'),
                              cppa('Endpoint'),
                              cppa('TransportLayerSecurity'),
                              cppa('UserAuthentication'),
                              cppa('TransportRestart'),
                              cppa('HTTPVersion'),
                              cppa('ChunkedTransferCoding'),
                              cppa('ContentCoding'),
                              cppa('Pipelining')],

    cppa('TransportLayerSecurity') : [ cppa('TLSProtocol'),
                                       cppa('CipherSuite'),
                                       cppa('ClientCertificateRef'),
                                       cppa('ClientCertificateRequired'),
                                       cppa('ClientTrustAnchorSetRef'),
                                       cppa('ClientCertificatePolicySetRef'),
                                       cppa('ServerCertificateRef'),
                                       cppa('ServerCertificateRequired'),
                                       cppa('ServerTrustAnchorSetRef'),
                                       cppa('ServerCertificatePolicySetRef')],

    cppa('TransportRestart') : [ cppa('RestartProtocol'),
                                 cppa('RestartInterval')]

}

def ensure_ordered(tree):
    if tree.tag is lxml.etree.Comment:
        return tree
    newtree = lxml.etree.Element(tree.tag,
                                 nsmap=_NSMAP2)
    for att in tree.attrib:
        newtree.set(att, tree.get(att))
    newtree.text = tree.text
    if tree.tag in cppa3_content_model:
        for child_tag in cppa3_content_model[tree.tag]:
            for child in tree:
                if child.tag == child_tag:
                    newtree.append(ensure_ordered(child))
        for child in tree:
            if child.tag is not lxml.etree.Comment:
                if child.tag not in cppa3_content_model[tree.tag]:
                    raise Exception(
                        'Child {} not in content model for {} !'.format(child.tag,
                                                                        tree.tag)
                    )
    else:
        if len(tree):
            for child in list(tree):
                try:
                    newtree.append(ensure_ordered(child))
                except:
                    logging.info('Exception for tree: {}'.format(str(child)))
                    raise
    return newtree

