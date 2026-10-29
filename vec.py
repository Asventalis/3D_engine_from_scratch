from math import sqrt, acos, cos, sin, pi as PI
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation


DPI = 144

def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

def add(vec1, vec2):
    return [vec1[i] + vec2[i] for i in range(3)]

def sub(vec1, vec2):
    return [vec1[i] - vec2[i] for i in range(3)]

def scaled(vec, factor):
    return [vec[i] * factor for i in range(3)]

def dot(vec1, vec2):
    return sum([vec1[i] * vec2[i] for i in range(len(vec1))])

def norm(vec):
    return sqrt(dot(vec, vec))

def normalized(vec):
    return scaled(vec, 1 / norm(vec))

def cross(vec1, vec2):
    return [vec1[1] * vec2[2] - vec1[2] * vec2[1],
            vec1[2] * vec2[0] - vec1[0] * vec2[2],
            vec1[0] * vec2[1] - vec1[1] * vec2[0]]

def angle(vec1, vec2):
    return acos(dot(vec1, vec2) / (norm(vec1) * norm(vec2)))

def rotated(vec, axis, angle):
    c = cos(angle)
    s = sin(angle)
    axis = normalized(axis)
    return [c * vec[i] + s * cross(axis, vec)[i] + (1 - c) * dot(axis, vec) * axis[i] for i in range(3)]

class Reference_System:
    def __init__(self, origin, x_axis, y_axis, z_axis):
        self.origin = origin
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.z_axis = z_axis
    
    def point_to_local(self, point):
        return [dot(sub(point, self.origin), self.x_axis),
                dot(sub(point, self.origin), self.y_axis),
                dot(sub(point, self.origin), self.z_axis)]
    
    def point_to_global(self, point):
        return add(self.origin, add(scaled(self.x_axis, point[0]), add(scaled(self.y_axis, point[1]), scaled(self.z_axis, point[2]))))
    
    def vector_to_local(self, vector):
        return [dot(vector, self.x_axis), dot(vector, self.y_axis), dot(vector, self.z_axis)]
    
    def vector_to_global(self, vector):
        return add(scaled(self.x_axis, vector[0]), add(scaled(self.y_axis, vector[1]), scaled(self.z_axis, vector[2])))

    def triangle_to_local(self, triangle):
        return Triangle(self.point_to_local(triangle.p1), self.point_to_local(triangle.p2), self.point_to_local(triangle.p3), triangle.color)
    
    def triangle_to_global(self, triangle):
        return Triangle(self.point_to_global(triangle.p1), self.point_to_global(triangle.p2), self.point_to_global(triangle.p3), triangle.color)
    
    def global_rotate(self, axis, angle):
        self.x_axis = rotated(self.x_axis, axis, angle)
        self.y_axis = rotated(self.y_axis, axis, angle)
        self.z_axis = rotated(self.z_axis, axis, angle)
    
    def local_rotate(self, axis, angle):
        actual_axis = self.vector_to_global(axis)
        self.global_rotate(actual_axis, angle)
    
    def global_translate(self, vector):
        self.origin = add(self.origin, vector)

    def local_translate(self, vector):
        actual_vector = self.point_to_global(vector)
        self.origin = add(self.origin, actual_vector)

    def __str__(self):
        return "Origin: " + str(self.origin) + "\nX-Axis: " + str(self.x_axis) + "\nY-Axis: " + str(self.y_axis) + "\nZ-Axis: " + str(self.z_axis)
    

class Triangle:
    def __init__(self, p1, p2, p3, color=[255, 255, 255]):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.color = color
        self.center = scaled(add(add(p1, p2), p3), 1/3)
    
    def normal(self):
        return normalized(cross(sub(self.p2, self.p1), sub(self.p3, self.p2)))
    
    def is_visible(self, reference_system):
        return dot(sub(self.center, reference_system.origin), self.normal()) < 0
    
    def __str__(self):
        return "P1: " + str(self.p1) + "\nP2: " + str(self.p2) + "\nP3: " + str(self.p3)
    
    def illumination(self, light_sources):
        for light in light_sources:
            if light.type == 'directional':
                factor = (1-light.intensity*dot(light.direction, self.normal()))/2
                return scaled(self.color, factor)
    
    def rotated(self, axis, angle):
        return Triangle(rotated(self.p1, axis, angle), rotated(self.p2, axis, angle), rotated(self.p3, axis, angle), self.color)
    
    def translated(self, vector):
        return Triangle(add(self.p1, vector), add(self.p2, vector), add(self.p3, vector), self.color)

class Mesh:
    def __init__(self, frame, triangles):
        self.triangles = triangles
        self.frame = frame
    
    def __str__(self):
        return "\n".join([str(triangle) for triangle in self.triangles])
    
    @staticmethod
    def MeshCube(center, size, color=[255, 255, 255]):
        frame = Reference_System(center, [1, 0, 0], [0, 1, 0], [0, 0, 1])
        half_size = size / 2
        p1 = [-half_size, -half_size, -half_size]
        p2 = [half_size, -half_size, -half_size]
        p3 = [half_size, half_size, -half_size]
        p4 = [-half_size, half_size, -half_size]
        p5 = [-half_size, -half_size, half_size]
        p6 = [half_size, -half_size, half_size]
        p7 = [half_size, half_size, half_size]
        p8 = [-half_size, half_size, half_size]
        return Mesh(frame, [Triangle(p1, p3, p2, color), 
                     Triangle(p1, p4, p3, color), 
                     Triangle(p1, p2, p6, color), 
                     Triangle(p1, p6, p5, color), 
                     Triangle(p2, p3, p7, color), 
                     Triangle(p2, p7, p6, color), 
                     Triangle(p3, p4, p8, color), 
                     Triangle(p3, p8, p7, color), 
                     Triangle(p4, p1, p5, color), 
                     Triangle(p4, p5, p8, color), 
                     Triangle(p5, p6, p7, color), 
                     Triangle(p5, p7, p8, color)])
    
    @staticmethod
    def MeshTetrahedron(center, size, color=[255, 255, 255]):
        frame = Reference_System(center, [1, 0, 0], [0, 1, 0], [0, 0, 1])
        half_size = size / 2
        p1 = [-half_size, -half_size, -half_size]
        p2 = [half_size, -half_size, -half_size]
        p3 = [0, half_size, -half_size]
        p4 = [0, 0, half_size]
        # all faces must have normal outward. Normal is computed as the cross product of p2-p1 and p3-p1
        return Mesh(frame, 
                    [Triangle(p1, p3, p2, color), 
                     Triangle(p1, p4, p3, color), 
                     Triangle(p1, p2, p4, color), 
                     Triangle(p2, p3, p4, color)])
    
    @staticmethod
    def MeshSquare(center, size, color=[255, 255, 255]):
        frame = Reference_System(center, [1, 0, 0], [0, 1, 0], [0, 0, 1])
        half_size = size / 2
        p1 = [-half_size, -half_size, 0]
        p2 = [half_size, -half_size, 0]
        p3 = [half_size, half_size, 0]
        p4 = [-half_size, half_size, 0]
        return Mesh(frame, [Triangle(p1, p3, p2, color), Triangle(p1, p4, p3, color), Triangle(p1, p2, p3, color), Triangle(p1, p3, p4, color)])
    
    @staticmethod
    def MeshChessBoard(center, square_size, rows=8, columns=8, color1=[255, 255, 255], color2=[0, 0, 0]):
        frame = Reference_System(center, [1, 0, 0], [0, 1, 0], [0, 0, 1])
        half_width = square_size * columns / 2
        half_height = square_size * rows / 2
        half_size = square_size / 2
        p1 = [-half_size, -half_size, 0]
        p2 = [half_size, -half_size, 0]
        p3 = [half_size, half_size, 0]
        p4 = [-half_size, half_size, 0]
        triangles = []
        for i in range(rows):
            for j in range(columns):
                if (i+j) % 2 == 0:
                    color = color1
                else:
                    color = color2
                square_center = [j * square_size - half_width + square_size / 2, i * square_size - half_height + square_size / 2, 0]
                triangles += Mesh.MeshSquare(square_center, square_size, color).global_triangles()
        return Mesh(frame, triangles)


    def local_rotate(self, axis, angle):
        self.frame.local_rotate(axis, angle)
    
    def global_rotate(self, axis, angle):
        self.frame.global_rotate(axis, angle)
    
    def local_translate(self, vector):
        self.frame.local_translate(vector)
    
    def global_translate(self, vector):
        self.frame.global_translate(vector)
    
    def local_scale(self, vector):
        '''Scale the triangles of the mesh. The scaling is applied with respect to local coordinates.'''
        for triangle in self.triangles:
            triangle.p1 = [triangle.p1[i]*vector[i] for i in range(3)]
            triangle.p2 = [triangle.p2[i]*vector[i] for i in range(3)]
            triangle.p3 = [triangle.p3[i]*vector[i] for i in range(3)]

    def global_triangles(self):
        return [self.frame.triangle_to_global(triangle) for triangle in self.triangles]

# x direction is in front of you, y direction is to your left, z direction is up (right-handed coordinate system)
class Spherical_Projector:
    def __init__(self, reference_system, radius, number_of_points=20):
        self.reference_system = reference_system
        self.radius = radius
        self.number_of_points = number_of_points
    
    def project_point(self, point):
        local_point = self.reference_system.point_to_local(point)
        on_sphere = scaled(normalized(local_point), self.radius)
        return -on_sphere[1], on_sphere[2] # screen is in front of you with x axis to the right and y axis up, so x axis is your actual inverted y axis and y axis is your actual z axis
    
    def project_segment(self, p1, p2):
        return [self.project_point(add(p1, scaled(sub(p2, p1), i / (self.number_of_points - 1)))) for i in range(self.number_of_points)]
    
    def project_triangle(self, triangle):
        #return a single list of points
        return self.project_segment(triangle.p1, triangle.p2)[:-1] + self.project_segment(triangle.p2, triangle.p3)[:-1] + self.project_segment(triangle.p3, triangle.p1)[:-1]


class Ortographic_Projector:
    def __init__(self, reference_system, distance):
        self.reference_system = reference_system
        self.distance = distance
    
    def project_point(self, point):
        local_point = self.reference_system.point_to_local(point)
        if local_point[0] <= 0:
            return None
        return -local_point[1]*self.distance/local_point[0], local_point[2]*self.distance/local_point[0] 

    def project_segment(self, p1, p2):
        return [self.project_point(p1), self.project_point(p2)]
    
    def project_triangle(self, triangle):
        return [self.project_point(triangle.p1), self.project_point(triangle.p2), self.project_point(triangle.p3)]


class Stereographic_Projector:
    def __init__(self, reference_system, radius, number_of_points=20):
        self.reference_system = reference_system
        self.radius = radius
        self.number_of_points = number_of_points
    
    def project_point(self, point):
        local_point = self.reference_system.point_to_local(point)
        # first, project everything on the sphere centered in the origin and with radius self.radius
        on_sphere = scaled(normalized(local_point), self.radius)
        # then, project the point on the plane z=0 using the frame that is in (-self.radius, 0, 0)
        if on_sphere[0] == -self.radius:
            return None
        return -on_sphere[1]/(self.radius+on_sphere[0]), on_sphere[2]/(self.radius+on_sphere[0])

    def project_segment(self, p1, p2):
        return [self.project_point(add(p1, scaled(sub(p2, p1), i / (self.number_of_points - 1)))) for i in range(self.number_of_points)]
    
    def project_triangle(self, triangle):
        #return a single list of points
        return self.project_segment(triangle.p1, triangle.p2)[:-1] + self.project_segment(triangle.p2, triangle.p3)[:-1] + self.project_segment(triangle.p3, triangle.p1)[:-1]
    

class Cylindrical_Projector:
    def __init__(self, reference_system, radius, number_of_points=20):
        self.reference_system = reference_system
        self.radius = radius
        self.number_of_points = number_of_points
    
    def project_point(self, point):
        local_point = self.reference_system.point_to_local(point)
        on_sphere = scaled(normalized(local_point), self.radius)
        # calculate the angle between the x axis and the projection of the point on the plane z=0, and sign opposite to y coordinate sign
        if on_sphere[0] == 0 and on_sphere[1] == 0:
            return None
        alpha = -sign(on_sphere[1])*angle([1, 0, 0], [on_sphere[0], on_sphere[1], 0])
        return alpha*self.radius, on_sphere[2]

    def project_segment(self, p1, p2):
        return [self.project_point(add(p1, scaled(sub(p2, p1), i / (self.number_of_points - 1)))) for i in range(self.number_of_points)]
    
    def project_triangle(self, triangle):
        #return a single list of points
        return self.project_segment(triangle.p1, triangle.p2)[:-1] + self.project_segment(triangle.p2, triangle.p3)[:-1] + self.project_segment(triangle.p3, triangle.p1)[:-1]
    


class Light_Source:
    def __init__(self, direction, type='directional', intensity=1):
        self.direction = direction
        self.type = type
        self.intensity = intensity
        

class Scene:
    def __init__(self):
        self.light_sources = {}
        self.cameras = {}
        self.meshes = {}

    def add_light_source(self, name, light_source):
        self.light_sources[name] = light_source

    def add_camera(self, name, camera):
        self.cameras[name] = camera

    def add_mesh(self, name, mesh):
        self.meshes[name] = mesh

    def render(self, camera_name):
        camera = self.cameras[camera_name]
        camera.clear()
        for mesh in self.meshes.values():
            camera.draw_mesh(mesh, self.light_sources.values())
        camera.show()

    def render_buffer(self, camera_name):
        camera = self.cameras[camera_name]
        camera.clear()
        for mesh in self.meshes.values():
            camera.add_mesh_to_buffer(mesh)
        camera.draw_buffer(self.light_sources.values())
        camera.show()

    def animate(self, camera_name, animate_function, fps=10, duration=10, animation_name='animation.gif'):
        def actual_animate_func(frame, scene, camera, fps):
            camera.axis.cla()
            camera.axis.set_xlim(-camera.width / 2, camera.width / 2)
            camera.axis.set_ylim(-camera.height / 2, camera.height / 2)
            camera.axis.set_aspect('equal')
            animate_function(frame, scene, camera, fps)
            for mesh in self.meshes.values():
                camera.add_mesh_to_buffer(mesh)
            camera.draw_buffer(scene.light_sources.values())
            return

        figure = self.cameras[camera_name].plot
        anim = FuncAnimation(figure, actual_animate_func, frames=duration*fps, interval=1/fps*1000, fargs=[self, self.cameras[camera_name], fps])
        anim.save(animation_name, writer='pillow', fps=fps)
        
        


class Camera:
    def __init__(self, width, height, projector, pixel_width=800, pixel_height=600):
        self.pixel_width = pixel_width
        self.pixel_height = pixel_height
        self.projector = projector
        self.frame = projector.reference_system # the camera frame is the same as the projector frame (shallow copy)
        self.width = width
        self.height = height
        self.plot = plt.figure(figsize=(pixel_width/DPI, pixel_height/DPI), dpi=DPI)
        self.axis = self.plot.add_subplot(111)
        self.axis.set_aspect('equal')
        self.axis.set_xlim(-width / 2, width / 2)
        self.axis.set_ylim(-height / 2, height / 2)
        
        self.triangle_buffer = []

    def draw_point(self, point, color):
        color = scaled(color, 1/255)
        projected_point = self.projector.project_point(point)
        if None in projected_point:
            return
        self.axis.plot(projected_point[0], projected_point[1], color)

    def draw_segment(self, p1, p2, color):
        color = scaled(color, 1/255)
        projected_segment = self.projector.project_segment(p1, p2)
        if None in projected_segment:
            return
        self.axis.plot([point[0] for point in projected_segment], [point[1] for point in projected_segment], color)
    
    def draw_triangle(self, triangle, light_sources=None):
        projected_triangle = self.projector.project_triangle(triangle)
        if None in projected_triangle:
            return
        if light_sources:
            color = scaled(triangle.illumination(light_sources), 1/255)
        else:
            color = scaled(triangle.color, 1/255)
        self.axis.fill([point[0] for point in projected_triangle], [point[1] for point in projected_triangle], facecolor=color, edgecolor=color)
    
    def draw_mesh(self, mesh, light_sources=None):
        for global_triangle in mesh.global_triangles():
            if global_triangle.is_visible(self.projector.reference_system):
                self.draw_triangle(global_triangle, light_sources)


    def add_mesh_to_buffer(self, mesh):
        for global_triangle in mesh.global_triangles():
            if global_triangle.is_visible(self.projector.reference_system):
                self.triangle_buffer.append(global_triangle)
        
    def draw_buffer(self, light_sources=None):
        # sort triangles by distance from camera
        self.triangle_buffer = sorted(self.triangle_buffer, key=lambda triangle: -norm(sub(triangle.center, self.projector.reference_system.origin)))
        for triangle in self.triangle_buffer:
            self.draw_triangle(triangle, light_sources)
        self.triangle_buffer = []

    def clear(self):
        self.axis.clear()
        self.axis.set_xlim(-self.width / 2, self.width / 2)
        self.axis.set_ylim(-self.height / 2, self.height / 2)
        self.axis.set_aspect('equal')

    def show(self):
        plt.show()
    
    def local_rotate(self, axis, angle):
        '''Rotate the camera around the axis. The axis is in local coordinates.'''
        self.projector.reference_system.local_rotate(axis, angle)

    def global_rotate(self, axis, angle):
        '''Rotate the camera around the axis. The axis is in global coordinates.'''
        self.projector.reference_system.global_rotate(axis, angle)

    def local_translate(self, vector):
        '''Translate the camera of a vector. The vector is in local coordinates.'''
        self.projector.reference_system.local_translate(vector)

    def global_translate(self, vector):
        '''Translate the camera of a vector. The vector is in global coordinates.'''
        self.projector.reference_system.global_translate(vector)

