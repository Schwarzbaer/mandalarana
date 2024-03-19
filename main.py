import random

from panda3d.core import TransparencyAttrib
from panda3d.core import NodePath

from direct.showbase.ShowBase import ShowBase

from make_models import make_ring

num_rings = 50
ring_distance = 1.5
ring_rotation = 10.0
ship_speed = 1.0
ShowBase()
base.accept('escape', base.task_mgr.stop)
#base.cam.set_pos(10, -10, 10)
#base.cam.look_at(0,0,0)


class Ring:
    def __init__(self):
        self.center = NodePath("center")
        petals = base.loader.load_texture("simple_petals.png")
        ring = make_ring()
        ring.set_texture(petals)
        ring.set_transparency(TransparencyAttrib.M_binary)
        ring.set_color(
            random.random(),
            random.random(),
            random.random(),
            1,
        )
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


rings = [Ring() for _ in range(num_rings)]
for idx, ring in enumerate(rings):
    if idx % 2 == 0:
        ring.rotation_direction *= -1
        
for idx in range(len(rings) - 1):
    rings[idx + 1].reparent_to(rings[idx])
    rings[idx + 1].center.set_y(ring_distance)
    rings[0].reparent_to_base()


def movement(task):
    for idx in range(len(rings)):
        ring = rings[idx]
        ring.rotate(360.0 / ring_rotation * globalClock.dt)
    ring = rings[0]
    ring.center.set_y(ring.center, -globalClock.dt * ship_speed)
    current_y = ring.center.get_y()
    # FIXME: What if we pass two rings in one frame??
    if current_y < 0.0:
        swap_ring = rings.pop(0)
        rings.append(swap_ring)
        swap_ring.detach()
        front_ring = rings[0]
        front_ring.reparent_to_base()
        front_ring.center.set_y(current_y + ring_distance)
        swap_ring.reparent_to(rings[num_rings - 2])
        swap_ring.center.set_y(ring_distance)
    return task.cont


base.task_mgr.add(movement)
base.run()
