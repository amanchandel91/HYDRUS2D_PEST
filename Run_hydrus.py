import os
import numpy as np
import re
import pandas as pd

# Get the current working directory
current_dir = os.getcwd()

# Get a list of all directories in the current directory
dirs = [d for d in os.listdir() if os.path.isdir(d)]
# Defining hydrus permanent working directory
   
# Check if there is at least one directory
if dirs:
    # Use the first directory as the value of my_variable
    work_dir = dirs[0]
else:
    # No directories found
    work_dir = ''
   

# Create batch file in the current directory
# Define the commands as a string
batch_file = f'''@echo off
(
    echo Running Hydrus on %cd%\\{work_dir}
    echo %cd%\\{work_dir} > LEVEL_01.dir
    %1 < %2
)'''
# Open a new file in write mode
with open(os.path.join(current_dir, 'run_hydrus.bat'), 'w') as run:
    run.write(batch_file)

# Create return file in the current directory
with open(os.path.join(current_dir, 'return.txt'), 'w') as ret:
    ret.write('return')

# Open the input file in read mode for selector.in
with open('input.dat', 'r') as inp:
    # Read the values from the file and convert them to floats
    values = [float(line.strip()) for line in inp if line.strip()]

# Open the Selector_1.in in read mode
with open(os.path.join(current_dir, work_dir, 'Selector_1.in'), 'r') as f:
    # Read the contents of the file

    Selector_1 = f.read()
w = 0.3
# Replace the variables in the Selector_1.in with values from the input file
# Use {variable_name} as a placeholder in Selector_1.in where you want to insert the values
Ka = values[1]*(1-w) + values[3]*w
variable_name = [ 'ths', 'Ks', 'thFr', 'KsFr', 'DisperL', 'DisperT', 'ThImob',
                 'DispF','Alfa']
values_dict = dict(zip(variable_name, values))
values_dict['Ka'] = Ka
Selector = Selector_1.format(**values_dict)

# Open the Selector.in file in write mode
with open(os.path.join(current_dir, work_dir, 'SELECTOR.IN'), 'w') as f:
    # Write the output to the file
    f.write(Selector)

# Execute Hydrus batch file
os.system('cmd /c "run_hydrus "C:\Program Files\PC-Progress\HYDRUS 5.01 64-bit\Bin\H2D_Dual64.exe" return.txt"')

with open(os.path.join(current_dir, work_dir,'ObsNod.out'), 'r') as f:
    # Read the contents of the file into a list of lines
    ObsNod_lines = f.readlines()

with open(os.path.join(current_dir, work_dir,'ObsNodF.out'), 'r') as f:
    # Read the contents of the file into a list of lines
    ObsNodF_lines = f.readlines()

# Define the line numbers to delete (0-indexed)
lines_to_delete = [1, 2, 3, 4, 5]

# Remove the first five lines and the last line
ObsNod_lines = [line for i, line in enumerate(ObsNod_lines) if i not in range(6) and i != len(ObsNod_lines)-1]
ObsNodF_lines = [line for i, line in enumerate(ObsNodF_lines) if i not in range(6) and i != len(ObsNodF_lines)-1]

# Convert the lists of lines into numpy arrays
ObsNod = np.array([line.split() for line in ObsNod_lines], dtype=float)
ObsNodF = np.array([line.split() for line in ObsNodF_lines], dtype=float)

# Create a new numpy array that contains the first and fifth columns of the ObsNod array
BTC_Mat = ObsNod[:, [0, 4]]
BTC_Fra = ObsNodF[:, [0, 4]]

qf = 8.123
qm = 18.954
BTC_sim = (w*BTC_Fra*qf+(1-w)*BTC_Mat*qm)/(w*qf+(1-w)*qm);

# Reading Experimental Values and extracting similar time stamp values of
# simulated data
Exp_BTC = np.loadtxt(os.path.join(current_dir,'exp_BTC.txt'))
Exp_Zeroth = np.cumsum(Exp_BTC[:, 0] * Exp_BTC[:, 1])
# Writing Cumulative zeroth temporal moment of the exp data in a file
np.savetxt('zeroth_Exp.txt', Exp_Zeroth)
l = len(Exp_BTC)
ade1 = np.zeros((l, BTC_sim.shape[1]))
BTC = np.zeros((l, BTC_sim.shape[1]))
for i in range(l):
    val, idx = min((val, idx) for (idx, val) in enumerate(abs(BTC_sim[:, 0] - Exp_BTC[i, 0])))
    BTC[i, :] = BTC_sim[idx, :]
# Writing Simulated BTC in a file
np.savetxt('Sim_BTC.txt', BTC)
# Calculation of Cumulative zeroth temporal moment
Sim_Zeroth = np.sum(BTC[:, 0] * BTC[:, 1])
Sim_first = np.sum(BTC[:, 0]**2 * BTC[:, 1])/2
Sim_second = np.sum(BTC[:, 0]**3 * BTC[:, 1])/3
Sim_first_norm = Sim_first/Sim_Zeroth
Sim_second_norm = (Sim_second/Sim_Zeroth)-((Sim_first/Sim_Zeroth)**2)
# Writing Cumulative zeroth temporal moment of simulated data in a file
np.savetxt('output.dat', BTC[:, 1])
