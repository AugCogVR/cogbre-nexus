import sys
from mcp.server.fastmcp import FastMCP
import json
import requests

# REF: https://modelcontextprotocol.io/quickstart/server 

# Initialize FastMCP server
mcp = FastMCP("cogbre")


@mcp.tool()
async def add_graph(payload:dict) -> str:
    """Add a graph to the virtual reality (VR) scene.
     
    Inputs: 
        Provide a JSON object containing the following information:
        - This object has a single key called "payload" and its value is a dict 
        - The dictionary assigned to "payload" shall contain:
            - payload_type: a string that shall be "graph"
            - id: string containing a unique name for this graph so you can refer to it later
            - nodes: a list of graph nodes adhering to the format described below
            - edges: a list of graph edges adhering to the format described below

        - Nodes: Each node object in the list of nodes shall have the following attributes:
            - name: a unique string representing a descriptive name of the object
            - type: A string representing the type of 3D object. Acceptable types are: cube, sphere, capsule, cylinder, plane, quad.
            - position: An object with x, y, and z attributes representing the 3D coordinates of the object. 
              NOTE: These objects will be instantiated in Unity, where the Y axis is “up.” All objects should
              be created above the ground plane (all Y values should be positive).  
            - rotation: An object with x, y, and z attributes representing the rotation in degrees along each axis.
            - scale: An object with x, y, and z attributes representing the size of the object.
            - color: An object with r, g, b, and a attributes representing the color of the object (using values between 0 and 1 for each component, with a for transparency).

        - Edges: Each edge object in the list of edges shall have the following attributes: 
            - source: a string containing the name of the source node
            - target: a string containing the name of the target node 

        Example of a JSON graph containing two nodes:
            {        
                "payload_type": "graph",
                "id": "simple_graph_123",
                "nodes": 
                [
                {
                    “name”: “fun cube”
                    "type": "cube",
                    "position": { "x": 0, "y": 1, "z": 0 },
                    "rotation": { "x": 0, "y": 45, "z": 0 },
                    "scale": { "x": 1, "y": 1, "z": 1 },
                    "color": { "r": 1, "g": 0, "b": 0, "a": 1 },
                },
                {
                    “name”: “serious sphere”
                    "type": "sphere",
                    "position": { "x": 3, "y": 1, "z": 0 },
                    "rotation": { "x": 0, "y": 0, "z": 0 },
                    "scale": { "x": 1, "y": 1, "z": 1 },
                    "color": { "r": 0, "g": 1, "b": 0, "a": 1 },
                }
                ]
                "edges":
                [
                {
                    "source": "fun cube",
                    "target": "serious sphere"
                }
                ]
            }

    Returns: 
        String indicating whether or not the action was successful
    """
    print(f"COGBRE MCP SERVER: add_graph sending payload: {payload}", file=sys.stderr)
    send_payload_to_nexus(json.dumps(payload))
    return "Success"

@mcp.tool()
async def remove_graph(id:str) -> str:
    """Remove a graph from the virtual reality (VR) scene.
     
    Inputs: 
        The ID of the graph as provided when the graph was created.

    Returns: 
        String providing the ID of the graph for future reference to this graph.
    """
    print(f"COGBRE MCP SERVER: remove_graph sending payload: {id}", file=sys.stderr)
    # send_payload_to_nexus(json.dumps(scene))
    return "Success"

@mcp.tool()
async def add_visualization(payload:dict) -> str:
    """Add a visualization to the VR scene expressed as a list of 3D geometric primitives.
     
    Inputs: 
        Provide a JSON object containing the following information:
        - This object has a single key called "payload" and its value is a dict 
        - The dictionary assigned to "payload" shall contain:
            - payload_type: a string that shall be "vis"
            - id: string containing a unique name for this visualization so you can refer to it later
            - primitives: a list of 3D primitives adhering to the format described below

        - Primitives: Each primitive object in the list of primitives shall have the following attributes:
            - name: a unique string representing a descriptive name of the object
            - type: A string representing the type of 3D object. Acceptable types are: cube, sphere, capsule, cylinder, plane, quad.
            - position: An object with x, y, and z attributes representing the 3D coordinates of the object. 
              NOTE: These objects will be instantiated in Unity, where the Y axis is “up.” All objects should
              be created above the ground plane (all Y values should be positive).  
            - rotation: An object with x, y, and z attributes representing the rotation in degrees along each axis.
            - scale: An object with x, y, and z attributes representing the size of the object.
            - color: An object with r, g, b, and a attributes representing the color of the object (using values between 0 and 1 for each component, with a for transparency).

        Example of a JSON scene containing a cube and a sphere:
            {
                "payload_type": "vis",
                "id": "simple_vis_123",
                "primitives": 
                [
                {
                    "type": "cube",
                    "position": { "x": 0, "y": 1, "z": 0 },
                    "rotation": { "x": 0, "y": 45, "z": 0 },
                    "scale": { "x": 1, "y": 1, "z": 1 },
                    "color": { "r": 1, "g": 0, "b": 0, "a": 1 },
                    “name”: “fun cube”
                },
                {
                    "type": "sphere",
                    "position": { "x": 3, "y": 1, "z": 0 },
                    "rotation": { "x": 0, "y": 0, "z": 0 },
                    "scale": { "x": 1, "y": 1, "z": 1 },
                    "color": { "r": 0, "g": 1, "b": 0, "a": 1 },
                    “name”: “serious sphere”
                }
                ]
            }

    Returns: 
        String indicating whether or not the visualization was accepted
    """
    print(f"COGBRE MCP SERVER: add_visualization sending payload: {payload}", file=sys.stderr)
    send_payload_to_nexus(json.dumps(payload))
    return "Success"

def send_payload_to_nexus(payload):
    # TODO: Determine actual session ID
    messageJSON = { "sessionId": "unknown", "command": ["push_ai_payload", payload]}
    response = requests.post("http://127.0.0.1:5000/ai_sync", json = messageJSON)
    print(f"COGBRE MCP SERVER: response after sending payload to Nexus: {response}", file=sys.stderr)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')

