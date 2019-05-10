docker run -it -p 8000:8000 --rm --volumes-from=annalist_site  annalist:0.5.16 bash

# devserver - mounts current working directory of host into /annalist_source in the container system:
# docker run -it -p 8000:8000 -v `pwd`:/annalist_source annalist:0.5.16 bash
