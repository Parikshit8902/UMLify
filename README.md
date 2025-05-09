UMLify ✨

Draw UML Class Diagrams & Get AI-Powered Feedback! 🚀

UMLify is a dynamic webapp designed to make creating and understanding UML class diagrams a breeze! 📊 
Whether you're learning or teaching, UMLify simplifies the process by letting you draw UML class diagrams and receive intelligent, constructive feedback powered by AI. 🧠

Features 🌟
1. Intuitive Drawing Interface: We've integrated the powerful draw.io interface, giving you access to all its tools to craft UML class diagrams effortlessly. ✏️
2. AI-Driven Feedback: Our app leverages the Llama-3.3-70B model via the Groq API to provide insightful suggestions and feedback on your diagrams. 🤖
3. Enhanced with RAG: Using Retrieval Augmented Generation (RAG), UMLify analyzes a dataset of 123 UML class diagram Markdown files to deliver precise and context-aware feedback. 📚

Repository Structure 📂
The repository includes the following files and folders, each with a specific role:

1. RAG.py 🛠️: Implements RAG and handles API calls to the AI model.
2. app.py 🌐: Connects the frontend and backend to power the webapp.
3. /static/index.html 🎨: The frontend interface for drawing and interaction.
4. /md_UML_class_diagrams 📖: Dataset of 123 UML class diagrams in Markdown format.
   
Getting Started 🚀
Follow these steps to run UMLify on your system:

1. Clone the Repository 📥: Download all repo contents and store them in a single folder.
2. Configure Paths in app.py 🛤️: Update the paths for the static and drawio directories to match your local system.
3. Set API Key in RAG.py 🔑: Replace the default API key with your own (if applicable).
4. Update Dataset Path in RAG.py 📍: Set the DATASET_PATH to the location of the md_UML_class_diagrams folder on your system.
5. Run the App 🏃: Execute app.py, then open the provided link (e.g., http://127.0.0.1:5500) in your web browser.
6. Draw Your Diagram ✍️: Use the draw.io interface to create your UML class diagram.
7. Save Your Diagram 💾: Go to File > Save As in the draw.io interface, name your file (e.g., filename.drawio), select XML File (.drawio), choose Device in the "Where" dropdown, and save it locally.
8. Get AI Feedback 🧠: In the "Upload Uncompressed Draw.io XML for AI Feedback" section, upload your saved .drawio file and click Get AI Feedback.
   
Shutting Down 🔌
To stop the webapp:
1. Close your browser. 🌐
2. In the terminal running app.py, press Ctrl + C. 🛑
