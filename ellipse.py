# ELLIPSE PARAMETRIC EQUATION GIVEN a, b, theta, xC, yC
# x(alpha) = a*cos(angle)*cos(theta)-b*sin(angle)*sin(theta)+xC
# y(alpha) = a*cos(angle)*sin(theta)+b*sin(angle)*cos(theta)+yC

# ELLIPSE INVERSE PARAMETRIC GIVEN a, b, theta, xC, yC
# alpha(x, y) = atan2(((y-yC)*cos(theta)-(x-xC)*sin(theta))/b, ((x-xC)*cos(theta)+(y-yC)*sin(theta))/a)

def ellipse_from_spherical_projection(p1, p2, eye_frame, radius):