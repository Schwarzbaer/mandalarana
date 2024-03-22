import math
import random
import itertools

from panda3d.core import TransparencyAttrib
from panda3d.core import NodePath

from direct.showbase.ShowBase import ShowBase

from make_models import make_ring

ring_distance = 3.0
ring_rotation = 10.0
ship_speed = 5.0
ShowBase()
base.accept('escape', base.task_mgr.stop)


class Ring:
    def __init__(self, rot_spec, spec):
        up_angle, twist = rot_spec
        self.up_angle = up_angle
        self.twist = twist
        tex_name, segments, color = spec
        # Center of the ring
        self.center = NodePath("center")
        if up_angle == 0.0:
            self.center.set_y(ring_distance)
            self.center.set_r(twist)
        else:
            circumference = 360.0 / up_angle * ring_distance
            radius = circumference / (2.0 * math.pi)
            self.radius = radius
            self.center.set_hpr(0, 0, twist)
            self.center.set_pos(self.center, 0, 0, radius)
            self.center.set_hpr(self.center, 0, up_angle, 0)
            self.center.set_pos(self.center, 0, 0, -radius)
        # The ring itself, which is just decorative
        petals = base.loader.load_texture(tex_name)
        ring = make_ring(segments)
        ring.set_texture(petals)
        ring.set_transparency(TransparencyAttrib.M_binary)
        #ring.set_color(*color)
        ring.reparent_to(self.center)
        self.ring = ring
        self.rotation_direction = random.random() ** 2

    def detach(self):
        self.center.detach_node()

    def reparent_to(self, other_ring):
        self.center.reparent_to(other_ring.center)

    def reparent_to_base(self):
        self.center.reparent_to(base.render)

    def rotate(self, angle):
        self.ring.set_r(self.ring.get_r() + angle * self.rotation_direction)


class Level:
    def __init__(self, course_specs, ring_specs):
        # Setting up the rings
        self.rings = []
        full_specs = zip(course_specs, itertools.cycle(ring_specs))
        for rot_spec, ring_spec in full_specs:
            self.rings.append(Ring(rot_spec, ring_spec))
        for idx, ring in enumerate(self.rings):
            if idx % 2 == 0:
                ring.rotation_direction *= -1

        # Scenegraphifying the rings
        for idx in range(len(self.rings) - 1):
            self.rings[idx + 1].reparent_to(self.rings[idx])

        base.cam.reparent_to(self.rings[0].center)

        # The tunnel task
        base.task_mgr.add(self.movement)

        # Actual game values
        self.advance = 0.0
        self.current_ring = 0

    def movement(self, task):
        self.advance += globalClock.dt * ship_speed
        # Are we still on the same ring?
        new_ring = math.floor(self.advance / ring_distance) % len(self.rings)
        if new_ring != self.current_ring:
            # No, we have changed ring. So let's make the new one the
            # root of the scene graph, and add the one we left behind to
            # the bottom of the graph.
            self.rings[new_ring].detach()
            predecessor = (self.current_ring - 1) % len(self.rings)
            self.rings[self.current_ring].reparent_to(self.rings[predecessor])
            self.current_ring = new_ring
            base.cam.reparent_to(self.rings[new_ring].center)
        # Now we move the camera. How far along are we on this ring's
        # distance?
        local_advance = self.advance % ring_distance
        local_advance_ratio = local_advance / ring_distance
        anti_ratio = 1.0 - local_advance_ratio
        # Now we do the same math that we did to place the ring, but in
        # reverse.
        ring = self.rings[self.current_ring]
        if ring.up_angle == 0.0:
            base.cam.set_pos(0, 0, 0)
            base.cam.set_hpr(0, 0, 0)

            base.cam.set_r(-ring.twist * anti_ratio)
            base.cam.set_y(-ring_distance * anti_ratio)
        else:
            base.cam.set_pos(0, 0, 0)
            base.cam.set_hpr(0, 0, 0)

            base.cam.set_z(base.cam, ring.radius)
            base.cam.set_p(base.cam, -ring.up_angle * anti_ratio)
            base.cam.set_z(base.cam, -ring.radius)
            base.cam.set_r(base.cam, -ring.twist * anti_ratio)

        # Rotate rings
        for idx in range(len(self.rings)):
            ring = self.rings[idx]
            ring.rotate(ring_rotation * globalClock.dt)
        # Dooone!
        return task.cont


ring_specs = [
    ("petal_1.png", 9, (1.0, 0.3, 0.3, 1)),
    ("petal_2.png", 8, (0.1, 0.8, 0.1, 1)),
    ("petal_3.png", 5, (0.8, 0.0, 0.8, 1)),
    ("petal_5.png", 8, (0.5, 1.0, 0.5, 1)),
    ("petal_4.png", 8, (0.8, 0.0, 0.0, 1)),
    ("petal_6.png", 8, (1.0, 1.0, 0.0, 1)),
]
course_spec = []
for i in range(30):
    ratio = float(i) / 30.0
    course_spec.append(
        (
            math.sin(2 * math.pi * ratio),
            10.0
        )
    )
level = Level(course_spec, ring_specs)


base.run()
