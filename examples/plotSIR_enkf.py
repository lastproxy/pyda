###############################################################################
###############################################################################
#   Copyright 2014 Kyle S. Hickmann and
#                  The Administrators of the Tulane Educational Fund
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
###############################################################################
###############################################################################

# Simple plot generation of enKF data assimilation on the SIR epidemic
# model.

# Import Data Assimilation utilities
import pyda.utilities.AssimilationVis as DA_vis

# Dimension of simulation output
SimDim = 2
# Filename of data assimilated
DataFileName = "./data/SIRdata.dat"
# Filename of Ensemble to plot
EnsembleFileName = "./ensemble.2.dat"
# Filename of Analysis Ensemble to plot
AnalysisFileName = "./analysis.2.dat"

# Call pyda.utilities function
DA_vis.ode_DA_vis2(SimDim,DataFileName,EnsembleFileName,AnalysisFileName)