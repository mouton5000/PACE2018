
if grep -Fxq "DEBUG = False" parameters.py
then
  zip -r ../pace2018.zip *.py algos/ dynamicgraphviz/ helpers/ steiner/
else
  echo "Remove debug mode in parameters.py"
fi

