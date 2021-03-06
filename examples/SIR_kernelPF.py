import inspect
import numpy as np

# Import Data Assimilation class
from pyda.assimilation.assimilation_current2horizon import DA_current2horizon

# Import Ensemble Generation class
from pyda.ensemble_generator.SIRensemble import SIRensemble

# Import analysis class
from pyda.analysis_generator.pf.pf_kernel import PF_KERNEL

class SIR_DA2horizon(DA_current2horizon):
    # Defines the array of observations corresponding to a generated ensemble.
    # Observation = (measurement size)x(Ensemble Size) numpy array
    def Model2DataMap(self,Ensemble):
        # In the SIR example we observe just the final Infected
        # proportion at the last ensemble entry.
        Observation = Ensemble[-1]
        return Observation
       
    # Attribute to define the data-error covariance matrix.
    def DataCovInit(self):
        # In the SIR example the data noise is assumed to be a scalar
        # that is constant at each observation. We use an array so
        # that the 'shape' of the scalar is understood by numpy in a
        # linear algebra sense.
        self.DataCov = np.array([[np.power(self.data_noise,2.0)]])

if __name__ == '__main__':
    # Specify ensemble generation method
    ensemble_method = SIRensemble()

    # Specify analysis method
    # Kernel perturbation standard deviation
    sigma = 0.001
    analysis_method = PF_KERNEL(sigma)

    # Input parameters to specify setup of problem
    data_noise = 0.0025
    Horizon = 200.0
    SimDim = 2
    EnSize = 25
    DataFileName = './data/SIRdata.dat'
    
    # Specify data assimilation method
    DA_method = SIR_DA2horizon(DataFileName,data_noise,Horizon,EnSize,SimDim,ensemble_method,analysis_method)

    # Read/Write initialization/parametrization file to correct place.
    DA_method.param_read('./data/SIRsampleparams.dat')
    DA_method.param_write('./param.0.dat')
    
    # Specify assimilation routine parameters
    InitialTime = 0.0
    Ntimestep = 20.0

    # Run data assimilation routine
    DA_method.DArun(Ntimestep,InitialTime)
