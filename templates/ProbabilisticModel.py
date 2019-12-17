# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
#
# GRIPY - Geofísica de Reservatório Interativa em Python
#
# ----------------------------------------------------------------------------
#
# Author: Fernando Vizeu Santos
# Company: Grupo de Inferência de Reservatório
#
# ----------------------------------------------------------------------------
#
# LICENSE
#
# ----------------------------------------------------------------------------

"""

"""

from __future__ import division

import numpy as np
from scipy import stats
from sklearn.mixture import GMM
from collections import defaultdict

_MIN_STD = 1.0E-4


class ProbabilisticModel(object):
    """
    Interface class for all probabilistic models.
    
    Depending on the model, it is easier to implement `prob` or `logprob`.
    It is convinient to implement only one of them call it on the other
    combined with the appropriated `numpy` function (`log` or `exp`).
    
    For discrete models, the methods `prob` and `logprob` must return the
    probability mass. In the case of continuous models, they must return the
    probability density.
    """

    def fit(self, data):
        """
        Fit the parameters of the model to the `data`.
        
        Parameters
        ----------
        data : numpy.ndarray
            The data that will be used to fit the model.
        """
        pass

    def logprob(self, x):
        """
        The log-probability of `x`.
        
        Parameters
        ----------
        x : float or numpy.ndarray
            The position where the log-probability will be calculated.
        
        Returns
        -------
        float
            The log-probability of the model in the given position.
        
        Notes
        -----
        The model must be fitted before this method is called.
        """
        pass

    def prob(self, x):
        """
        The probability of `x`.
        
        Parameters
        ----------
        x : float or numpy.ndarray
            The position where the log-probability will be calculated.
        
        Returns
        -------
        float
            The probability of the model in the given position.
        
        Notes
        -----
        The model must be fitted before this method is called.
        """
        pass

    def sample(self, n):
        """
        Get `n` samples of the model.
        
        Parameters
        ----------
        n : int
            The number of samples.
        
        Returns
        -------
        numpy.ndarray
            Random samples generetad from the model.
        
        Notes
        -----
        The model must be fitted before this method is called.
        """
        pass


class Discrete1DPM(ProbabilisticModel):
    """
    Base class for discrete one-dimensional probabilistic models.
    
    Attributes
    ----------
    probabilities : dict
        A dictionary whose keys are the values of the random variable and
        values are their respectives probabilities.
    """

    def __init__(self):
        self.probabilities = defaultdict(float)

    def logprob(self, x):
        return np.log(self.prob(x))

    def prob(self, x):
        return np.vectorize(self.probabilities.__getitem__)(x)  # TODO: alguma forma melhor de fazer isso?

    def sample(self, n=1):
        return np.random.choice(self.probabilities.keys(), size=n, p=self.probabilities.values())


class UniformD1DPM(Discrete1DPM):
    """
    A uniform discrete probabilistic model.
    
    The possible values (i.e. the values with non-zero probabilities) are
    the ones used to fit the model, or in other words the `data` passed to
    the `fit` method. Note that the number of times a value appears on `data`
    makes no difference.
    
    Examples
    -------
    >>> data = np.array([1, 1, 1, 2, 2, 3, 5, 6])
    >>> model = UniformD1DPM()
    >>> model.fit(data)
    >>> model.prob(1)
    0.2 # or 1 in 5 (the number of unique values in `data`)
    >>> model.prob(1.1)
    0.0
    >>> model.prob(2)
    0.2
    >>> model.prob(4)
    0.0
    >>> model.prob(8)
    0.0
    """

    def fit(self, data):
        self.probabilities.clear()
        uniquedata = np.unique(data)
        for ud in uniquedata:
            self.probabilities[ud] = 1.0 / len(uniquedata)


class ProportionalD1DPM(Discrete1DPM):
    """
    Discrete probabilistic model with probabilities proportional to the number
    of occurrences of an event.
    
    The possible values (i.e. the values with non-zero probabilities) are
    the ones used to fit the model, or in other words the `data` passed to
    the `fit` method. The probability of a given value occurring under this
    model is proportional to the number of times it appears on `data`.
    
    Examples
    -------
    >>> data = np.array([1, 1, 1, 2, 2, 3, 5, 6])
    >>> model = ProportionalD1DPM()
    >>> model.fit(data)
    >>> model.prob(1)
    0.375 # or 3 in 8 (the number of occurances divided by `data` size)
    >>> model.prob(1.1)
    0.0
    >>> model.prob(2)
    0.25
    >>> model.prob(4)
    0.0
    >>> model.prob(8)
    0.0
    """

    def fit(self, data):
        uniquedata = np.unique(data)
        self.probabilities = {}
        for ud in uniquedata:
            self.probabilities[ud] = np.sum(data == ud) / len(data)


class FixedD1DPM(Discrete1DPM):
    """
    Discrete probabilistic model with pre-defined probabilities.
    
    Parameters
    ----------
    probabilities : dict
        A dictionary whose keys are the values of the random variable and
        values are their respectives probabilities.
    
    Examples
    --------
    >>> probabilities = {1: 0.5, 2: 0.3, 3: 0.2}
    >>> model = FixedD1DPM(probabilities)
    >>> model.prob(1)
    0.5
    >>> model.prob(1.1)
    0.0
    >>> model.prob(2)
    0.3
    >>> model.prob(4)
    0.0
    >>> model.prob(8)
    0.0
    """

    def __init__(self, probabilities):
        super(FixedD1DPM, self).__init__()
        self.probabilities.update(probabilities)


class Normal1DPM(ProbabilisticModel):
    """
    Probabilistic model for one-dimensional normal random variables.
    
    For multi-variate normal distribution use `NormalPM`.
    
    Attributes
    ----------
    mean : float
        Mean of the normal distribution.
    std : float
        Standard deviation of the normal distribution.
    
    See Also
    --------
    NormalPM : Probabilistic model for multi-variate normal random variables.
    
    Examples
    --------
    >>> # draw 100 samples from standard normal distributon
    >>> data = np.random.normal(loc=0.0, scale=1.0, size=100)
    >>> model = Normal1DPM()
    >>> model.mean
    0.0113...
    >>> model.std
    1.0705...
    >>> model.prob(2.0)
    0.0664...
    >>> model.sample(3)
    array([-0.0674..., 1.7581..., -1.0981..., -0.7181... ])
    """

    def fit(self, data):
        self.mean = np.mean(data)
        self.std = max(np.std(data, ddof=0), _MIN_STD)  # TODO: verificar qual o ddof correto a se utilizar

    def logprob(self, x):
        return stats.norm.logpdf(x, loc=self.mean, scale=self.std)

    def prob(self, x):
        return stats.norm.pdf(x, loc=self.mean, scale=self.std)

    def sample(self, n=1):
        return stats.norm.rvs(loc=self.mean, scale=self.std, size=n)


class NormalPM(ProbabilisticModel):
    """
    Probabilistic model for multi-variate normal random variables.
    
    For univariate normal distribution use `Normal1DPM`.
    
    For this model, `data` must be (n-samples, n-dimensions) shaped.
    
    Attributes
    ----------
    mean : np.ndarray
        Mean of the normal distribution.
    cov : np.ndarray
        Covariance matrix of the normal distribution.
    
    Parameters
    ----------
    cv_type : string, optional
        The type of the covariance matrix to be used. Accepted values are
        "spherical", "diag" or "full". If "spherical" the covariance matrix
        is a scalar multiplied by an identity matrix. If "diag" the covariance
        matrix is diagonal. And if "full" it has no restrictions (except those
        inherent to a covariance matrix). Defaults to "full".
    
    See Also
    --------
    Normal1DPM : Probabilistic model for one-dimensional normal random variables.
    
    Examples
    --------
    >>> data = np.empty((100, 2))
    >>> data[:, 0] = np.random.normal(loc=0.0, scale=1.0, size=100)
    >>> data[:, 1] = np.random.normal(loc=1.0, scale=2.0, size=100)
    >>> model = NormalPM("diag")
    >>> model.mean
    array([-0.0650..., 0.8733...])
    >>> model.cov
    array([[1.1658..., 0.       ],
           [0.       , 3.7543...]])
    >>> model.prob((1.0, 3.0))
    0.0256...
    >>> model.sample(1)
    array([-0.3807..., 1.3748...])
    """

    def __init__(self, cv_type='full'):
        self.cv_type = cv_type

    def fit(self, data):
        gmm = GMM(n_components=1, covariance_type=self.cv_type)
        gmm.fit(data)
        self.mean = gmm.means_[0]
        if self.cv_type == 'full':
            self.cov = gmm.covars_[0]
        elif self.cv_type == 'tied':
            self.cov = gmm.covars_
        else:
            self.cov = np.diag(gmm.covars_[0])

    def logprob(self, x):
        return stats.multivariate_normal.logpdf(x, mean=self.mean, cov=self.cov)

    def prob(self, x):
        return stats.multivariate_normal.pdf(x, mean=self.mean, cov=self.cov)

    def sample(self, n=1):
        return stats.multivariate_normal.rvs(mean=self.mean, cov=self.cov, size=n)


class NaiveNormalPM(ProbabilisticModel):
    """
    Probabilistic model for indenpendent normal random variables.
    
    This model works the same way as the `NormalPM` with "diag" `cv_type`, but
    is considerably faster.
    
    For this model, `data` must be (n-samples, n-dimensions) shaped.
    
    Attributes
    ----------
    mean : np.ndarray
        Mean of the normal distribution.
    std : np.ndarray
        Vector containing the standard deviation for each variable.
    
    See Also
    --------
    NormalPM : Probabilistic model for one-dimensional normal random variables.
    
    Examples
    --------
    >>> data = np.empty((100, 2))
    >>> data[:, 0] = np.random.normal(loc=0.0, scale=1.0, size=100)
    >>> data[:, 1] = np.random.normal(loc=1.0, scale=2.0, size=100)
    >>> model = NaiveNormalPM()
    >>> model.mean
    array([-0.0650..., 0.8733...])
    >>> model.std
    array([1.1658..., 3.7543...])
    >>> model.prob((1.0, 3.0))
    0.0256...
    >>> model.sample(1)
    array([-0.3807..., 1.3748...])
    """

    def fit(self, data):
        self.mean = np.mean(data, axis=0)
        self.std = np.std(data, ddof=0, axis=0)
        self.std[self.std <= _MIN_STD] = _MIN_STD  # TODO: verificar qual o ddof correto a se utilizar

    def logprob(self, x):
        return np.sum(
            np.vstack(stats.norm.logpdf(x_, loc=mean, scale=std) for x_, mean, std in zip(x.T, self.mean, self.std)),
            axis=0)

    def prob(self, x):
        return np.prod(
            np.vstack(stats.norm.pdf(x_, loc=mean, scale=std) for x_, mean, std in zip(x.T, self.mean, self.std)),
            axis=0)

    def sample(self, n=1):
        return np.vstack(stats.norm.rvs(loc=mean, scale=std, size=n) for mean, std in zip(self.mean, self.std)).T


_PMDICT = {"uniform": UniformD1DPM,
           "proportional": ProportionalD1DPM,
           "fixed": FixedD1DPM,
           "normal-1d": Normal1DPM,
           "normal": NormalPM,
           "naivenormal": NaiveNormalPM,
           }


def get_probabilistic_model(key):
    return _PMDICT.get(key, None)
