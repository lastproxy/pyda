import inspect
import numpy as np
import numpy.random as rn

# Import Data Assimilation class
from .data_assimilation_class import DataAssimilationClass

class DA_Init2HorizonSmoother(DataAssimilationClass):
    # This implements a data assimilation scheme in which previous
    # data are used together with the most recent data point to adjust
    # the ensemble and parametrization. The maximum number of data
    # points to use is passed as an argument when initiating this
    # class. The ensemble is then propagated from the initial
    # conditions to the horizon each assimilation step. This means
    # that instead of adjusting the current state of the ensemble at
    # each step only the initial conditions and parametrization are
    # adjusted.

    # The class is initialized by reading in the data to arrays.
    # Data = (Ndata_pts)x(measurement size) numpy array
    # DataTime = (Ndata_pts) numpy vector
    # data_noise = either scalar standard deviation of data error 
    #              or vector of standard deviations in data error 
    #              at each data point
    # data_lag = integer lag controlling the maximum past data points 
    #            used in the ensemble analysis
    # EnSize = Integer specifying size of ensemble
    # SimDim = Dimension of the simulation at each timestep
    # Horizon = Time to propagate ensemble forecast until after last data 
    #           point is assimilated
    # EnsembleClass = object of type EnsembleGeneratorClass(object) that will
    #                 be called to generate the ensemble
    # AnalysisClass = object of type AnalysisGeneratorClass(object) that will 
    #                 be called to form the analysis ensemble
    def __init__(self,DataFileName,data_noise,data_lag,Horizon,EnSize,SimDim,EnsembleClass,AnalysisClass):
        tmpData = np.loadtxt(DataFileName,delimiter='\t')
        self.DataTime = tmpData[:,0]
        self.Data = tmpData[:,1:]
        self.data_noise = data_noise
        self.data_lag = data_lag
        self.Horizon = Horizon
        self._ensemble = EnsembleClass
        self._analysis = AnalysisClass
        
        # Important sizes and dimensions
        self.EnSize = EnSize
        self.SimDim = SimDim
        self.ObsDim = self.Data.shape[1]

    # Attribute to read a parameter array to a file. There must be
    # SimDim first columns that contain values of the Ensemble State
    # variables to propagate model from.
    def param_read(self,ParamFileName):
        self.Param = np.loadtxt(ParamFileName,delimiter='\t')

    # Attribute to write a parameter array to a file. 
    def param_write(self,ParamFileName):
        np.savetxt(ParamFileName,self.Param,fmt='%5.5f',delimiter='\t')

    # Attribute to write an ensemble array to a file. The ensemble
    # array is reshaped. The ensemble time vector is the left most
    # column.
    def ensemble_write(self,Ensemble,EnsTime,EnsFileName):
        # EnsembleWrite is combined numpy array.
        Ntimestep = EnsTime.shape[0]
        EnsembleWrite = np.zeros((Ntimestep, self.SimDim*self.EnSize+1))
        EnsembleWrite[:,0] = EnsTime

        for i in range(self.EnSize):
            EnsembleWrite[:,(self.SimDim*i+1):(self.SimDim*(i+1)+1)] = Ensemble[:,i].reshape(Ntimestep,self.SimDim) 

        np.savetxt(EnsFileName,EnsembleWrite,fmt='%5.5f',delimiter=' ')

    # Defines the array of observations corresponding to a generated ensemble.
    # Observation = (measurement size)x(Ensemble Size) numpy array
    def Model2DataMap(self,Ensemble):
        # Defines the mapping of the simulation to the data. 
        raise NotImplementedError(inspect.stack()[0][3])

    # Attribute to define the data-error covariance matrix.
    def DataCovInit(self):
        # The error covariance in the data must be defined. If the
        # data being assimilated at each step is just a scalar then
        # this will just be a scalar. However, if the data being
        # assimilated at each step is a vector the covariance will be
        # a square matrix of equal size.

        # This should use self.data_noise
        # self.DataCov = 
        raise NotImplementedError(inspect.stack()[0][3])

    # Attribute that controls how the data, ensemble generation,
    # analysis, and reading/writing interact.
    # Ntimestep = number of timesteps per data point in ensemble generation
    # InitialTime = time simulation starts before first data point
    # HorizonIntervals = number of intervals from initial time to horizon
    def DArun(self,Ntimestep,InitialTime,HorizonIntervals):
        # Data Assimilation process consists of 3 steps: 
        # 1.) Ensemble generation 
        # 2.) Analysis generation 
        # 3.) Write analysis/ensemble arrays and parameter array 
        # The process is then repeated until the data is exhausted. At this 
        # point a forecast is made until the final Horizon.

        # Initialize Parametrization/Initialization
        ParamFileName = "".join(('./param.0.dat'))
        self.param_read(ParamFileName)

        # Initialize Data Covariance
        self.DataCovInit()

        for i in range(self.Data.shape[0]):
            # Grab the index of the current data point or the lag,
            # whichever is smaller. This lets us just assimilate at
            # most data_lag past data points.
            LagIndex = min(i+1,self.data_lag)

            # 1.) Ensemble Generation
            stop_time = self.DataTime[i]
            [Ensemble,EnsTime] = self._ensemble.fwd_propagate(self.Param,InitialTime,stop_time,(i+1)*Ntimestep)      

            # Generate ensemble forecast to horizon
            [Forecast,CastTime] = self._ensemble.fwd_propagate(self.Param,InitialTime,self.Horizon,Ntimestep*HorizonIntervals)

            # Write ensemble array
            EnsFileName = "".join(('./ensemble.',str(i),'.dat'))
            self.ensemble_write(Forecast,CastTime,EnsFileName)            

            # Sample ensemble at times corresponding to previous data,
            # up to lag, and collect observation at each time.
            for j in range(LagIndex):
                if (j == 0):
                    # Observation at current time
                    Observation = self.Model2DataMap(Ensemble)
                else:
                    # Observations at previous data times.
                    # Index must count back from current state by blocks of 
                    # SimDim*Ntimestep rows
                    obsindex = -self.SimDim*Ntimestep*j
                    Observation = np.vstack([self.Model2DataMap(Ensemble[:obsindex,:]),Observation])

            # Produce unperturbed data array of size (DataIndex*ObsDim)x(EnSize)
            DataArray = np.tile(np.reshape(self.Data[(i-(LagIndex-1)):(i+1),:],(LagIndex*self.ObsDim,1)),(1,self.EnSize))
            
            # Define data array used in ensemble analysis
            # DataArray = (observation size)x(ensemble size) numpy array created by Data[i,:]
            #             and DataArray            
            # Handle scalar Data Covariance and Matrix cases differently
            if (self.DataCov.ndim == 0):
                # Form data covariance matrix
                DataPerturbation = np.sqrt(self.DataCov)*rn.randn(LagIndex,self.EnSize)
            elif (self.DataCov.ndim == 2):
                # Compute SVD of Data Covariance to generate
                # noise. First DataCov must be tiled to give block
                # diagonal matrix for covariance of LagIndex block of
                # data points.
                U, s, V = np.linalg.svd(np.kron(np.diag(np.ones(LagIndex),0),self.DataCov), full_matrices=False)
                DataPerturbation = np.dot(np.dot(U,np.diag(s)),rn.randn(LagIndex*self.ObsDim,self.EnSize))
            else:
                print 'Data Covariance should be matrix or scalar', '\n'

            # Perturb data
            DataArray = DataArray + DataPerturbation

            # 2.) Analysis generation
            # Covariance should now be block diagonal
            BlockCov = np.kron(np.diag(np.ones(LagIndex),0),self.DataCov)
            [Analysis,AnalysisParam] = self._analysis.create_analysis(DataArray,BlockCov,self.Param,Ensemble,Observation)
            self.Param = AnalysisParam

            # Generate analysis forecast to horizon starting at new data point
            [Forecast,CastTime] = self._ensemble.fwd_propagate(self.Param,InitialTime,self.Horizon,Ntimestep*HorizonIntervals)

            # Write analysis to files
            AnsFileName = "".join(('./analysis.',str(i),'.dat'))
            ParamFileName = "".join(('./param.',str(i+1),'.dat'))
            self.param_write(ParamFileName)
            self.ensemble_write(Forecast,CastTime,AnsFileName)            

