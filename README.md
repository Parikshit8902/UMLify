UMLify ✨ - Draw UML class diagrams and Get AI Feedback! 🚀

UMLify is an webapp, where users can draw UML class diagrams, and get feedback on it. The aim of this webapp is to simplify the process of Teaching as well as interpreting UML class diagrams, along with providing constructive feedback on it. 📚

We have integrated draw.io interface into our Webapp, providing users the entire functionality of draw.io, helping them create UML class diagrams with ease. 🎨

To provide suggestions and constructive feedback on the class diagrams, we have utilised the capabilities of Llama-3.3-70B model, which we are calling using Groq API. 🤖

To further enhance the output, we have implemented RAG (Retrieval Augmented Generation), which provides output studying a database consisting of 126 UML class diagram files in Markdown format. 📊

The Repo consists of the following files/folders along with their functionalities:

1. RAG.py: RAG implementation, calling model using API. 🛠️
2. app.py: Webapp interface corelating Frontend and Backend. 🌐
3. /static/index.html: Frontend 🎨
4. /md_UML_class_diagrams: UML class diagrams dataset containing Markdown files 📂

To run the application, perform the following steps:

1. Download the repo contents and save all the files at a single location. 📥
2. In app.py, set the path of static as well as drawio directories according to the local path of your system. 🛤️
3. In RAG.py, if you have generated your own API key, then replace it with your own key. 🔑
4. In RAG.py, set the path of dataset in DATASET_PATH accoriding to your local path. 📍
5. Run app.py, and then open the link at the end of the file (http://127.0.0.1:5500) on your web-browser. Now you should see the interface on your system. You can draw UML class diagrams in the interface. ✍️
6. To save the UML class diagram, save it as a draw.io XML on your system. For that, in draw.io interface, go to File -> Save As -> Enter filename.drawio and type of file "XML File (.drwaio)", and save it on your device by selecting "Device" in the "Where" dropdown menu. 💾
7. Now, to get feedback on the UML class diagram, in "Upload Uncompressed Draw.io XML for AI Feedback" section, choose the downloaded file and click "Get AI Feedback" button. 🧠

To close the webapp, first close the browser, and then in terminal of app.py, press Ctrl + c. 🛑
