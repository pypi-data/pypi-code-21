"""
Reproduces Figure 4 from:

Golowasch, J., Casey, M., Abbott, L. F., & Marder, E. (1999).
Network Stability from Activity-Dependent Regulation of Neuronal Conductances.
Neural Computation, 11(5), 1079-1096.
https://doi.org/10.1162/089976699300016359
"""
import matplotlib.pyplot as plt

from brian2.only import *
import brian2.numpy_ as np

set_device('cpp_standalone', build_on_run=False, directory=None)

defaultclock.dt = 0.01*ms

### Class-independent constants
# Reversal potentials
E_L = -68*mV
E_Na = 20*mV
E_K = -80*mV
E_Ca = 120*mV
E_proc = -10*mV

# Capacitance
C_s = 0.2*nF
C_a = 0.02*nF

# maximal conductances
g_E = 10*nS
g_La = 7.5*nS
g_Na = 300*nS
g_Kd = 4*uS
G_Ca = 0.2*uS
G_K = 16*uS

# time constants (independent of V)
tau_h_Ca = 150*ms
tau_m_A = 0.1*ms
tau_h_A = 50*ms
tau_m_proc = 6*ms
tau_m_Na = 0.025*ms
tau_z = 5*second

# Synapses
s_fast = 0.2/mV
V_fast = -50*mV
s_slow = 1/mV
V_slow = -55*mV
E_syn = -75*mV
k_1 = 1/ms

### Neuronal equations
eqs = '''
# somatic compartment
dV_s/dt = (-I_syn - I_L - I_Ca - I_K - I_A - I_proc - g_E*(V_s - V_a))/C_s : volt

I_L = g_Ls*(V_s - E_L) : amp
I_K = g_K*m_K**4*(V_s - E_K) : amp
I_A = g_A*m_A**3*h_A*(V_s - E_K) : amp
I_proc = g_proc*m_proc*(V_s - E_proc) : amp

I_syn = I_fast + I_slow: amp
I_fast : amp
I_slow : amp

I_Ca = g_Ca*m_Ca**3*h_Ca*(V_s - E_Ca)            : amp
dm_Ca/dt = (m_Ca_inf - m_Ca)/tau_m_Ca            : 1
m_Ca_inf = 1/(1 + exp(0.205/mV*(-61.2*mV - V_s))): 1
tau_m_Ca = 30*ms -5*ms/(1 + exp(0.2/mV*(-65*mV - V_s))) : second
dh_Ca/dt = (h_Ca_inf - h_Ca)/tau_h_Ca            : 1
h_Ca_inf = 1/(1 + exp(-0.15/mV*(-75*mV - V_s)))  : 1

dm_K/dt = (m_K_inf - m_K)/tau_m_K                : 1
m_K_inf = 1/(1 + exp(0.1/mV*(-35*mV - V_s)))     : 1
tau_m_K = 2*ms + 55*ms/(1 + exp(-0.125/mV*(-54*mV - V_s))) : second

dm_A/dt = (m_A_inf - m_A)/tau_m_A                : 1
m_A_inf = 1/(1 + exp(0.2/mV*(-60*mV - V_s)))     : 1
dh_A/dt = (h_A_inf - h_A)/tau_h_A                : 1
h_A_inf = 1/(1 + exp(-0.18/mV*(-68*mV - V_s)))   : 1

dm_proc/dt = (m_proc_inf - m_proc)/tau_m_proc    : 1
m_proc_inf = 1/(1 + exp(0.2/mV*(-55*mV - V_s)))  : 1

# axonal compartment
dV_a/dt = (-g_La*(V_a - E_L) - g_Na*m_Na**3*h_Na*(V_a - E_Na)
           -g_Kd*m_Kd**4*(V_a - E_K) - g_E*(V_a - V_s))/C_a : volt

dm_Na/dt = (m_Na_inf - m_Na)/tau_m_Na            : 1
m_Na_inf = 1/(1 + exp(0.1/mV*(-42.5*mV - V_a)))  : 1
dh_Na/dt = (h_Na_inf - h_Na)/tau_h_Na            : 1
h_Na_inf = 1/(1 + exp(-0.13/mV*(-50*mV - V_a)))  : 1
tau_h_Na = 10*ms/(1 + exp(0.12/mV*(-77*mV - V_a))) : second

dm_Kd/dt = (m_Kd_inf - m_Kd)/tau_m_Kd            : 1
m_Kd_inf = 1/(1 + exp(0.2/mV*(-41*mV - V_a)))    : 1
tau_m_Kd = 12.2*ms + 10.5*ms/(1 + exp(-0.05/mV*(58*mV - V_a))) : second

# class-specific fixed maximal conductances
g_Ls   : siemens (constant)
g_A    : siemens (constant)
g_proc : siemens (constant)

# Adaptive conductances
g_Ca = G_Ca/2*(1 + tanh(z)) : siemens
g_K = G_K/2*(1 - tanh(z))   : siemens
I_diff = (I_target + I_Ca) : amp
dz/dt = tanh(I_diff/nA)/tau_z : 1
I_target : amp (constant)

# neuron class
label : integer (constant)
'''
ABPD, LP, PY = 0, 1, 2

circuit = NeuronGroup(3, eqs, method='rk2')
circuit.z = [-1, 0, 1]
# class-specific constants
circuit.label = [ABPD, LP, PY]
circuit.I_target = [0.4, 0.3, 0.5]*nA
circuit.g_Ls = [30, 25, 15]*nS
circuit.g_A = [450, 100, 250]*nS
circuit.g_proc = [6, 8, 0]*nS

# Initial conditions
circuit.V_s = E_L
circuit.V_a = E_L
circuit.m_Ca = 'm_Ca_inf'
circuit.h_Ca = 'h_Ca_inf'
circuit.m_K = 'm_K_inf'
circuit.m_A = 'm_A_inf'
circuit.h_A = 'h_A_inf'
circuit.m_proc = 'm_proc_inf'
circuit.m_Na = 'm_Na_inf'
circuit.h_Na = 'h_Na_inf'
circuit.m_Kd = 'm_Kd_inf'

eqs_fast = '''
g_fast : siemens (constant)
I_fast_post = g_fast*(V_s_post - E_syn)/(1+exp(s_fast*(V_fast-V_s_pre))) : amp (summed)
'''
fast_synapses = Synapses(circuit, circuit, model=eqs_fast)
fast_synapses.connect('label_pre != label_post and not (label_pre == PY and label_post == ABPD)')
fast_synapses.g_fast['label_pre == ABPD and label_post == LP'] = 0.015*uS
fast_synapses.g_fast['label_pre == ABPD and label_post == PY'] = 0.005*uS
fast_synapses.g_fast['label_pre == LP and label_post == ABPD'] = 0.01*uS
fast_synapses.g_fast['label_pre == LP and label_post == PY']   = 0.02*uS
fast_synapses.g_fast['label_pre == PY and label_post == LP']   = 0.005*uS

eqs_slow = '''
k_2 : 1/second (constant)
g_slow : siemens (constant)
I_slow_post = g_slow*m_slow*(V_s_post-E_syn) : amp (summed)
dm_slow/dt = k_1*(1-m_slow)/(1+exp(s_slow*(V_slow-V_s_pre))) - k_2*m_slow : 1 (clock-driven)
'''
slow_synapses = Synapses(circuit, circuit, model=eqs_slow, method='linear')
slow_synapses.connect('label_pre == ABPD and label_post != ABPD')
slow_synapses.g_slow['label_post == LP'] = 0.025*uS
slow_synapses.k_2['label_post == LP']    = 0.03/ms
slow_synapses.g_slow['label_post == PY'] = 0.015*uS
slow_synapses.k_2['label_post == PY']    = 0.008/ms

mon = StateMonitor(circuit, 'V_s', record=True, dt=1*ms)

slow_synapses.active = False
fast_synapses.active = False
mon.active = False

run(40*second, report='text')
mon.active = True
run(3*second, report='text')  # Figure 3A
slow_synapses.active = True
fast_synapses.active = True
run(3*second, report='text')  # Figure 3B
mon.active = False
run(40*second, report='text')
mon.active = True
run(3*second, report='text')  # Figure 3C
slow_synapses.active = False
fast_synapses.active = False
run(3*second, report='text')

device.build()

labels = ['AB/PD', 'LP', 'PY']
fig, axes = plt.subplots(2, 2, sharey='all')
for idx in range(3):
    axes[0, 0].plot(mon.t/second, mon.V_s[idx])
    axes[0, 1].plot(mon.t / second, mon.V_s[idx])
    axes[1, 0].plot(mon.t / second, mon.V_s[idx])
    axes[1, 1].plot(mon.t / second, mon.V_s[idx])
axes[0, 0].set(xlim=(40, 43))
axes[0, 1].set(xlim=(43, 46))
axes[1, 0].set(xlim=(86, 89))
axes[1, 1].set(xlim=(89, 92))
plt.show()


# from brian2tools import plot_state
# rows = int(np.sqrt(len(mon.record_variables)))
# cols = int(np.ceil(1.0*len(mon.record_variables)/rows))
# print len(mon.record_variables), rows, cols
# fig, axes = plt.subplots(rows, cols, sharex=True)
# for index, var in enumerate(mon.record_variables):
#     print index, var
#     row = index // cols
#     col = index % cols
#     plot_state(mon.t, getattr(mon[0], var), var_name=var, axes=axes[row, col])
# plt.show()
