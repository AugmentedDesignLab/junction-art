import pyodrx
import numpy as np
from scipy.integrate import quad
from scipy.special import fresnel

class IntertialParamPoly(pyodrx.ParamPoly3):
    
    def get_start_data(self,x,y,h):
        """ Returns the start point of the geometry, ignores x, y, h as param poly does not depend on xyh
        
        Parameters
        ----------
            x (float): x end point of the geometry

            y (float): y end point of the geometry

            h (float): end heading of the geometry

        Returns
        ---------
            x (float): the start x point
            y (float): the start y point
            h (float): the start heading
            length (float): the length of the geometry

        """

        x = 0
        y = 0
        h = 0
        if self.prange == 'normalized':
            p = 1
            I = quad(self._integrand,0,1)
            self.length = I[0]
        else:
            p = self.length
        newu = self.au + self.bu*p + self.cu*p**2 + self.du*p**3
        newv = self.av + self.bv*p + self.cv*p**2 + self.dv*p**3

        new_x = x - newu*np.cos(h)-np.sin(h)*newv
        new_y = y - newu*np.sin(h)+np.cos(h)*newv
        new_h = h - np.arctan2(self.bv + 2*self.cv*p + 3*self.dv*p**2,self.bu + 2*self.cu*p + 3*self.du*p**2)

        return new_x, new_y, new_h, self.length


    def get_end_data(self,x,y,h):
        """ Returns the end point of the geometry
        
        Parameters
        ----------
            x (float): x final point of the geometry

            y (float): y final point of the geometry

            h (float): final heading of the geometry

        Returns
        ---------
            x (float): the start x point
            y (float): the start y point
            h (float): the start heading of the inverse geometry 
            length (float): length of the polynomial

        """
        x = 0
        y = 0
        h = 0
        if self.prange == 'normalized':
            p = 1
            I = quad(self._integrand,0,1)
            self.length = I[0]
        else:
            p = self.length
        newu = self.au + self.bu*p + self.cu*p**2 + self.du*p**3
        newv = self.av + self.bv*p + self.cv*p**2 + self.dv*p**3

        new_x = x + newu*np.cos(h)-np.sin(h)*newv
        new_y = y + newu*np.sin(h)+np.cos(h)*newv
        new_h = h + np.arctan2(self.bv + 2*self.cv*p + 3*self.dv*p**2,self.bu + 2*self.cu*p + 3*self.du*p**2)

        return new_x, new_y, new_h, self.length
