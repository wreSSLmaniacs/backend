docker run --name pybox -v "$(pwd)"/codes/testuser/:/code --rm -t -d pyenv
docker exec -d pybox bash ./script.sh

docker stop pybox

ls codes/testuser
cat codes/testuser/out.txt