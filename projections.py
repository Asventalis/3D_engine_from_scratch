import matplotlib.pyplot as plt
import matplotlib.animation as animation
from numpy import array, vstack, cross as np_cross
from numpy.linalg import norm, solve
from math import cos, sin, acos, atan2, sqrt, atan, floor, ceil, pi as PI

def sign(number):
    if number > 0:
        return 1
    elif number < 0:
        return -1
    else:
        return 0

def colvec(list):
    '''Converts a list to a column vector'''
    return array([list]).T

def rowvec(list):
    '''Converts a list to a row vector'''
    return array([list])

def normalized(v):
    '''Returns the normalized vector v'''
    len = norm(v)
    if len == 0: 
       return v
    return v / len

def dot(a, b):
    '''Returns the dot product of a and b'''
    res = a.T @ b
    return res[0, 0]

def cross(a, b):
    '''Returns the cross product of a and b'''
    return np_cross(a, b, axis=0)

def distance2D(p1, p2):
    '''Returns the distance between two points in 2D'''
    return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
def rotated(vector, angle, axis):
    '''Rotates the vector by the given angle around the given axis'''
    axis = normalized(axis)
    a = cos(angle/2)
    b = sin(angle/2)*axis[0, 0]
    c = sin(angle/2)*axis[1, 0]
    d = sin(angle/2)*axis[2, 0]
    rotation_matrix = vstack((array([a**2 + b**2 - c**2 - d**2, 2*(b*c - a*d), 2*(b*d + a*c)]), array([2*(b*c + a*d), a**2 - b**2 + c**2 - d**2, 2*(c*d - a*b)]), array([2*(b*d - a*c), 2*(c*d + a*b), a**2 - b**2 - c**2 + d**2])))
    return rotation_matrix @ vector

class ReferenceFrame:
    def __init__(self, origin, x, y, z):
        self.origin = normalized(colvec(origin))
        self.x = normalized(colvec(x))
        self.y = normalized(colvec(y))
        self.z = normalized(colvec(z))
        self.transformation_matrix = vstack((self.x.T, self.y.T, self.z.T))
        

    def change_coordinates_system(self, old_point):
        '''Transforms a point from the old coordinate system to the new one'''
        return self.transformation_matrix @ (old_point - self.origin)
    
    def inverse_coordinates_system(self, new_point):
        '''Transforms a point from the new coordinate system to the old one'''
        return (self.transformation_matrix.T @ new_point) + self.origin
    
class Triangle:
    def __init__(self, p1, p2, p3):
        self.p1 = colvec(p1)
        self.p2 = colvec(p2)
        self.p3 = colvec(p3)
        self.normal = normalized(cross(self.p2 - self.p1, self.p3 - self.p1))

    def contains(self, point):
        '''Returns whether the point is inside the triangle'''
        normal = self.normal()
        return dot(normal, cross(self.p2 - self.p1, point - self.p1)) >= 0 and dot(normal, cross(self.p3 - self.p2, point - self.p2)) >= 0 and dot(normal, cross(self.p1 - self.p3, point - self.p3)) >= 0

    def spherical_projection_curve(self, eye_frame, radius, number_of_points):
        '''Returns the points of the 3 ellipse arcs that form the triangle in the spherical projection'''
        p1_3D = spherical_projection(self.p1, eye_frame, radius)
        p2_3D = spherical_projection(self.p2, eye_frame, radius)
        p3_3D = spherical_projection(self.p3, eye_frame, radius)

        points1 = ellipse_arc(eye_frame, self.p1, self.p2, radius, number_of_points+1)
        points2 = ellipse_arc(eye_frame, self.p2, self.p3, radius, number_of_points+1)
        points3 = ellipse_arc(eye_frame, self.p3, self.p1, radius, number_of_points+1)
        start1 = points1[0]
        end1 = points1[-1]
        start2 = points2[0]
        end2 = points2[-1]
        start3 = points3[0]
        end3 = points3[-1]
        if (distance2D(p1_3D, start1) > distance2D(p1_3D, end1)):
            points1 = points1[::-1]
        if (distance2D(p2_3D, start2) > distance2D(p2_3D, end2)):
            points2 = points2[::-1]
        if (distance2D(p3_3D, start3) > distance2D(p3_3D, end3)):
            points3 = points3[::-1]
        print(points1[0])
        print(points1[-1])
        print(points2[0])
        print(points2[-1])
        print(points3[0])
        print(points3[-1])
        print(len(points1))
        points1.pop()
        points2.pop()
        points3.pop()
        points1.extend(points2)
        print(len(points1))
        points1.extend(points3)
        print(len(points1))
        return points1
    
    def translated(self, vector):
        '''Translates the triangle by the given vector'''
        return Triangle(self.p1 + colvec(vector), self.p2 + colvec(vector), self.p3 + colvec(vector))
    
    def rotated(self, angle, axis):
        '''Rotates the triangle by the given angle around the given axis'''
        axis = colvec(axis)
        return Triangle(rotated(self.p1, angle, axis), rotated(self.p2, angle, axis), rotated(self.p3, angle, axis))
    
    def color_intensity(self, light_direction):
        '''Returns the color intensity of the triangle given the direction of the light. 0 is no intensity, 1 is full intensity'''
        return (-dot(self.normal, light_direction)+1)/2

    def is_drawable(self, eye_frame):
        '''Returns whether the triangle is visible from the observer'''
        return dot(self.normal, eye_frame.x) > 0    

def ellipse_data(eye_frame, p1, p2, radius):
    normal = normalized(cross(p2 - p1, eye_frame.origin - p1))
    normal = eye_frame.change_coordinates_system(normal+eye_frame.origin)
    a = radius
    b = abs(radius*normal[0, 0])
    theta = atan(normal[1, 0]/normal[2, 0])
    return a, b, theta

def ellipse_params(a, b, center, theta):
    '''Returns the coefficients A, B, C, D, E, F of the generic ellipse equation Ax^2 + Bxy + Cy^2 + Dx + Ey + F = 0 given the semiaxes a, b, the center, and the angle theta of the ellipse'''
    A = b**2*cos(theta)**2 + a**2*sin(theta)**2
    B = 2*(b**2 - a**2)*sin(theta)*cos(theta)
    C = b**2*sin(theta)**2 + a**2*cos(theta)**2
    D = -2*A*center[0] - B*center[1]
    E = -B*center[0] - 2*C*center[1]
    F = A*center[0]**2 + B*center[0]*center[1] + C*center[1]**2 - a**2*b**2
    return A, B, C, D, E, F

def ellipse_data_from_params(params):
    '''Returns a, b, center, and angle of the ellipse given the parameters of the ellipse'''
    A, B, C, D, E, F = params
    a = -sqrt(2*(A*E**2 + C*D**2 - B*D*E + (B**2 - 4*A*C)*F)*(A + C + sqrt((A - C)**2 + B**2)))/(B**2 - 4*A*C)
    b = -sqrt(2*(A*E**2 + C*D**2 - B*D*E + (B**2 - 4*A*C)*F)*(A + C - sqrt((A - C)**2 + B**2)))/(B**2 - 4*A*C)
    center = [(-B*E + 2*C*D)/(4*A*C - B**2), (-B*E - 2*C*D)/(4*A*C - B**2)]
    theta = atan2(2*A, B - C)/2
    return a, b, center, theta

def calculate_ellipse_points_parametric(a, b, center, theta, angle):
    xC, yC = center
    x = a*cos(angle)*cos(theta)-b*sin(angle)*sin(theta)+xC
    y = a*cos(angle)*sin(theta)+b*sin(angle)*cos(theta)+yC
    return x, y    

def inverse_ellipse_parametric(a, b, center, theta, point):
    x, y = point
    x = x - center[0]
    y = y - center[1]
    return atan2((y*cos(theta)-x*sin(theta))/b, (x*cos(theta)+y*sin(theta))/a)

def calculate_ellipse_points(a, b, center, theta, x):
    y_inf = (a*b*sqrt((a*cos(theta))**2+(b*sin(theta))**2-(x-center[0])**2)-cos(theta)*sin(theta)*(x-center[0])*(a**2-b**2))/((a*cos(theta))**2+(b*sin(theta))**2)+center[1]
    y_sup = -(a*b*sqrt((a*cos(theta))**2+(b*sin(theta))**2-(x-center[0])**2)+cos(theta)*sin(theta)*(x-center[0])*(a**2-b**2))/((a*cos(theta))**2+(b*sin(theta))**2)+center[1]
    return y_inf, y_sup

def angle_range(p1, p2, a, b, theta, number_of_points):
    angle1 = inverse_ellipse_parametric(a, b, [0,0], theta, p1)
    angle2 = inverse_ellipse_parametric(a, b, [0,0], theta, p2)
    start = min(angle1, angle2)
    end = max(angle1, angle2)
    if end - start > PI:
        start, end = end, start + 2*PI
    delta = (end - start)/(number_of_points-1)
    return [start + i*delta for i in range(number_of_points)]

def ellipse_arc(eye_frame, p1, p2, radius, number_of_points):
    a, b, theta = ellipse_data(eye_frame, p1, p2, radius)
    p1 = spherical_projection(p1, eye_frame, radius)
    p2 = spherical_projection(p2, eye_frame, radius)
    angles = angle_range(p1, p2, a, b, theta, number_of_points)
    return [calculate_ellipse_points_parametric(a,b,[0,0],theta,angle) for angle in angles]

def planar_projection(point, eye_frame, focal_distance):
    '''Projects a 3D point on a plane in front of the observer at a certain focal distance. For the observer, x direction is forward, y direction is left, z direction is up'''
    coords = eye_frame.change_coordinates_system(point)
    return -coords[1,0] * focal_distance / coords[0,0], coords[2,0] * focal_distance / coords[0,0]

def spherical_projection(point, eye_frame, radius):
    '''Projects a 3D point on a sphere around the observer of a certain radius and then projects perpendicularly in front of the observer. For the observer, x direction is forward, y direction is left, z direction is up'''
    coords = eye_frame.change_coordinates_system(point)
    on_sphere = coords*radius/norm(coords)
    return -on_sphere[1,0], on_sphere[2,0]

def stereographic_projection(point, eye_frame, radius):
    '''Projects a 3D point on a sphere around the observer of a certain radius and then projects the sphere on a plane using stereographic projection. For the observer, x direction is forward, y direction is left, z direction is up'''
    coords = eye_frame.change_coordinates_system(point)
    on_sphere = coords*radius/norm(coords)
    return -on_sphere[1,0]/(1+on_sphere[0,0]/radius), on_sphere[2,0]/(1+on_sphere[0,0]/radius)

def line_points(start, end, number_of_points):
    '''Returns a list of points on a line starting at start and going to end with number_of_points points'''
    return [array(start) + i*(array(end)-array(start))/(number_of_points-1) for i in range(number_of_points)]

def random_normal_vector(vector):
    '''Returns a vector normal to the given vector, either parallel to the xy plane or the yz plane, depending on the vector, for numerical stability'''
    if vector[2,0] < vector[0,0]:
        return colvec([vector[1,0], -vector[0,0], 0])
    else:
        return colvec([0, -vector[2,0], vector[1,0]])

def circle_points(center, radius, normal, number_of_points):
    '''Returns a list of points on a circle with center center, radius radius, that is on the plane with normal normal and passing through point center, with number_of_points points'''
    points = []
    for i in range(number_of_points):
        angle = 2*3.14159*i/number_of_points
        points.append(center + radius*(array([cos(angle), sin(angle), 0])*normal))

class Canvas:
    def __init__(self, xinf=-15, xsup=15, yinf=-15, ysup=15, xlabel='X', ylabel='Y', title=''):
        fig, ax = plt.subplots()
        self.fig = fig
        self.ax = ax
        self.ax.axis('equal')
        self.ax.set_xlim(xinf, xsup)
        self.ax.set_ylim(yinf, ysup)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.set_title(title)
        self.buffer = []

    def plot_curve(self, curve):
        x_coords = [point[0] for point in curve]
        y_coords = [point[1] for point in curve]
        self.ax.plot(x_coords, y_coords)
    
    def clear_plot(self):
        self.ax.clear()

    def clear_buffer(self):
        self.buffer = []
    
    def add_to_buffer(self, curve):
        self.buffer.append(curve)

    def plot_buffer(self):
        for curve in self.buffer:
            self.plot_curve(curve)

    def start_animation(self, update_function, interval=200):
        '''Starts an animation with the update_function that will be called at each frame, with interval interval. The update_function must have this signature: update_function(frame, self)'''	
        self.ani = animation.FuncAnimation(self.fig, update_function, interval=interval, fargs=[self])
        plt.show()

def update_example(frame, obj):
    obj.clear_plot()
    line_points_3D = line_points([4 + frame/10, 60 + frame/10, -3 + frame/10], [7 + frame/10, -40 + frame/10, 2 + frame/10], 100)
    line_points_2D = [stereographic_projection(point, eye_frame, radius) for point in line_points_3D]
    obj.plot_curve(line_points_2D)