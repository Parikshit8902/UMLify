UMLify ✨
Draw UML Class Diagrams & Get AI-Powered Feedback! 🚀

UMLify is a dynamic webapp designed to make creating and understanding UML class diagrams a breeze! 📊 Whether you're learning or teaching, UMLify simplifies the process by letting you draw UML class diagrams and receive intelligent, constructive feedback powered by AI. 🧠

Features 🌟
Intuitive Drawing Interface: We've integrated the powerful draw.io interface, giving you access to all its tools to craft UML class diagrams effortlessly. ✏️
AI-Driven Feedback: Our app leverages the Llama-3.3-70B model via the Groq API to provide insightful suggestions and feedback on your diagrams. 🤖
Enhanced with RAG: Using Retrieval Augmented Generation (RAG), UMLify analyzes a dataset of 123 UML class diagram Markdown files to deliver precise and context-aware feedback. 📚
Repository Structure 📂
The repository includes the following files and folders, each with a specific role:

RAG.py 🛠️: Implements RAG and handles API calls to the AI model.
app.py 🌐: Connects the frontend and backend to power the webapp.
/static/index.html 🎨: The frontend interface for drawing and interaction.
/md_UML_class_diagrams 📖: Dataset of 123 UML class diagrams in Markdown format.
Getting Started 🚀
Follow these steps to run UMLify on your system:

Clone the Repository 📥: Download all repo contents and store them in a single folder.
Configure Paths in app.py 🛤️: Update the paths for the static and drawio directories to match your local system.
Set API Key in RAG.py 🔑: Replace the default API key with your own (if applicable).
Update Dataset Path in RAG.py 📍: Set the DATASET_PATH to the location of the md_UML_class_diagrams folder on your system.
Run the App 🏃: Execute app.py, then open the provided link (e.g., http://127.0.0.1:5500) in your web browser.
Draw Your Diagram ✍️: Use the draw.io interface to create your UML class diagram.
Save Your Diagram 💾: Go to File > Save As in the draw.io interface, name your file (e.g., filename.drawio), select XML File (.drawio), choose Device in the "Where" dropdown, and save it locally.
Get AI Feedback 🧠: In the "Upload Uncompressed Draw.io XML for AI Feedback" section, upload your saved .drawio file and click Get AI Feedback.
Shutting Down 🔌
To stop the webapp:

Close your browser. 🌐
In the terminal running app.py, press Ctrl + C. 🛑



