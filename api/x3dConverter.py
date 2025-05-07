import json
import math
import numpy as np


def vector_sub(a, b):
    return {'x': b['x'] - a['x'], 'y': b['y'] - a['y'], 'z': b['z'] - a['z']}


def vector_length(v):
    return math.sqrt(v['x']**2 + v['y']**2 + v['z']**2)


def make_billboard_with_background(text, position, font_size=0.3, padding=0.2):
    x, y, z = position

    # Estimate dimensions
    text_width = len(text) * font_size * 0.6
    text_height = font_size
    box_width = text_width + padding
    box_height = text_height + padding
    box_depth = 0.01

    return f"""
<Transform translation='{x} {y} {z}'>
  <Billboard>

    <!-- Background Box -->
    <Transform translation='0 0 -0.01'>
      <Shape>
        <Appearance>
          <Material diffuseColor='0 0 0' transparency='0.5'/>
        </Appearance>
        <Box size='{box_width} {box_height} {box_depth}'/>
      </Shape>
    </Transform>

    <!-- Text Label Centered -->
    <Transform translation='{-text_width/2} {-text_height/2} 0'>
      <Shape>
        <Appearance>
          <Material diffuseColor='1 1 1'/>
        </Appearance>
        <Text string='"{text}"'>
          <FontStyle size='{font_size}'/>
        </Text>
      </Shape>
    </Transform>

  </Billboard>
</Transform>
"""


def create_x3d_node(node):
    shape_map = {
        "cube": "Box",
        "sphere": "Sphere",
        "capsule": "Cylinder",  # X3D lacks capsule primitive
        "cylinder": "Cylinder",
        "plane": "Box",  # Treat plane and quad as flat boxes
        "quad": "Box"
    }
    shape = shape_map.get(node["type"], "Box")
    pos = node["position"]
    rot = node["rotation"]
    scale = {k: v / 2 for k, v in node["scale"].items()}
    color = node["color"]
    label_y_offset = scale['y'] + 0.5  # Offset for the label above the object
    if node["type"] == "plane":
        scale['x'] = 1.0
        scale['y'] = 0.01
        scale['z'] = 1.0
    node["name"] = node["name"].replace("&", "+")
    return f"""
<Transform translation='{pos['x']} {pos['y']} {pos['z']}'
          rotation='0 1 0 {math.radians(rot['y'])}'
          scale='{scale['x']} {scale['y']} {scale['z']}'>
  <Shape>
    <Appearance>
      <Material diffuseColor='{color['r']} {color['g']} {color['b']}' transparency='{1 - color['a']}'/>
    </Appearance>
    <{shape}/>
  </Shape>
</Transform>
""" + make_billboard_with_background(node["name"], position = (pos['x'], pos['y'] + label_y_offset, pos['z']), font_size=0.2)


def compute_rotation(from_vec, to_vec):
    from_vec = np.array(from_vec)
    to_vec = np.array(to_vec)
    from_vec = from_vec / np.linalg.norm(from_vec)
    to_vec = to_vec / np.linalg.norm(to_vec)
    axis = np.cross(from_vec, to_vec)
    angle = np.arccos(np.clip(np.dot(from_vec, to_vec), -1.0, 1.0))
    
    if np.linalg.norm(axis) < 1e-6:
        if angle < 1e-6:
            return (0, 1, 0, 0)  # no rotation
        else:
            return (1, 0, 0, np.pi)  # 180 degrees
    axis = axis / np.linalg.norm(axis)
    return (*axis, angle)


def create_x3d_edge(source_node, target_node):
    p1 = np.array([source_node["position"][k] for k in ("x", "y", "z")])
    p2 = np.array([target_node["position"][k] for k in ("x", "y", "z")])
    direction = p2 - p1
    length = np.linalg.norm(direction)
    midpoint = (p1 + p2) / 2
    shaft_rot = compute_rotation((0, 1, 0), direction)
    cone_rot = compute_rotation((0, 1, 0), direction)

    # Shaft (cylinder)
    shaft = f"""
<Transform translation='{midpoint[0]} {midpoint[1]} {midpoint[2]}'
        rotation='{shaft_rot[0]} {shaft_rot[1]} {shaft_rot[2]} {shaft_rot[3]}'
        scale='0.05 {length / 2} 0.05'>
<Shape>
    <Appearance>
    <Material diffuseColor='1 1 1'/>
    </Appearance>
    <Cylinder/>
</Shape>
</Transform>
"""

    # Arrowhead (cone)
    arrow_offset = (direction / length) * 0.5
    cone_pos = p2 - arrow_offset 
    cone = f"""
<Transform translation='{cone_pos[0]} {cone_pos[1]} {cone_pos[2]}'
        rotation='{cone_rot[0]} {cone_rot[1]} {cone_rot[2]} {cone_rot[3]}'
        scale='0.2 0.4 0.2'>
<Shape>
    <Appearance>
    <Material diffuseColor='1 1 1'/>
    </Appearance>
    <Cone/>
</Shape>
</Transform>
"""
    return shaft + cone


def json_to_x3d(json_data):
    nodes = {node["name"]: node for node in json_data["nodes"]}
    x3d_nodes = [create_x3d_node(n) for n in nodes.values()]
    x3d_edges = ""
    if "edges" in json_data:
        for e in json_data["edges"]:
            e["source"] = e["source"].replace("&", "+")
            e["target"] = e["target"].replace("&", "+")
        x3d_edges = [create_x3d_edge(nodes[e["source"]], nodes[e["target"]])
                     for e in json_data["edges"]
                     if e["source"] in nodes and e["target"] in nodes]
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<X3D profile="Immersive" version="3.3" xmlns:xsd="http://www.w3.org/2001/XMLSchema-instance">
  <Scene>
    <Background skyColor='0.3 0.7 1.0'/>
    {"".join(x3d_nodes)}
    {"".join(x3d_edges)}
  </Scene>
</X3D>
"""

