import projections
import matplotlib.pyplot as plt

eye_frame = projections.ReferenceFrame([10, 10, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1])
radius = 10
number_of_points = 10
tri = projections.Triangle([11, -18, 30], [20, 48, 5], [10, -10, 1])
tri_proj = tri.spherical_projection_curve(eye_frame, radius, number_of_points)
p1_proj = projections.spherical_projection(tri.p1, eye_frame, radius)
p2_proj = projections.spherical_projection(tri.p2, eye_frame, radius)
p3_proj = projections.spherical_projection(tri.p3, eye_frame, radius)
x = [tri_proj[i][0] for i in range(len(tri_proj))]
y = [tri_proj[i][1] for i in range(len(tri_proj))]

plt.fill(x,y)
plt.plot(p1_proj[0],p1_proj[1],'r*')
plt.plot(p2_proj[0],p2_proj[1],'r*')
plt.plot(p3_proj[0],p3_proj[1],'r*')

plt.axis('equal')
plt.xlim(-1.5*radius, 1.5*radius)
plt.ylim(-1.5*radius, 1.5*radius)
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Spherical Projection')
plt.show()