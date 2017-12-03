"""
conn.py 

Contains Cell related classes 

Contributors: salvadordura@gmail.com
"""

from neuron import h # Import NEURON
import framework as f


###############################################################################
#
# CONNECTION CLASS
#
###############################################################################


class CellConn(object):
    ''' Connection (unitary connection) between 2 cells, which may include multiple synapses'''
                  
    def __init__(self, params):
        self.preGid = params.pop('preGid')  # global cell id 
        self.postGid = params.pop('postGid')  # dictionary of cell tags/attributes 
        self.synConns = []

        self.createSynConns(params)  # create cell 

    def createSynConns(self, params):
    	postCell = f.net.cells[f.net.gid2lid[self.postGid]]  # get postsynaptic cell object

        if self.preGid == self.postGid:
            print 'Error: attempted to create self-connection on cell gid=%d, section=%s '%(self.postGid, params['sec'])
            return  # if self-connection return

        if not params['sec'] or not params['sec'] in postCell.secs:  # if no section specified or section specified doesnt exist
            if 'soma' in postCell.secs:  
                params['sec'] = 'soma'  # use 'soma' if exists
            elif postCell.secs:  
                params['sec'] = postCell.secs.keys()[0]  # if no 'soma', use first sectiona available
                for secName, secParams in postCell.secs.iteritems():              # replace with first section that includes synaptic mechanism
                    if 'synMechs' in secParams:
                        if secParams['synMechs']:
                            params['sec'] = secName
                            break
            else:  
                print 'Error: no Section available on cell gid=%d to add connection'%(self.postGid)
                return  # if no Sections available print error and exit
        sec = postCell.secs[params['sec']]

        weightIndex = 0  # set default weight matrix index

        pointp = None
        if 'pointps' in postCell.secs[params['sec']]:  #  check if point processes with 'vref' (artificial cell)
            for pointpName, pointpParams in postCell.secs[params['sec']]['pointps'].iteritems():
                if 'vref' in pointpParams:  # if includes vref param means doesn't use Section v or synaptic mechanisms
                    pointp = pointpName
                    if 'synList' in pointpParams:
                        if params['synMech'] in pointpParams['synList']: 
                            weightIndex = pointpParams['synList'].index(params['synMech'])  # udpate weight index based pointp synList


        if not pointp: # not a point process
            if 'synMechs' in sec: # section has synaptic mechanisms
                if params['synMech']: # desired synaptic mechanism specified in conn params
                    if params['synMech'] not in sec['synMechs']:  # if exact name of desired synaptic mechanism doesn't exist
                        synIndex = [0]  # by default use syn 0
                        synIndex.extend([i for i,syn in enumerate(sec['synMechs']) if params['synMech'] in syn])  # check if contained in any of the synaptic mechanism names
                        params['synMech'] = sec['synMechs'].keys()[synIndex[-1]]
                else:  # if no synaptic mechanism specified            
                    params['synMech'] = sec['synMechs'].keys()[0]  # use first synaptic mechanism available in section
            else: # if still no synaptic mechanism  
                print 'Error: no Synapse or point process available on cell gid=%d, section=%s to add stim'%(self.postGid, params['sec'])
                return  # if no Synapse available print error and exit

        if not params['threshold']:
            params['threshold'] = 10.0

        self.synConns.append(params)
        if pointp:
            postTarget = sec['pointps'][pointp]['hPointp'] #  local point neuron
        else:
            postTarget= sec['synMechs'][params['synMech']]['hSyn'] # local synaptic mechanism
        netcon = f.pc.gid_connect(self.preGid, postTarget) # create Netcon between global gid and target
        netcon.weight[weightIndex] = f.net.params['scaleConnWeight']*params['weight']  # set Netcon weight
        netcon.delay = params['delay']  # set Netcon delay
        netcon.threshold = params['threshold']  # set Netcon delay
        self.synConns[-1]['hNetcon'] = netcon  # add netcon object to dict in conns list
        if f.cfg['verbose']: print('Created connection preGid=%d, postGid=%d, sec=%s, syn=%s, weight=%.4g, delay=%.1f'%
            (self.preGid, self.postGid, params['sec'], params['synMech'], f.net.params['scaleConnWeight']*params['weight'], params['delay']))

        plasticity = params.get('plast')
        if plasticity:  # add plasticity
            try:
                plastSection = h.Section()
                plastMech = getattr(h, plasticity['mech'], None)(0, sec=plastSection)  # create plasticity mechanism (eg. h.STDP)
                for plastParamName,plastParamValue in plasticity['params'].iteritems():  # add params of the plasticity mechanism
                    setattr(plastMech, plastParamName, plastParamValue)
                if plasticity['mech'] == 'STDP':  # specific implementation steps required for the STDP mech
                    precon = f.pc.gid_connect(self.preGid, plastMech); precon.weight[0] = 1 # Send presynaptic spikes to the STDP adjuster
                    pstcon = f.pc.gid_connect(self.postGid, plastMech); pstcon.weight[0] = -1 # Send postsynaptic spikes to the STDP adjuster
                    h.setpointer(netcon._ref_weight[weightIndex], 'synweight', plastMech) # Associate the STDP adjuster with this weight
                    self.synConns[-1]['hPlastSection'] = plastSection
                    self.synConns[-1]['hSTDP']         = plastMech
                    self.synConns[-1]['hSTDPprecon']   = precon
                    self.synConns[-1]['hSTDPpstcon']   = pstcon
                    self.synConns[-1]['STDPdata']      = {'preGid': self.preGid, 'postGid': self.postGid, 'receptor': weightIndex} # Not used; FYI only; store here just so it's all in one place
                    if f.cfg['verbose']: print('  Added STDP plasticity to synaptic mechanism')
            except:
                print 'Error: exception when adding plasticity using %s mechanism' % (plasticity['mech'])
