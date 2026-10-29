import projections
import matplotlib.pyplot as plt
import numpy as np
from math import cos, sin, pi as PI


eye_frame = projections.ReferenceFrame([0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1])
p1 = projections.colvec([11, -18, 30])
p2 = projections.colvec([20, 48, 5])
radius = 10

a, b, theta =  projections.ellipse_data(eye_frame, p1, p2, radius)
print("data of ellipse: a=", a, " b=", b, " theta=", theta)

params = projections.ellipse_params(a,b, [0, 0], theta)
print("params of ellipse:", params)

p1_proj = projections.spherical_projection(p1, eye_frame, radius)
p2_proj = projections.spherical_projection(p2, eye_frame, radius)
print("p1_proj:", p1_proj)
print("p2_proj:", p2_proj)

angle_range = projections.angle_range(p1_proj, p2_proj, a, b, theta, 10)
values = projections.ellipse_arc(eye_frame, p1, p2, radius, 5)
x = [values[i][0] for i in range(len(values))]
y = [values[i][1] for i in range(len(values))]

x_circle = [radius*sin(2*PI*i/500) for i in range(500)]
y_circle = [radius*cos(2*PI*i/500) for i in range(500)]



plt.fill(x_circle, y_circle, edgecolor='y', fill=False)
plt.plot(x,y)
plt.plot(p1_proj[0],p1_proj[1],'r*')
plt.plot(p2_proj[0],p2_proj[1],'r*')
plt.axis('equal')
plt.xlim(-15, 15)
plt.ylim(-15, 15)
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Spherical Projection')
plt.show()
