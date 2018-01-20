# Tutorial: "A tour of Data Assimilation methods"
# Model: Lorenz-63
# DA Methods: Nudging, 3D-Var, 4D-Var, Particle Filter, EnKF, Hybrid
import numpy as np
from class_lorenz63 import lorenz63
from class_state_vector import state_vector
from class_obs_data import obs_data
from class_da_system import da_system

#-----------------------------------------------------------------------
# Exercises:
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# Tutorial 2:
#
# Exercises:
# (1) Generate an analysis using nudging
# (2) Generate an analysis using Optimal Interpolation (OI)
# (3) Generate an analysis using 3D-Var
#
# Additional exercises:
# (1) Test different estimates of the background error covariance matrix
# (2) Test different estimates of the observation error
# (3) Adjust parameters to 'break' the methods:
#  (a) Increase observational noise (by increasing sigma_r)
#  (b) Observe fewer dimensions (e.g. only x and y, only y, only z) by modifying the H operator
#  (c) Add a bias to the model
#  (d) Use a fundamentally different model as 'truth' (i.e. introduce a systematic model error)
#  (e) Draw observational errors from a skewed distribution
#-----------------------------------------------------------------------

# Step 1:
#

#-----------------------------------------------------------------------
# Read the L63 nature run
#-----------------------------------------------------------------------
infile = 'x_nature.pkl'
sv = state_vector()
sv = sv.load(infile)
x_nature = sv.getTrajectory()

#-----------------------------------------------------------------------
# Initialize the timesteps
#-----------------------------------------------------------------------
t_nature = sv.getTimes()
ainc_step = 1  # (how frequently to perform an analysis)
dtau = (t_nature[ainc_step] - t_nature[0])
tsteps=10 * ainc_step
dt = dtau/tsteps
maxit,xdim = np.shape(x_nature)

#-----------------------------------------------------------------------
# Read the L63 observations
#-----------------------------------------------------------------------
infile = 'y_obs.pkl'
obs = obs_data()
obs = obs.load(infile)

#-----------------------------------------------------------------------
# Try reducing the observed dimensions
#-----------------------------------------------------------------------
#obs.reduceDim([0])  # x only
#obs.reduceDim([1])  # y only
#obs.reduceDim([2])  # z only
#obs.reduceDim([0,1])  # x and y only
#obs.reduceDim([1,2])  # y and z only
#obs.reduceDim([0,2])  # z and x only

y_obs = obs.getVal()
y_pts = obs.getPos()
y_err = obs.getErr()
print('y_obs = ')
print(y_obs[0,:])
print('y_pts = ')
print(y_pts[0,:])

#-----------------------------------------------------------------------
# Initialize the model
#-----------------------------------------------------------------------
l63 = lorenz63()

#-----------------------------------------------------------------------
# Initialize the da system
#-----------------------------------------------------------------------
#das = da_system(state_vector=sv,obs_data=obs)
das = da_system()
I = np.identity(xdim)
sigma_b = 0.9
das.setB(sigma_b**2*I)
print('B = ')
print(das.B)
sigma_r = 1.0
das.setR(sigma_r**2*I)
print('R = ')
print(das.R)
das.setH(I)
print('H = ')
print(das.H)

#-----------------------------------------------------------------------
# Choose DA method:
#-----------------------------------------------------------------------

#-----------
# Session 0:
# Test basic functionality
#-----------
#method='skip'

#-----------
# Session 2:
# 3D methods
#-----------
# Nudging
#method='nudging'
# OI
method='OI'
# 3D-Var
#method='3DVar'

das.setMethod(method)

#-----------------------------------------------------------------------
# Test assimilation methods:
#-----------------------------------------------------------------------
#
xa = sv.x0
xa_history = np.zeros_like(x_nature)
KH_history = []
for i in range(0,maxit,ainc_step):
 
  #----------------------------------------------
  # Run forecast model for this analysis cycle:
  #----------------------------------------------
  t = np.arange(t_nature[i],t_nature[i]+dtau+dt,dt)
# print('t = ', t)
  # Run the model
  xf_4D =  l63.run(xa,t) 
  # Get last timestep of the forecast
  xf = xf_4D[-1,:] 

  #----------------------------------------------
  # Get the observations for this analysis cycle
  #----------------------------------------------
  yo = y_obs[i,:]
  yp = y_pts[i,:]

  #----------------------------------------------
  # Update the error covariances
  #----------------------------------------------
  das.setB(sigma_b**2*I)
  das.setR(sigma_r**2*I)
  das.setH(I)
  das.reduceYdim(yp)
 
  #----------------------------------------------
  # Compute analysis
  #----------------------------------------------
  xa, KH = das.compute_analysis(xf,yo)
# print('xa = ')
# print(xa)
# print('KH = ')
# print(KH)

  # Archive the analysis
  xa_history[i,:] = xa

  # Archive the KH matrix
  KH_history.append(KH)
 
#--------------------------------------------------------------------------------
# Fill in unobserved dimensions
#--------------------------------------------------------------------------------
fillValue=0.0
obs.fillDim(fillValue)
das.setObsData(obs)

sv.setTrajectory(xa_history)
das.setStateVector(sv)

outfile='x_analysis_'+method+'.pkl'
das.save(outfile)
