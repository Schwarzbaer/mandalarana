import random
import itertools

from panda3d.core import TransparencyAttrib
from panda3d.core import NodePath

from direct.showbase.ShowBase import ShowBase

from make_models import make_ring

num_rings = 50
ring_distance = 3.0
ring_rotation = 10.0
ship_speed = 2.0
ShowBase()
base.accept('escape', base.task_mgr.stop)
#base.cam.set_pos(10, -10, 10)
#base.cam.look_at(0,0,0)


class Ring:
    def __init__(self, spec):
        self.center = NodePath("center")
        tex_name, segments, color = spec
        petals = base.loader.load_texture(tex_name)
        ring = make_ring(segments)
        ring.set_texture(petals)
        ring.set_transparency(TransparencyAttrib.M_binary)
        ring.set_color(*color)
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
    def __init__(self, num_rings, tunnel_spec):
        # Setting up the rings
        self.rings = []
        ring_specs = itertools.cycle(tunnel_spec)
        for _ in range(num_rings):
            self.rings.append(Ring(next(ring_specs)))
        for idx, ring in enumerate(self.rings):
            if idx % 2 == 0:
                ring.rotation_direction *= -1

        # Scenegraphifying the rings
        for idx in range(len(self.rings) - 1):
            self.rings[idx + 1].reparent_to(self.rings[idx])
            self.rings[idx + 1].center.set_y(ring_distance)
            self.rings[0].reparent_to_base()

        # The tunnel task
        base.task_mgr.add(self.movement)

    def movement(self, task):
        for idx in range(len(self.rings)):
            ring = self.rings[idx]
            ring.rotate(360.0 / ring_rotation * globalClock.dt)
        ring = self.rings[0]
        ring.center.set_y(ring.center, -globalClock.dt * ship_speed)
        current_y = ring.center.get_y()
        # FIXME: What if we pass two rings in one frame??
        if current_y < 0.0:
            swap_ring = self.rings.pop(0)
            self.rings.append(swap_ring)
            swap_ring.detach()
            front_ring = self.rings[0]
            front_ring.reparent_to_base()
            front_ring.center.set_y(current_y + ring_distance)
            swap_ring.reparent_to(self.rings[num_rings - 2])
            swap_ring.center.set_y(ring_distance)
        return task.cont


ring_specs = [
    ("petal_1.png", 9, (1.0, 0.3, 0.3, 1)),
    ("petal_2.png", 8, (0.1, 0.8, 0.1, 1)),
    ("petal_3.png", 5, (0.8, 0.0, 0.8, 1)),
    ("petal_5.png", 8, (0.5, 1.0, 0.5, 1)),
    ("petal_4.png", 8, (0.8, 0.0, 0.0, 1)),
    ("petal_6.png", 8, (1.0, 1.0, 0.0, 1)),
]
level = Level(50, ring_specs)


base.run()
