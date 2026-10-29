from vec import *

PI = 3.14159265359

scene = Scene()

eye_frame = Reference_System([0, 0, 1.7], [1, 0, 0], [0, 1, 0], [0, 0, 1])

radius = 5
spherical = Spherical_Projector(eye_frame, radius, 40)
stereographic = Stereographic_Projector(eye_frame, radius)
cylindrical = Cylindrical_Projector(eye_frame, radius)

focal_distance = 10
ortogonal = Ortographic_Projector(eye_frame, focal_distance)



mesh_floor = Mesh.MeshChessBoard([4, 0, 0], 1)
scene.add_mesh('Scacchiera', mesh_floor)

left_wall = Mesh.MeshChessBoard([4, 4, 4], 1)
left_wall.global_rotate([1, 0, 0], PI/2)
scene.add_mesh('PareteSinistra', left_wall)

right_wall = Mesh.MeshChessBoard([4, -4, 4], 1)
right_wall.global_rotate([1, 0, 0], PI/2)
scene.add_mesh('PareteDestra', right_wall)

front_wall = Mesh.MeshChessBoard([8, 0, 4], 1)
front_wall.global_rotate([0, 1, 0], -PI/2)
scene.add_mesh('PareteFrontale', front_wall)

ceiling = Mesh.MeshChessBoard([4, 0, 8], 1)
ceiling.global_rotate([0, 1, 0], PI)
scene.add_mesh('Soffitto', ceiling)

red_box = Mesh.MeshCube([2, -2.5, 3], 1,  [255, 0, 0])
scene.add_mesh('redBox', red_box)


light_direction = normalized([1, -2, -3])
sun = Light_Source(light_direction)
scene.add_light_source('Sun', sun)


cam = Camera(radius*PI*1.1, radius*2, cylindrical)
scene.add_camera('Camera', cam)

print(angle([1, 0, 0], [0, 1, 0]))


def animation_function(frame, scene, camera, fps):
    print("drawing frame", frame, "out of", fps*10)
    delta_t = 1/fps

    redBox = scene.meshes['redBox']
    redBox_velocity = 0.5
    redBox.global_translate([0, redBox_velocity*delta_t, 0])
    redBox_angular_velocity = PI/2
    redBox.global_rotate([1, 2, 3], redBox_angular_velocity*delta_t)


scene.animate('Camera', animation_function, fps=30, duration=10, animation_name='prova.gif')
