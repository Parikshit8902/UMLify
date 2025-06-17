import os
import re
#import torch
#from transformers import AutoTokenizer
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests

# Groq API setup
GROQ_API_KEY = "API_KEY"  # Replace with your actual Groq API key
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Paths to pretrained model and dataset
#MODEL_PATH = "Path_To_snapshpts_directory_of_model"  # Optional, for tokenizer
DATASET_PATH = "Path_To_Dataset"  # Update with your dataset path

# Load tokenizer (optional, for consistency with Qwen)
#tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

# Load and process UML dataset
def load_uml_dataset(DATASET_PATH):
    uml_diagrams = []
    file_names = []
    
    for file_name in os.listdir(DATASET_PATH):
        if file_name.endswith('.markdown'):
            file_path = os.path.join(DATASET_PATH, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                uml_blocks = re.findall(r'```(?:plantuml|uml)\n(.*?)\n```', content, re.DOTALL)
                for block in uml_blocks:
                    uml_diagrams.append(block.strip())
                    file_names.append(file_name)
    
    print(f"Loaded {len(uml_diagrams)} UML diagrams from {len(file_names)} files")  # Debug print
    if not uml_diagrams:
        raise ValueError("No UML diagrams found in .md files.")
    
    return uml_diagrams, file_names

# Initialize TF-IDF vectorizer for retrieval
uml_diagrams, file_names = load_uml_dataset(DATASET_PATH)
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(uml_diagrams)

def convert_to_plantuml_format(xml_text: str) -> str:
    """
    Convert the simplified UML text format into a PlantUML-like format for better retrieval.
    Input is expected to be a simplified text format derived from an uncompressed Draw.io XML.
    """
    lines = xml_text.split("\n")
    plantuml_lines = ["@startuml"]
    
    current_class = None
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("Class:"):
            if current_class:
                plantuml_lines.append("}")
            current_class = line.replace("Class:", "").strip()
            plantuml_lines.append(f"class {current_class} {{")
        elif line == "Attributes:":
            continue
        elif line == "Methods:":
            continue
        elif line.startswith("-"):
            attr = line[1:].strip()
            plantuml_lines.append(f"  -{attr}")
        elif line.startswith("+"):
            method = line[1:].strip()
            plantuml_lines.append(f"  +{method}")
        elif line.startswith("Relationship:"):
            parts = line.split()
            rel_type = parts[1]
            from_class = parts[3]
            to_class = parts[5]
            
            if rel_type == "inheritance":
                plantuml_lines.append(f"{from_class} --|> {to_class}")
            elif rel_type == "aggregation":
                plantuml_lines.append(f"{from_class} o--> {to_class}")
            elif rel_type == "composition":
                plantuml_lines.append(f"{from_class} *--> {to_class}")
            elif rel_type == "dependency":
                plantuml_lines.append(f"{from_class} ..> {to_class}")
            else:
                plantuml_lines.append(f"{from_class} --> {to_class}")
    
    if current_class:
        plantuml_lines.append("}")
    plantuml_lines.append("@enduml")
    return "\n".join(plantuml_lines)

def retrieve_context(xml_text: str, top_k=3) -> str:
    """
    Retrieve top-k relevant UML diagrams from the dataset based on similarity to input.
    """
    # Convert the simplified UML text to PlantUML format for better retrieval
    plantuml_text = convert_to_plantuml_format(xml_text)
    input_vector = vectorizer.transform([plantuml_text])
    similarities = cosine_similarity(input_vector, tfidf_matrix).flatten()
    top_k_indices = np.argsort(similarities)[-top_k:][::-1]
    
    context = ["# Retrieved UML Diagrams (Context) - Similarity Scores:"]
    for idx in top_k_indices:
        similarity_score = similarities[idx]
        context.append(f"## From {file_names[idx]} (Similarity: {similarity_score:.4f}):")
        context.append(uml_diagrams[idx])
        context.append("")
    
    return "\n".join(context)

def build_prompt(xml_text: str, context: str) -> str:
    """
    Build a prompt for the Groq API with retrieved context.
    """
    return f"""
You are an expert in software architecture and UML modeling with deep knowledge of design principles and best practices. Your task is to thoroughly analyze the provided UML model, focusing primarily on the UML Input below. Use the retrieved context from similar UML diagrams as a secondary reference to enhance your analysis where relevant (e.g., by comparing class structures, relationships, or design patterns). If the context is limited or unrelated, rely on your expertise in UML best practices to provide a comprehensive and detailed analysis.

## Context (Similar UML Diagrams):
{context}

## UML Input (Simplified Text Format):
{xml_text}

## Instructions:
- Interpret attributes and methods in the UML Input as follows: attributes start with '-', and methods start with '+'. For each attribute or method, identify any additional details like data types (e.g., String, Integer), parameters (e.g., user_info: String), or return types (e.g., : boolean), and include them in your analysis.
- Evaluate the UML model against UML best practices, including proper use of visibility modifiers (public, private, protected), consistency in naming conventions, appropriate use of stereotypes, and alignment with the domain (e.g., a ticket distribution system).
- Assess the design using software engineering principles such as encapsulation, cohesion, coupling, and SOLID principles (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion).
- Provide detailed explanations for each identified issue and suggestion, including their impact on readability, maintainability, scalability, and functionality of the system.

## Expected Output:
### 1. Classes & Attributes:
- List each class along with its attributes and methods as extracted from the UML Input.
- For each class:
  - Comment on the completeness of attributes and methods (e.g., are essential attributes missing?).
  - Evaluate naming conventions (e.g., clarity, consistency, adherence to standards like camelCase or PascalCase).
  - Check for visibility modifiers (e.g., public, private) and suggest adding them if missing.
  - Assess whether the class adheres to the Single Responsibility Principle (e.g., does it have too many responsibilities?).

### 2. Relationships & Multiplicities:
- List all detected relationships, including their type (e.g., association, aggregation, inheritance), source and target classes, multiplicities (if specified), and any labels.
- For each relationship:
  - Evaluate its correctness and appropriateness for the domain (e.g., does an aggregation make sense here?).
  - Check if multiplicities are logical and complete (e.g., should a 1...1 be a 1...*?).
  - Assess whether the relationship supports low coupling and high cohesion.
  - Comment on any missing relationships that could improve the model (e.g., a missing dependency or association).

### 3. Potential Issues:
- Identify and explain issues in the UML model, such as:
  - **Naming Issues**: Inconsistent or unclear names for classes, attributes, methods, or relationships (e.g., typos, non-descriptive names).
  - **Design Issues**: Violations of UML best practices or design principles (e.g., lack of encapsulation, high coupling, low cohesion, SOLID violations).
  - **Completeness Issues**: Missing classes, attributes, methods, or relationships that are essential for the domain.
  - **Domain Appropriateness**: Elements that do not align with the system’s purpose (e.g., a ticket distribution system should have specific features).
- For each issue, explain its impact on the system (e.g., how it affects readability, maintainability, or functionality).

### 4. Scope of Improvement:
- Provide a detailed analysis of how the UML model can be improved, considering the following aspects:
  - **Structural Improvements**: Suggest adding or modifying classes, attributes, methods, or relationships to better represent the system (e.g., introduce a new class for a missing concept).
  - **Design Pattern Applicability**: Recommend design patterns that could enhance the model (e.g., Factory pattern for ticket creation, Observer pattern for transaction updates).
  - **Scalability and Maintainability**: Explain how the model can be made more scalable (e.g., by reducing coupling) and maintainable (e.g., by improving encapsulation).
  - **Domain Alignment**: Suggest changes to better align the model with the domain (e.g., adding validation logic for tickets in a ticket distribution system).
  - **Best Practices**: Recommend adherence to UML best practices (e.g., adding visibility modifiers, using stereotypes for clarity).
- For each suggestion, provide a detailed explanation of how it improves the model, including benefits to readability, maintainability, scalability, and functionality.

### 5. Comparison with Context (Optional):
- If the retrieved context contains relevant UML diagrams, compare the input UML model with the context:
  - Highlight similarities or differences in class structures, relationships, or design approaches.
  - Suggest improvements based on patterns or practices observed in the context (e.g., "The context diagram uses a Factory pattern for ticket creation, which could be applied here").
- If the context is not relevant, skip this section.

Focus on providing a thorough, detailed, and actionable analysis that helps the user improve their UML model. Ensure all suggestions are practical and directly applicable to the given diagram.
    """

def query_groq(prompt: str) -> str:
    """
    Query the Groq API for UML analysis.
    """
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2048,
        "temperature": 1.0,
        "top_p": 0.98
    }

    response = requests.post(GROQ_API_URL, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response from AI.")
    else:
        return f"Error from Groq API: {response.status_code} - {response.text}"

def analyze_uml(xml_text: str) -> str:
    """
    Analyze UML model using RAG with Groq API.
    """
    context = retrieve_context(xml_text, top_k=3)
    prompt = build_prompt(xml_text, context)
    feedback = query_groq(prompt)
    return feedback
