W209 DataViz - Dashboard Ivan Wong, Max Ziff

First:

- Clone this repo:
`git clone git@github.com:donaldziff/w209.git`

- Get the latest database
 - If you're on the ischool server you copy it:
   `cp ~ziff/w209-databases/products.db w209`
 - Or you can get it from the shared google drive:
   https://drive.google.com/drive/folders/1Gy-wKe0bJQyjW8mx4vB70iZVb7NuaG6J
   Look for a file named `products.db`

For your local machine:
- Create a virtual environment with python >=3.7
- Install Dependencies:
  - With PIP: `pip install -r requirements.txt`
  - With Anaconda: `conda install --file requirements.txt`

- Run the web app with
  `python ./run.py`

- For development, it may be easier to run without producing cache:
  `python -B ./run.py`

For the ischool server:
- cd ~
- mv w209 w209.original
- git clone git@github.com:donaldziff/w209.git
- /usr/local/bin/virtualenv w209
- cd w209
- source bin/activate
- pip install `cat requirements.txt`
- touch start.wsgi

Whenever you make a change, touch start.wsgi to force the server to reload

Modifying the database:

We have junglescout data available on google drive. The shared folder
is here https://drive.google.com/drive/folders/1Gy-wKe0bJQyjW8mx4vB70iZVb7NuaG6J.
In that folder is a tarball max0312.tar.gz which contains subdirectories for two JS queries.

Download that file and put it the base directory of this project. Then untar that file:
  `cd input_files && tar tar xvf ../max0312.tar.gz`
The details of those queries are in READMEs.

Run the dataload notebook to create a new product db that holds those results, along with
any other query data you add to the input_files directory. The dataload notebook a new
column `tag` with the name of that subdirectory (or '.') so it's easy to restrict the db
to any subset.
