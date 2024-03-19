from panda3d.core import InternalName
from panda3d.core import NodePath
from panda3d.core import Geom
from panda3d.core import GeomNode
from panda3d.core import GeomVertexArrayFormat
from panda3d.core import GeomVertexFormat
from panda3d.core import GeomVertexData
from panda3d.core import GeomVertexWriter
from panda3d.core import GeomTriangles
from panda3d.core import Point3


root = NodePath("root")
turtle = root.attach_new_node("turtle")


def make_ring(segments=32):
    # Defining the vertex array
    v_array_format = GeomVertexArrayFormat()
    v_array_format.add_column(
        InternalName.get_vertex(),
        3,
        Geom.NT_float32,
        Geom.C_point,
    )
    v_array_format.add_column(
        InternalName.get_texcoord(),
        2,
        Geom.NT_float32,
        Geom.C_texcoord,
    )
    v_format = GeomVertexFormat()
    v_format.add_array(v_array_format)
    v_format = GeomVertexFormat.register_format(v_format)

    # Creating the vertices
    v_data = GeomVertexData("Data", v_format, Geom.UH_static)
    v_data.unclean_set_num_rows((segments + 1) * 2)

    vertex = GeomVertexWriter(v_data, InternalName.get_vertex())
    texcoord = GeomVertexWriter(v_data, InternalName.get_texcoord())
    tris = GeomTriangles(Geom.UHStatic)

    for s in range(segments + 1):
        ratio = float(s) / float(segments)
        turtle.set_r(360.0 * ratio)
        vertex.set_data3f(
            turtle.get_relative_point(
                root,
                Point3(0, 0, -0.7),
            ),
        )
        texcoord.set_data2f(ratio, 1.0)
        vertex.set_data3f(
            turtle.get_relative_point(
                root,
                Point3(0, 0, -2.0),
            ),
        )
        texcoord.set_data2f(ratio, 0.0)
        if s > 0:
            base_vert = (s - 1) * 2
            tl = base_vert + 0
            bl = base_vert + 1
            tr = base_vert + 2
            br = base_vert + 3
            tris.add_vertices(tl, bl, tr)
            tris.add_vertices(tr, bl, br)

    # Packaging it all up
    geom = Geom(v_data)
    geom.add_primitive(tris)
    node = GeomNode('geom_node')
    node.add_geom(geom)
    return NodePath(node)
