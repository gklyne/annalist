Remove old ":dangling" docker images

    docker rmi $(sudo docker images -f "dangling=true" -q)
