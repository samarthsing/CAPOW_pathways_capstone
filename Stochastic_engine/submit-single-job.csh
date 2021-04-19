#/bin/tcsh

# Set up python environment
conda activate /usr/local/usrapps/infews/CAPOW_env

   	bsub -W 5000 -x -o out.%J -e err.%J "python stochastic_engine_partial.py"

conda deactivate
