# This file contains cosmological constants, physical constants and conversion factors

import numpy as np

# Various useful physical constants
abu_he = 0.074
abu_h = 1.0-abu_he
c = 3.0e5 # km/s
pc=  3.086e18 #1 pc in cm
Mpc = 1e6*pc
G_grav = 6.6732e-8
m_p = 1.672661e-24 #g
mean_molecular = abu_h+4.0*abu_he
abu_he_mass = 0.2486 
abu_h_mass = 1.0-abu_he_mass
def set_abundance_helium(value):
	global abu_he_mass, abu_h_mass
	abu_he_mass = value
	abu_h_mass = 1.0-abu_he_mass

mean_molecular = 1.0/(1.0-abu_he_mass)
solar_masses_per_gram = 5.02785431e-34
kms = 1.e5 #1 km/s in cm/s

# Cosmology
h = 0.7
Omega0 = 0.27
OmegaB = 0.044
lam = 1.0-Omega0

# Set cosmological parameter
def set_hubble_h(value): 
	global h, H0
	h  = value 
	H0 = 100.0*h

def set_omega_matter(value): 
	global Omega0, lam
	Omega0 = value
	lam = 1.0-Omega0

def set_omega_baryon(value): 
	global OmegaB
	OmegaB = value 

def set_omega_lambda(value): 
	global lam
	lam = value 

# Cosmology
H0 = 100.0*h
H0cgs = H0*1e5/Mpc
rho_crit_0 = 3.0*H0cgs*H0cgs/(8.0*np.pi*G_grav)
q0 = 0.5*Omega0- lam
rho_matter = rho_crit_0*Omega0  
Tcmb0=2.725

# Redshift dependent Hubble parameter, km/s/Mpc
Hz = lambda z: H0*np.sqrt(Omega0*(1.0+z)**3.+lam) 

# 21 cm stuff
A10 = 2.85e-15
nu0 = 1.42e3
Tstar = 0.068
lambda0 = c*1.0e5/(nu0*1.0e6) # cm
num_h_0=(1-abu_he_mass)*OmegaB*rho_crit_0/m_p
# meandt = 2.9*0.043/0.04
meandt = 3.0*lambda0**3/(32.*np.pi)*A10*Tstar*num_h_0/(H0cgs/h)*1000.
