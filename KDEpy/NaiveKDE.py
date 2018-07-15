#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  4 10:52:17 2018

@author: tommy

./binary_tree.pxi-465-cdef DTYPE_t _log_kernel_norm(DTYPE_t h, ITYPE_t d,
./binary_tree.pxi-466-                              KernelType kernel) except -1:
./binary_tree.pxi-473-    if kernel == GAUSSIAN_KERNEL:
./binary_tree.pxi-474-        factor = 0.5 * d * LOG_2PI
./binary_tree.pxi-475-    elif kernel == TOPHAT_KERNEL:
./binary_tree.pxi:476:        factor = logVn(d)
./binary_tree.pxi-477-    elif kernel == EPANECHNIKOV_KERNEL:
./binary_tree.pxi:478:        factor = logVn(d) + log(2. / (d + 2.))
./binary_tree.pxi-479-    elif kernel == EXPONENTIAL_KERNEL:
./binary_tree.pxi-480-        factor = logSn(d - 1) + lgamma(d)
./binary_tree.pxi-481-    elif kernel == LINEAR_KERNEL:
./binary_tree.pxi:482:        factor = logVn(d) - log(d + 1.)
./binary_tree.pxi-483-    elif kernel == COSINE_KERNEL:
./binary_tree.pxi-484-        # this is derived from a chain rule integration
./binary_tree.pxi-485-        factor = 0
./binary_tree.pxi-486-        tmp = 2. / PI
./binary_tree.pxi-487-        for k in range(1, d + 1, 2):
./binary_tree.pxi-488-            factor += tmp
./binary_tree.pxi-489-            tmp *= -(d - k) * (d - k - 1) * (2. / PI) ** 2
./binary_tree.pxi-490-        factor = log(factor) + logSn(d - 1)
./binary_tree.pxi-491-    else:
./binary_tree.pxi-492-        raise ValueError("Kernel code not recognized")
./binary_tree.pxi-493-    return -factor - d * log(h)


"""
import pytest
import numbers
import numpy as np
from KDEpy.BaseKDE import BaseKDE


class NaiveKDE(BaseKDE):
    """
    The class for a naive implementation of the KDE.
    """
    
    def __init__(self, kernel='gaussian', bw=1, norm=2):
        """
        Initialize a naive KDE.
        """
        super().__init__(kernel, bw)
        self.norm = norm
    
    def fit(self, data, weights=None):
        """Fit the KDE to the data.
    
        Parameters
        ----------
        data
            The data points.
        weights
            The weights.
            
        Returns
        -------
        self
            Returns the instance.
            
        Examples
        --------
        >>> data = [1, 3, 4, 7]
        >>> kde = NaiveKDE().fit(data)
        """
        
        # Sets self.data
        super().fit(data)
        
        # If weights were passed
        if weights is not None:
            if not len(weights) == len(data):
                raise ValueError('Length of data and weights must match.')
            else:
                weights = self._process_sequence(weights)
                self.weights = np.asfarray(weights)
        else:
            self.weights = np.ones_like(self.data)
            
        self.weights = self.weights / np.sum(self.weights)
            
        return self
    
    def evaluate(self, grid_points=None):
        """Evaluate on the grid points.
        """
        
        # This method sets self.grid points and verifies it
        super().evaluate(grid_points)
        
        # Return the array converted to a float type
        grid_points = np.asfarray(self.grid_points)
        
        # Create zeros on the grid points
        evaluated = np.zeros_like(grid_points)
        
        # For every data point, compute the kernel and add to the grid
        bw = self.bw
        if isinstance(bw, numbers.Number):
            bw = np.asfarray(np.ones_like(self.data) * bw)
        elif callable(bw):
            bw = np.asfarray(np.ones_like(self.data) * bw(self.data))

        for weight, data_point, bw in zip(self.weights, self.data, bw):
            evaluated += weight * self.kernel(grid_points - data_point, 
                                              bw=bw)
            
        return self._evalate_return_logic(evaluated, grid_points)


if __name__ == "__main__":
    # --durations=10  <- May be used to show potentially slow tests
    pytest.main(args=['.', '--doctest-modules', '-v'])

if __name__ == '__main__':
    
    import matplotlib.pyplot as plt
    
    # Basic example of the naive KDE
    # -----------------------------------------
    data = [3, 3.5, 4, 6, 8]
    kernel = 'gaussian'
    bw = 1
    
    plt.figure(figsize=(10, 4))
    plt.title('Basic example of the naive KDE')
    
    plt.subplot(1, 2, 1)
    kde = NaiveKDE(kernel=kernel, bw=bw)
    kde.fit(data)
    x = np.linspace(0, 10, num=1024)
    for d in data:
        k = NaiveKDE(kernel=kernel, bw=bw).fit([d]).evaluate(x) / len(data)
        plt.plot(x, k, color='k', ls='--')
        
    y = kde.evaluate(x)
    plt.plot(x, y)
    plt.scatter(data, np.zeros_like(data))
    
    plt.subplot(1, 2, 2)
    kde = NaiveKDE(kernel=kernel, bw=bw)
    kde.fit(data)
    x = np.linspace(0, 10, num=1024)
    for d in data:
        k = NaiveKDE(kernel=kernel, bw=bw).fit([d]).evaluate(x) / len(data)
        plt.plot(x, k, color='k', ls='--')
        
    y = kde.evaluate(x)
    plt.plot(x, y)
    plt.scatter(data, np.zeros_like(data))
    plt.show()
    
    # Naive KDE with weights
    # -----------------------------------------
    data = [3, 3.5, 4, 6, 8]
    weights = np.array([1, 1, 1, 1, 5])
    weights = weights / np.sum(weights)
    kernel = 'gaussian'
    bw = 1
    
    kde = NaiveKDE(kernel=kernel, bw=bw)
    kde.fit(data, weights=weights)
    
    x = np.linspace(0, 10, num=1024)
    for d, w in zip(data, weights):
        k = (NaiveKDE(kernel=kernel, bw=bw).fit([d], weights=[w]).evaluate(x) *
             w)
        plt.plot(x, k, color='k', ls='--')
        
    y = kde.evaluate(x)
    plt.title('Naive KDE with weights')
    plt.plot(x, y)
    plt.scatter(data, np.zeros_like(data))
    plt.show()
    
    # Naive KDE with variable h
    # -----------------------------------------
    data = [2, 3, 4, 5, 6, 7]
    bws = [1, 2, 3, 4, 5, 6]
    bws = [1 / k for k in bws]
    kernel = 'gaussian'
    
    kde = NaiveKDE(kernel=kernel, bw=bws)
    kde.fit(data)
    
    x = np.linspace(0, 10, num=1024)
    for d, bw in zip(data, bws):
        k = NaiveKDE(kernel=kernel, bw=bw).fit([d]).evaluate(x) / len(data)
        plt.plot(x, k, color='k', ls='--')
        
    y = kde.evaluate(x)  
    plt.title('Naive KDE with variable h')
    plt.plot(x, y)
    plt.scatter(data, np.zeros_like(data))
    plt.show()
    
    # Naive KDE with silverman
    # -----------------------------------------
    data = [2, 3, 4, 5, 6, 7]
    bws = [1, 2, 3, 4, 5, 6]
    bws = [1 / k for k in bws]
    kernel = 'gaussian'
    
    kde = NaiveKDE(kernel=kernel, bw='silverman')
    kde.fit(data)
    
    x = np.linspace(0, 10, num=1024)
    for d, bw in zip(data, bws):
        k = (NaiveKDE(kernel=kernel, bw='silverman').fit([d]).evaluate(x) / 
             len(data))
        plt.plot(x, k, color='k', ls='--')
        
    y = kde.evaluate(x)  
    plt.title('Naive KDE with silverman')
    plt.plot(x, y)
    plt.scatter(data, np.zeros_like(data))
    plt.show()