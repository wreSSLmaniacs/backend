import os

user = "testuser"

os.system('docker run --name cppbox -v "$(pwd)"/codes/{}/:/code --rm -t -d cppenv'.format(user))    # This will start a container
os.system('docker exec -d cppbox bash script.sh')       # This will execute our commands (inside container)

os.system('docker stop cppbox')
os.system('ls codes/testuser')
# os.system('cat codes/testuser/out.txt')