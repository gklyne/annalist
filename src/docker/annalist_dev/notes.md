Remove old "dangling" docker images:

    docker rmi $(docker images -f "dangling=true" -q)

Remove all containers:

   docker rm `docker ps -aq`

Remove all images:

    docker rmi `docker images -aq`


