import os
import re
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import xml.etree.ElementTree as ET
from RAG import analyze_uml

app = FastAPI()

# Directory setup
static_dir = r"Path_To Static_Directory"
drawio_dir = r"Path_To_Draw.io_Directory"

if not os.path.exists(static_dir):
    raise RuntimeError(f"Static directory '{static_dir}' does not exist.")
if not os.path.exists(drawio_dir):
    raise RuntimeError(f"Draw.io directory '{drawio_dir}' does not exist.")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/drawio-26.1.0/drawio-26.1.0", StaticFiles(directory=drawio_dir), name="drawio")

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"), headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

def extract_uml_info(xml_content: str) -> str:
    try:
        root = ET.fromstring(xml_content)
        # Find the mxGraphModel (the uncompressed XML already contains this structure)
        graph_model = root.find(".//mxGraphModel")
        if graph_model is None:
            raise ValueError("Missing mxGraphModel in XML.")

        cells = graph_model.findall(".//mxCell")

        elements = {}
        relationships = []
        multiplicities = {}
        labels = {}

        # Step 1: Identify classes and their attributes/methods
        for cell in cells:
            cell_id = cell.attrib.get("id")
            value = cell.attrib.get("value", "")
            style = cell.attrib.get("style", "")
            parent = cell.attrib.get("parent")

            # Check if it's a class (swimlane typically represents a class in draw.io UML)
            if "swimlane" in style and value:
                # Extract class name (first line before <br> or HTML tags)
                class_name = re.sub(r"<[^>]+>", "", value.split("<")[0]).strip() if "<" in value else value.strip()
                elements[cell_id] = {"type": "class", "name": class_name, "attributes": [], "methods": []}

                # Find the child cell that contains attributes and methods (usually the first child with text style)
                for child in cells:
                    if child.attrib.get("parent") == cell_id and "text" in child.attrib.get("style", ""):
                        child_value = child.attrib.get("value", "")
                        if child_value:
                            # Clean HTML tags and split by <div> or <br>
                            clean_value = re.sub(r"<[^>]+>", "", child_value)  # Remove all HTML tags
                            lines = [line.strip() for line in clean_value.split("\n") if line.strip()]

                            # Separate attributes and methods
                            for line in lines:
                                # Determine if the line represents a method (contains parentheses)
                                if "(" in line and ")" in line:
                                    # This is a method
                                    method_name = line.strip()
                                    # Remove visibility prefix (+ or -) if present
                                    if method_name.startswith("+") or method_name.startswith("-"):
                                        method_name = method_name[1:].strip()
                                    elements[cell_id]["methods"].append(method_name)
                                else:
                                    # This is an attribute
                                    attr_name = line.strip()
                                    # Remove visibility prefix (+ or -) if present
                                    if attr_name.startswith("+") or attr_name.startswith("-"):
                                        attr_name = attr_name[1:].strip()
                                    elements[cell_id]["attributes"].append(attr_name)

            # Check for multiplicity or relationship labels (text cells)
            if "text" in style and "edgeStyle" not in style and value:
                # Look for parent edge to associate this text with a relationship
                for edge in cells:
                    if edge.attrib.get("edge") == "1" and edge.attrib.get("id") == parent:
                        if re.match(r"^(0|1|\*|\.\.)", value):  # Multiplicity (e.g., 0...*, 1...1)
                            if edge.attrib.get("id") not in multiplicities:
                                multiplicities[edge.attrib.get("id")] = {}
                            # Determine if this multiplicity is near the source or target
                            edge_source = edge.attrib.get("source")
                            edge_target = edge.attrib.get("target")
                            cell_geometry = cell.find("mxGeometry")
                            edge_geometry = edge.find("mxGeometry")
                            if cell_geometry is not None and edge_geometry is not None:
                                cell_y = float(cell_geometry.attrib.get("y", 0))
                                source_y = float(edge_geometry.find("mxPoint[@as='sourcePoint']").attrib.get("y", 0)) if edge_geometry.find("mxPoint[@as='sourcePoint']") is not None else float('inf')
                                target_y = float(edge_geometry.find("mxPoint[@as='targetPoint']").attrib.get("y", 0)) if edge_geometry.find("mxPoint[@as='targetPoint']") is not None else float('inf')
                                # Assign multiplicity to source or target based on proximity
                                if abs(cell_y - source_y) < abs(cell_y - target_y):
                                    multiplicities[edge.attrib.get("id")]["source"] = value
                                else:
                                    multiplicities[edge.attrib.get("id")]["target"] = value
                        else:  # Relationship label (e.g., "Requests and receives ticket")
                            labels[parent] = value

        # Step 2: Identify relationships
        for cell in cells:
            cell_id = cell.attrib.get("id")
            if cell.attrib.get("edge") == "1":
                source = cell.attrib.get("source")
                target = cell.attrib.get("target")
                style = cell.attrib.get("style", "")
                rel_type = "association"

                # Determine relationship type based on style
                if "endArrow=diamond" in style and "endFill=1" in style:
                    rel_type = "aggregation"
                elif "endArrow=block" in style and "endFill=0" in style:
                    rel_type = "inheritance"
                elif "endArrow=block" in style and "endFill=1" in style:
                    rel_type = "composition"
                elif "endArrow=none" in style and "dashed=1" in style:
                    rel_type = "dependency"
                elif "endArrow=open" in style or "endArrow=none" in style:
                    rel_type = "association"

                relationships.append({"from": source, "to": target, "type": rel_type, "id": cell_id})

        # Step 3: Generate simplified text format
        output = []
        for eid, data in elements.items():
            output.append(f"Class: {data['name']}")
            if data["attributes"]:
                output.append("Attributes:")
                for attr in data["attributes"]:
                    output.append(f"- {attr}")
            if data["methods"]:
                output.append("Methods:")
                for method in data["methods"]:
                    output.append(f"+ {method}")
            output.append("")

        for rel in relationships:
            from_class = elements.get(rel["from"], {}).get("name", "Unknown")
            to_class = elements.get(rel["to"], {}).get("name", "Unknown")
            rel_label = labels.get(rel["id"], "")
            multiplicity = multiplicities.get(rel["id"], {})
            source_multiplicity = multiplicity.get("source", "N/A")
            target_multiplicity = multiplicity.get("target", "N/A")
            output.append(f"Relationship: {rel['type']} from {from_class} to {to_class} (Source Multiplicity: {source_multiplicity}, Target Multiplicity: {target_multiplicity}, Label: {rel_label})")

        return "\n".join(output)

    except Exception as e:
        print("❌ Error parsing XML to extract UML info:", str(e))
        return "Could not extract UML information."

@app.post("/upload_xml")
async def upload_xml(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".xml"):
            raise HTTPException(status_code=400, detail="Only XML files are allowed.")

        content = await file.read()
        xml_content = content.decode("utf-8")

        # Directly extract UML info from the uncompressed XML
        simplified_format = extract_uml_info(xml_content)
        print(f"Simplified UML: {simplified_format}")  # Debug print

        feedback = analyze_uml(simplified_format)
        print(f"Feedback from RAG: {feedback}")  # Debug print
        return JSONResponse(content={"feedback": feedback})

    except Exception as e:
        print("❌ Error processing XML file:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5500, reload=True)

#http://127.0.0.1:5500
