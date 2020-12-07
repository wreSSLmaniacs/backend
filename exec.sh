docker run --name cppbox -v "$(pwd)"/codes/testuser/:/code --rm -t -d cppenv
docker exec -d cppbox bash script.sh

docker stop cppbox

ls codes/testuser
cat codes/testuser/out.txt