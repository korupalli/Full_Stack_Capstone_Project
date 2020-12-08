# Installation Guide

Download Instructions

1.	Download ZIP code from git repository: https://github.com/unsw-cse-capstone-project/capstone-project-comp9900-h12a-5star  
2.	Save the zip file in your directory folder
3.	Go to the directory folder where zip file is saved, unzip/extract the zip file

Build and Run Backend Server

1.	Open command prompt in Windows or terminal in Linux/Mac OS.
2.	Go to the root directory of the application.
3.	Now, cd to the api folder 
4.	We will now upgrade pip and install all the python library dependencies in a python environment by using the below commands. The screenshots are taken from VLAB terminal. Run the below commands in the given order.

•	python3 -m pip install --upgrade pip

•	python3 -m pip install --user --upgrade pip

•	python3 -m pip install --user virtualenv

•	python3 -m venv env

•	source env/bin/activate 

•	python3 -m pip install -r requirement.txt

5.	Now, in the same terminal run this command to run the backend server

•	python3 manage.py runserver

6.	The backend server should be up and running. The next step to build and run frontend server while the backend server is still running.

Build and Run Frontend Server

1.	Open command prompt in Windows or terminal in Linux/Mac OS.
2.	Go to the root directory of the application.
3.	Now, cd to the web folder
4.	Now install the Node.js dependencies. Run the below command.
•	npm install

5.	Run the frontend server.
•	npm start 

