# ChairStore
### By Narendra Reddy
This is the second project of Udacity [FSND Course](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).

### Project Description
ChairStore is an application which has chair categories, each category consists of different kinds of chairs  as well as it has google oauth2 for user registration.The authenticated users will have the chance to add, edit and delete of his own item and category only.

#### Requirements for project
  * [Python](https://www.python.org/downloads)
  * [Vagrant](https://www.vagrantup.com/)
  * [VirtualBox](https://www.virtualbox.org/)
  * [Git](https://git-scm.com/downloads) - for windows
  
#### Project Setup:
  1. Vagrant Installation
  2. VirtualBox Installation
  3. Clone or Download [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm) repository.
  4. Unzip the above vagrant zip folder and open it
  5. Place the ChairStore folder into the above vagrant folder
  
#### Project Execution
  1. From vagrant folder open gitbash
  2. Use this command to Launch the Vagrant 
  ``` $ vagrant up ```
  3. Use this command to Log into Vagrant
    ``` $ vagrant ssh ```
  4. Then move vagrant folder by using the commmand
    ``` $ cd /vagrant ```
  5. Move ChairStore to project folder by using the command
    ``` $ cd ChairStore ```
  6. Use this command to run the project
    ``` $ python Catalog.py ```
  10. open the application in the browser by using[http://localhost:5000](http://localhost:5000).
  ### JSON end points
  In this application we created json end points
#### urls:
``` http://localhost:5000/chairs/category/json ```
``` http://localhost:5000/chairs/all.json ```
``` http://localhost:5000/chairs/category/3/items.json ```