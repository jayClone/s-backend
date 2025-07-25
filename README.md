# Farm-Stack-Backend-Template
This is Farm Stack Backend Template with Production Version Routing Support, Two Way Room Based Communication (Socket IO) All Working With Latest Version Packages Support and Extensible Template

## Setup 

1. Create a Virtual Environment
```
python -m venv venv
```
2. Now Activate the environment

windows :  
```
venv\Scripts\activate
```
linux :
```
venv\Scripts\activate.sh
```

3. Configure the Port you want to use in server.py

4. install req.txt using Pip
```
pip install -r req.txt
```

5. Now run Server.py
```
python server.py
```

## Folder Structure

```
📦Farm-Stack-Backend-Template
 ┣
 ┣ 📂api                 ⊙ This is Base API folder
 ┃ ┣ 📂db                ⊙ Demo DB configuration
 ┃ ┃ ┗ 📜__init__.py
 ┃ ┣ 📂extensions        ⊙ Extension Folder. Make Extensions Here
 ┃ ┃ ┣ 📂discord
 ┃ ┃ ┃ ┗ 📜discordBot.py  
 ┃ ┃ ┗ 📂etc             
 ┃ ┣ 📂models            ⊙ This is Models folder to Store Schema of Objects
 ┃ ┃ ┗ 📜Room.py         
 ┃ ┣ 📂socket            ⊙ Base Folder for Sockets 
 ┃ ┃ ┗ 📜__init__.py     ⊙ You can Configure more Socket events in this. 
 ┃ ┗ 📂versions          ⊙ Manage API version in this.
 ┃ ┃ ┣ 📂v1              ⊙ Version 1 File Development goes here
 ┃ ┃ ┃ ┣ 📂room          ⊙ Files Related to Room Management Goes here
 ┃ ┃ ┃ ┃ ┗ 📜root.py     ⊙ Root File for Rooms management
 ┃ ┃ ┃ ┗ 📜__init__.py   ⊙ This is API Version 1 Base File 
 ┃ ┃ ┣ 📂v2              ⊙ Version 2 Api files Goes here 
 ┃ ┃ ┃ ┗ 📜__init__.py   ⊙ This Is Demo Of Version 2 Configuration
 ┃ ┃ ┗ 📜__init__.py     ⊙ This is Base file Of API Version Management Add New Versions Using This
 ┣ 📂static              ⊙ This is Static Folder to Store Static Files
 ┃ ┗ 📜socket.io.min.js  ⊙ Dont remove this File It is needed For Long Polling
 ┣ 📜bind.py             ⊙ It Binds API , Socket You Can Configure Middlewares in this File or JWT configuration
 ┣ 📜devices.db          ⊙ This is Sqlite database for the default room Management example
 ┣ 📜req.txt             ⊙ Install these Packages
 ┣ 📜server.py           ⊙ Configure Port in this
 ┗ 📜z.bat               ⊙ Auto Start Script for Windows after venv configuration
```
