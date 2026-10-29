import matplotlib.pyplot as plt
from numpy import array, dot
from numpy.linalg import norm
from projections import ReferenceFrame, planar_projection, spherical_projection, stereographic_projection, line_points

eye_frame = ReferenceFrame([0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1])
focal_distance = 10
radius = 10

line_points_3D = line_points([4, 6, -3], [7, -4, 2], 100)
# for point in line_points_3D:
#     print(point)

line_points_2D = [stereographic_projection(point, eye_frame, radius) for point in line_points_3D]

x_coords = [point[0] for point in line_points_2D]
y_coords = [point[1] for point in line_points_2D]

plt.plot(x_coords, y_coords)
plt.axis('equal')
plt.xlim(-15, 15)
plt.ylim(-15, 15)
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Planar Projection')
plt.show()
import matplotlib.animation as animation

fig, ax = plt.subplots()

def update(frame, ax):
    ax.clear()
    line_points_3D = line_points([4 + frame/10, 60 + frame/10, -3 + frame/10], [7 + frame/10, -40 + frame/10, 2 + frame/10], 100)
    line_points_2D = [stereographic_projection(point, eye_frame, radius) for point in line_points_3D]
    x_coords = [point[0] for point in line_points_2D]
    y_coords = [point[1] for point in line_points_2D]
    ax.plot(x_coords, y_coords)

ani = animation.FuncAnimation(fig, update, frames=100, interval=100)
plt.show()