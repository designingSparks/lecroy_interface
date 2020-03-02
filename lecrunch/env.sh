THIS=$(dirname ${BASH_ARGV[0]})
LECRUNCH=$(cd ${THIS}; pwd)
export LECRUNCH

# add lecrunch to $PATH and $PYTHONPATH
export PATH=$LECRUNCH:$PATH
export PYTHONPATH=$LECRUNCH:$PYTHONPATH