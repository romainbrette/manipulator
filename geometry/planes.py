'''
Calculation related to planes (intersections, etc)
'''
from numpy import cross, dot

__all__ = ['Plane']

class Plane(object):
    '''
    A plane is defined by its normal vector n and an offset a, according to:
    n.x + a = 0
    '''
    def __init__(self, vector, offset):
        self.n = vector
        self.a = offset

    @staticmethod
    def from_points(x1, x2, x3):
        '''
        Returns a plane determined by three points
        '''
        n = cross(x2-x1, x3-x1)
        a = -dot(n, x1)
        return Plane(n,a)

    def signed_distance(self, x, u):
        '''
        Signed distance of x from the plane along vector u.
        That is, returns k such that x + k.u is in the plane.
        '''
        return -(dot(self.n, x) + self.a)/dot(self.n, u)

    def project(self, x, u = None):
        '''
        Projects point x to the plane along vector u.
        If u is not specified, default is the normal vector, i.e.,
        orthogonal projection
        '''
        if u is None:
            u = self.n
        return x+self.signed_distance(x, u)*u

    def parallel_plane(self, x):
        '''
        Returns a parallel plane passing by x
        '''
        return Plane(self.n, -dot(self.n, x))

if __name__ == '__main__':
    from numpy import *
    x1 = zeros(3)
    x2 = array([0,1,0])
    x3 = array([1,0,0])

    p = Plane.from_points(x1, x2, x3)
    print p.n
    print p.signed_distance(2*ones(3), array([0,0,1]))
    print p.project(2*ones(3), array([0,0,1]))
    print p.project(2*ones(3))
    p2 = p.parallel_plane(2*ones(3))
    print p2.n, p2.a
