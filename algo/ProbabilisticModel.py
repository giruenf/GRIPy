# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np
from scipy import stats
from sklearn.mixture import GMM
from collections import defaultdict

from Algo import RockPhysics as RP
from scipy.optimize import minimize

_MIN_STD = 1.0E-4


class ProbabilisticModel(object):
    def fit(self, data):
        pass

    def logprob(self, x):
        pass
    
    def prob(self, x):
        pass

    def sample(self, n):
        pass


class Discrete1DPM(ProbabilisticModel):
    def __init__(self):
        self.probabilities = defaultdict(float)
    
    def logprob(self, x):
        return np.log(self.prob(x))
    
    def prob(self, x):
        return np.vectorize(self.probabilities.__getitem__)(x)  # TODO: alguma forma melhor de fazer isso?
    
    def sample(self, n=1):
        return np.random.choice(self.probabilities.keys(), size=n, p=self.probabilities.values())


class UniformD1DPM(Discrete1DPM):
    def fit(self, data):
        self.probabilities.clear()
        uniquedata = np.unique(data)
        for ud in uniquedata:
            self.probabilities[ud] = 1.0/len(uniquedata)


class ProportionalD1DPM(Discrete1DPM):
    def fit(self, data):
        uniquedata = np.unique(data)
        self.probabilities = {}
        for ud in uniquedata:
            self.probabilities[ud] = np.sum(data == ud)/len(data)


class FixedD1DPM(Discrete1DPM):
    def __init__(self, probabilities):
        super(FixedD1DPM, self).__init__()
        self.probabilities.update(probabilities)


class Normal1DPM(ProbabilisticModel):
    def fit(self, data):
        self.mean = np.mean(data)
        # self.std = np.std(data, ddof=0)
        self.std = max(np.std(data, ddof=0), _MIN_STD)  # TODO: verificar qual o ddof correto a se utilizar

    def logprob(self, x):
        return stats.norm.logpdf(x, loc=self.mean, scale=self.std)
        
    def prob(self, x):
        # if not self.std:
            # return (x == self.mean).astype(float)
        # return stats.norm.pdf(x, loc=self.mean, scale=self.std)
        
        return stats.norm.pdf(x, loc=self.mean, scale=self.std)
        # return np.exp(self.logprob(x))

    def sample(self, n=1):
        return stats.norm.rvs(loc=self.mean, scale=self.std, size=n)
        
        
class NormalPM(ProbabilisticModel):
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
        # return np.exp(self.logprob(x))

    def sample(self, n=1):
        return stats.multivariate_normal.rvs(mean=self.mean, cov=self.cov, size=n)


class NaiveNormalPM(ProbabilisticModel):
    def fit(self, data):
        self.means = np.mean(data, axis=0)
        self.stds = np.std(data, ddof=0, axis=0)
        self.stds[self.stds <= _MIN_STD] = _MIN_STD  # TODO: verificar qual o ddof correto a se utilizar
    
    def logprob(self, x):
        return np.sum(np.vstack(stats.norm.logpdf(x_, loc=mean, scale=std) for x_, mean, std in zip(x.T, self.means, self.stds)), axis=0)
    
    def prob(self, x):
        # std1 = self.stds != 0
        # if std1.all():
            # return np.prod(np.vstack(stats.norm.pdf(x_, loc=mean, scale=std) for x_, mean, std in zip(x.T, self.means, self.stds)), axis=0)
        # elif std1.any():
            # p0 = np.prod(np.vstack(x_ == mean for x_, mean in zip(x.T[~std1], self.means[~std1])), axis=0, dtype=float)
            # p1 = np.prod(np.vstack(stats.norm.pdf(x_, loc=mean, scale=std) for x_, mean, std in zip(x.T[std1], self.means[std1], self.stds[std1])), axis=0)
            # return p0*p1
        # else:
            # return np.prod(np.vstack(x_ == mean for x_, mean in zip(x.T, self.means)), axis=0, dtype=float)
        return np.prod(np.vstack(stats.norm.pdf(x_, loc=mean, scale=std) for x_, mean, std in zip(x.T, self.means, self.stds)), axis=0)
        # return np.exp(self.logprob(x))
    
    def sample(self, n=1):
        return np.vstack(stats.norm.rvs(loc=mean, scale=std, size=n) for mean, std in zip(self.means, self.stds)).T
        

class NormalMixture1DPM(ProbabilisticModel):
    def __init__(self, n=None, n_min=2, n_max=9, n_estimator='BIC'):
        self.n = n
        self.n_min = n_min
        self.n_max = n_max
        self.n_estimator = n_estimator
    
    @staticmethod
    def _chosebestformetric(name, score):
        if name in ('BIC',):
            return np.argmin(score)
        else:
            return np.argmax(score)

    def fit(self, data):
        if self.n is None:
            means = []
            stds = []
            weights = []
            score = []
            for n in range(self.n_min, self.n_max):
                gmm = GMM(n_components=n, covariance_type='full')
                gmm.fit(data)
                means.append(gmm.means_)
                stds.append(gmm.covars_)
                weights.append(gmm.weights_)
                if self.n_estimator == 'BIC':
                    score.append(gmm.bic(data))
            
            i_best = self._chosebestformetric(self.n_estimator, score)
            
            self.means = means[i_best]
            self.stds = stds[i_best]
            self.weights = weights[i_best]
        
        else:
            gmm = GMM(n_components=self.n, covariance_type='full')
            gmm.fit(data)
            self.means = gmm.means_
            self.stds = gmm.covars_
            self.weights = gmm.weights_
    
    def logprob(self, x):
        p = 0.0
        for i in range(len(self.means)):
            pp = np.log(self.weights[i])
            for j in range(len(self.means[i])):
                pp += stats.norm.logpdf(x, loc=self.means[i, j], scale=self.stds[i, j])
            p += np.exp(pp)
        return np.log(p)
    
    def prob(self, x):
        p = 0.0
        for i in range(len(self.means)):
            pp = self.weights[i]
            for j in range(len(self.means[i])):
                pp *= stats.norm.pdf(x, loc=self.means[i, j], scale=self.stds[i, j])
            p += pp
        return p

    def sample(self, n=1):
        counts = np.random.multinomial(n, self.weights, size=1)
        samples = np.empty((n, len(self.means[0])))
        
        k = 0
        for i in range(len(self.means)):
            for j in range(len(self.means[i])):
                samples[k:k+counts[i], j] = stats.norm.rvs(loc=self.means[i, j], scale=self.stds[i, j], size=counts[i])
            k += counts[i]
        
        np.shuffle(samples)
        
        return samples
        

class NormalMixturePM(ProbabilisticModel):
    def __init__(self, cv_type='full', n=None, n_min=2, n_max=9, n_estimator='BIC'):
        self.cv_type = cv_type
        self.n = n
        self.n_min = n_min
        self.n_max = n_max
        self.n_estimator = n_estimator
    
    @staticmethod
    def _chosebestformetric(name, score):
        if name in ('BIC',):
            return np.argmin(score)
        else:
            return np.argmax(score)

    def fit(self, data):
        if self.n is None:
            means = []
            covs = []
            weights = []
            score = []
            for n in range(self.n_min, self.n_max):
                gmm = GMM(n_components=n, covariance_type=self.cv_type)
                gmm.fit(data)
                means.append(gmm.means_)
                if self.cv_type == 'full':
                    covs.append(gmm.covars_)
                elif self.cv_type == 'tied':
                    covs.append(np.tile(gmm.covars_, (n, 1, 1)))
                else:
                    covs.append(np.array([np.diag(cv) for cv in gmm.covars_]))
                weights.append(gmm.weights_)
                if self.n_estimator == 'BIC':
                    score.append(gmm.bic(data))
            
            i_best = self._chosebestformetric(self.n_estimator, score)
            
            self.means = means[i_best]
            self.covs = covs[i_best]
            self.weights = weights[i_best]
        
        else:
            gmm = GMM(n_components=self.n, covariance_type=self.cv_type)
            gmm.fit(data)
            self.means = gmm.means_
            if self.cv_type == 'full':
                self.covs = gmm.covars_
            elif self.cv_type == 'tied':
                self.covs = np.tile(gmm.covars_, (n, 1, 1))
            else:
                self.covs = np.array([np.diag(cv) for cv in gmm.covars_])
            self.weights = gmm.weights_

    def logprob(self, x):
        p = 0.0
        for i in range(len(self.means)):
            p += np.exp(np.log(self.weights[i]) + stats.multivariate_normal.logpdf(x, mean=self.means[i], cov=self.covs[i]))
        return np.log(p)

    def prob(self, x):
        p = 0.0
        for i in range(len(self.means)):
            p += self.weights[i]*stats.multivariate_normal.pdf(x, mean=self.means[i], cov=self.covs[i])
        return p

    def sample(self, n=1):
        counts = np.random.multinomial(n, self.weights, size=1)
        samples = np.empty((n, len(self.means[0])))
        
        j = 0
        for i in range(len(self.means)):
            samples[j:j+counts[i]] = stats.multivariate_normal.rvs(mean=self.means[i], cov=self.covs[i], size=counts[i])
            j += counts[i]
        
        np.shuffle(samples)
        
        return samples

        
class GaussianKDEPM(ProbabilisticModel):
    def __init__(self, bw='scott'):
        self.bw = bw

    def fit(self, data):
        self.gkde = stats.gaussian_kde(data.T, self.bw)

    def prob(self, x):
        return self.gkde.evaluate(x.T)

    def sample(self, n=1):
        return self.gkde.resample(n)

        
class KeysXuPM(ProbabilisticModel):
    # Unidades:
    # -> Densidade: g/cm3
    # -> Velocidade: km/s
    # -> Módulos elásticos: GPa
    def __init__(self, rho_fl_min=0.5, rho_fl_max=1.5, rho_fl0=1.0,
                 rho_gr_min=1.5, rho_gr_max=4.0, rho_gr0=2.75,
                 alpha_min=0.001, alpha_max=0.999, alpha0=0.5,
                 km_min=5.0, km_max=75.0, km0=40.0,
                 gm_min=5.0, gm_max=75.0, gm0=40.0,
                 kfl_min=0.001, kfl_max=5.999, kfl0=3.0,
                 rho_std=None, vp_std=None, phi_std_factor=1.0, rho_std_factor=1.0, vp_std_factor=1.0):
        
        self.rho_fl_min = rho_fl_min
        self.rho_fl_max = rho_fl_max
        self.rho_fl0 = rho_fl0
        self.rho_gr_min = rho_gr_min
        self.rho_gr_max = rho_gr_max
        self.rho_gr0 = rho_gr0
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max
        self.alpha0 = alpha0
        self.km_min = km_min
        self.km_max = km_max
        self.km0 = km0
        self.gm_min = gm_min
        self.gm_max = gm_max
        self.gm0 = gm0
        self.kfl_min = kfl_min
        self.kfl_max = kfl_max
        self.kfl0 = kfl0
        
        self.rho_std = rho_std
        self.vp_std = vp_std
        self.phi_std_factor = phi_std_factor
        self.rho_std_factor = rho_std_factor
        self.vp_std_factor = vp_std_factor
        
        self.otherspm = None
    
    def rho_residual(self, x):
        return np.mean((self.rho - RP.rho(self.phi, x[0], x[1]))**2)
    
    def vp_residual(self, x):
        return np.mean((self.vp - RP.Vp(x[0], x[1], self.phi, x[2], x[3], self.rho))**2)
    
    def calibrate_phi(self):
        self.phi_mean = np.mean(self.phi)
        self.phi_std = np.std(self.phi, ddof=0)
    
    def calibrate_rho(self):
        method = 'L-BFGS-B'
        options = dict()
        
        rho0 = (self.rho_gr0, self.rho_fl0)
        rho_bounds = ((self.rho_gr_min, self.rho_gr_max), (self.rho_fl_min, self.rho_fl_max))

        rho_par = minimize(self.rho_residual, rho0, method=method, bounds=rho_bounds, options=options)
        
        self.rho_gr = rho_par.x[0]
        self.rho_fl = rho_par.x[1]
        
        if self.rho_std is None:
            self.rho_std = np.std(self.rho - RP.rho(self.phi, self.rho_gr, self.rho_fl), ddof=0)
        
        # print "rho_par.success =", rho_par.success
        # print "rho_par.message =", rho_par.message
        # print "rho_par.nit =", rho_par.nit
        # print
    
    def calibrate_vp(self):
        method = 'L-BFGS-B'
        options = dict()
        
        vp0 = (self.km0, self.gm0, self.alpha0, self.kfl0)
        vp_bounds = ((self.km_min, self.km_max), (self.gm_min, self.gm_max), (self.alpha_min, self.alpha_max), (self.kfl_min, self.kfl_max))
        
        vp_par = minimize(self.vp_residual, vp0, method=method, bounds=vp_bounds, options=options)
        
        self.Km = vp_par.x[0]
        self.Gm = vp_par.x[1]
        self.alpha = vp_par.x[2]
        self.Kfl = vp_par.x[3]
        
        if self.vp_std is None:
            self.vp_std = np.std(self.vp - RP.Vp(self.Km, self.Gm, self.phi, self.alpha, self.Kfl, self.rho), ddof=0)
        
        # print "vp_par.success =", vp_par.success
        # print "vp_par.message =", vp_par.message
        # print "vp_par.nit =", vp_par.nit
        # print
        
    def fit(self, data):
        self.phi = data[:, 0]
        self.rho = data[:, 1]
        self.vp = data[:, 2]
        
        self.calibrate_phi()
        self.calibrate_rho()
        self.calibrate_vp()
        
        if data.shape[1] > 3:
            self.otherspm = NaiveNormalPM()
            self.otherspm.fit(data[:, 3:])
        
        # import matplotlib.pyplot as plt
        
        # min_phi = np.min(self.phi)
        # max_phi = np.max(self.phi)
        # D_phi = max_phi - min_phi
        # phi_plot = np.linspace(min_phi - 0.1*D_phi, max_phi + 0.1*D_phi, 1000)
        # rho_plot = RP.rho(phi_plot, self.rho_gr, self.rho_fl)
        # vp_plot = RP.Vp(self.Km, self.Gm, phi_plot, self.alpha, self.Kfl, rho_plot)
        
        # plt.subplot(121)
        # plt.plot(phi_plot, rho_plot, 'r--')
        # plt.plot(self.phi, self.rho, 'bo')
        
        # plt.subplot(122)
        # plt.plot(phi_plot, vp_plot, 'r--')
        # plt.plot(self.phi, self.vp, 'bo')
        
        # plt.show()

    def logprob(self, x):
        phi = x[:, 0]
        rho = x[:, 1]
        vp = x[:, 2]
        
        phi_std = self.phi_std*self.phi_std_factor
        logp_phi = stats.norm.logpdf(phi, loc=self.phi_mean, scale=phi_std)
        
        rho_mean = RP.rho(phi, self.rho_gr, self.rho_fl)
        rho_std = self.rho_std*self.rho_std_factor
        logp_rho = stats.norm.logpdf(rho, loc=rho_mean, scale=rho_std)
        
        vp_mean = RP.Vp(self.Km, self.Gm, phi, self.alpha, self.Kfl, rho)
        vp_std = self.vp_std*self.vp_std_factor
        logp_vp = stats.norm.logpdf(vp, loc=vp_mean, scale=vp_std)
        
        logp_others = 0.0
        if self.otherspm is not None:
            logp_others = self.otherspm.logprob(x[:, 3:])
        
        return logp_phi + logp_rho + logp_vp + logp_others
    
    def prob(self, x):
        phi = x[:, 0]
        rho = x[:, 1]
        vp = x[:, 2]
        
        phi_std = self.phi_std*self.phi_std_factor
        p_phi = stats.norm.pdf(phi, loc=self.phi_mean, scale=phi_std)
        
        rho_mean = RP.rho(phi, self.rho_gr, self.rho_fl)
        rho_std = self.rho_std*self.rho_std_factor
        p_rho = stats.norm.pdf(rho, loc=rho_mean, scale=rho_std)
        
        vp_mean = RP.Vp(self.Km, self.Gm, phi, self.alpha, self.Kfl, rho)
        vp_std = self.vp_std*self.vp_std_factor
        p_vp = stats.norm.pdf(vp, loc=vp_mean, scale=vp_std)
        
        p_others = 1.0
        if self.otherspm is not None:
            p_others = self.otherspm.prob(x[:, 3:])
        
        return p_phi*p_rho*p_vp*p_others
    
    def sample(self, n=1):
        phi_std = self.phi_std*self.phi_std_factor
        phi = stats.norm.rvs(loc=self.phi_mean, scale=phi_std, size=n)
        
        rho_mean = RP.rho(phi, self.rho_gr, self.rho_fl)
        rho_std = self.rho_std*self.rho_std_factor
        rho = stats.norm.rvs(loc=rho_mean, scale=rho_std, size=n)
        
        vp_mean = RP.Vp(self.Km, self.Gm, phi, self.alpha, self.Kfl, rho)
        vp_std = self.vp_std*self.vp_std_factor
        vp = stats.norm.rvs(loc=vp_mean, scale=vp_std, size=n)
        
        if self.otherspm is not None:
            others = self.otherspm.sample(n)
            return np.vstack([phi, rho, vp, others.T]).T
        else:
            return np.vstack([phi, rho, vp]).T


_PMDICT = {"uniform": UniformD1DPM,
           "proportional": ProportionalD1DPM,
           "fixed": FixedD1DPM,
           "normal-1d": Normal1DPM,
           "normal": NormalPM,
           "naivenormal": NaiveNormalPM,
           "normalmixture-1d": NormalMixture1DPM,
           "normalmixture": NormalMixturePM,
           "gaussiankde": GaussianKDEPM,
           "keysxu": KeysXuPM,
           }

def get_probabilistic_model(key):
    return _PMDICT.get(key, None)
