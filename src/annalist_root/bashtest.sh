echo "BASH_SOURCE: $BASH_SOURCE"

# See: http://stackoverflow.com/questions/59895/

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "DIR: $DIR"

# echo "The script you are running has basename `basename $0`, dirname `dirname $0`"
# echo "The present working directory is `pwd`"

# My variant on above
echo "Using BASH_SOURCE"
echo "The script you are running has basename `basename $BASH_SOURCE`, dirname `dirname $BASH_SOURCE`"
echo "The present working directory is `pwd`"

