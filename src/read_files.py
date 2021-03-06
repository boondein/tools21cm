import numpy as np
#import c2raytools as c2t
import glob
from xfrac_file import XfracFile
import helper_functions, density_file, vel_file, lightcone
import temperature as tm
import sys

def _load_binary_data(filename, dtype=np.float32): 
	""" 
	We assume that the data was written 
	with write_binary_data() (little endian). 
	""" 
	f = open(filename, "rb") 
	data = f.read() 
	f.close() 
	_data = np.fromstring(data, dtype) 
	if sys.byteorder == 'big':
		_data = _data.byteswap()
	return _data 

def read_21cmfast_files(filename):
	"""
	Parameter
	---------
	filename: Give the filename of the 21cmFAST output files.

	Return
	---------
	Numpy array
	"""
	bla = _load_binary_data(filename)
	dim = round(bla.size**0.333333)
	return bla.reshape(dim,dim,dim)

def read_c2ray_files(filename, file_type='xfrac', density_file=None):
	"""
	Parameter
	---------
	filename    : Give the filename of the C2Ray output files.
	file_type   : The file of file being read has to be mentioned. The options are 
	               'xfrac', 'dens', 'vel'. (Default: 'xfrac')
	density_file: This is necessary if file_type=='vel'. (Default: None)

	Return
	---------
	Numpy array
	"""
	assert file_type in ['xfrac', 'dens', 'vel']
	if file_type=='xfrac': out = XfracFile(filename).xi
	elif file_type=='dens': 
		dens, dtype = helper_functions.get_data_and_type(filename)
		out = dens.astype(np.float64)
	elif file_type=='vel':
		assert density_file is not None
		dfile = density_file.DensityFile(density_file)
		vel_file = vel_file.VelocityFile(filename)
		out = vel_file.get_kms_from_density(dfile)
	return out

def read_grizzly_files(filename):
	"""
	Parameter
	---------
	filename: Give the filename of the GRIZZLY xfrac files.

	Return
	---------
	Numpy array
	"""
	return XfracFile(filename).xi


def coeval_21cm_c2ray(xfrac_dir, dens_dir, z, interpolation='linear', mean_subtract=False):
	"""
	xfrac_dir     : Give the path that contains the xfrac-files.
	dens_dir      : Give the path that contains the density-files.
	z	      : Redshift.
	interpolation : This is used when the xfrac cube at that redshift is not available.
	"""
	xfrac = coeval_xfrac_c2ray(xfrac_dir, z, interpolation=interpolation)
	dens  = coeval_dens_c2ray(dens_dir, z)
	dt    = tm.calc_dt(xfrac, dens, z=z)
	if mean_subtract: 
		for i in xrange(dt.shape[2]): dt[:,:,i] -= dt[:,:,i].mean()
		print "Mean is subtracted along third axis."
	return dt


def coeval_xfrac_c2ray(xfrac_dir, z, interpolation='linear'):
	"""
	xfrac_dir     : Give the path that contains the xfrac-files.
	z	      : Redshift.
	interpolation : This is used when the coveal cube at that redshift is not available.
	"""
	if not interpolation in ['linear']: #, 'step', 'sigmoid', 'step_cell'
		raise ValueError('Unknown interpolation type: %s' % interpolation)
	xfrac_files = glob.glob(xfrac_dir + '/xfrac3d_*.bin')
	xfrac_zs = None
	xfrac_zs = lightcone._get_file_redshifts(xfrac_zs, xfrac_files)
	if z in xfrac_zs:
		xfrac = XfracFile(xfrac_files[np.argwhere(z==xfrac_zs)]).xi
	else:
		z_l = xfrac_zs[xfrac_zs<z].max()
		z_h = xfrac_zs[xfrac_zs>z].min()
		xfrac_l = XfracFile(xfrac_files[xfrac_zs[xfrac_zs<z].argmax()]).xi
		xfrac_h = XfracFile(xfrac_files[xfrac_zs[xfrac_zs>z].argmin()]).xi
		xfrac = xfrac_h + (xfrac_l-xfrac_h)*(z-z_h)/(z_l-z_h)
		print "The xfrac cube has been interpolated using", interpolation, "interpolation."
		print "CAUTION: This data should be used with care."
	return xfrac

def coeval_dens_c2ray(dens_dir, z):
	"""
	dens_dir      : Give the path that contains the density-files.
	z	      : Redshift.
	"""
	dens_files  = glob.glob(dens_dir + '/*n_all.dat')
	dens_zs  = None
	dens_zs  = lightcone._get_file_redshifts(dens_zs, dens_files)
	if z in dens_zs:
		dens, dtype = helper_functions.get_data_and_type(dens_files[np.argwhere(z==dens_zs)])
	else:
		#z_l = dens_zs[dens_zs<z].max()
		z_h = dens_zs[dens_zs>z].min()
		#dens_l,dtype = helper_functions.get_data_and_type(dens_files[dens_zs[dens_zs<z].argmax()])
		dens_h, dtype = helper_functions.get_data_and_type(dens_files[dens_zs[dens_zs>z].argmin()])
		#dens = dens_h + (dens_l-dens_h)*(z-z_h)/(z_l-z_h)
		dens = dens_h*(1+z_h)**3/(1+z)**3
		#print "The density cube has been interpolated using", interpolation, "interpolation."
		print "The density has been scaled from the density at the previous time."
	return dens.astype(np.float64)

def subtract_mean_channelwise(dt, axis=-1):
	"""
	dt  : Brightness temperature whose channel-wise should be subtracted.
	axis: Frequency axis (Defualt:-1).
	"""
	assert dt.ndim == 3
	if axis != -1 or axis != 2: dt = np.swapaxes(dt, axis, 2)
	for i in xrange(dt.shape[2]): dt[:,:,i] -= dt[:,:,i].mean()
	if axis != -1 or axis != 2: dt = np.swapaxes(dt, axis, 2)
	return dt
	
