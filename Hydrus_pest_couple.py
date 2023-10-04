import os
import numpy as np
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
os.system('Run_hydrus.py')



# Pest files generation
# Creating input.tpl and input.par
with open(os.path.join(current_dir, 'input.tpl'), 'w') as f1, open(os.path.join(current_dir, 'input.par'), 'w') as f2:
    f1.write('ptf #\n')
    f2.write('single point\n')
    for i in variable_name:
        user_in1 = input(f'{i} Est(E)/Discrete(D):')
        if user_in1.lower() == 'e':
            f1.write(f'# {i} #\n')
            f2.write(f'{i} {values_dict[i]} 1 0\n')
        else:
            f1.write(f'{values_dict[i]}\n')
        #else:
        #   print('Invalid input')
    
os.system('cmd /k "tempchek input.tpl"')
os.system('cmd /k "tempchek input.tpl input.dat input.par"')

# Open the experimental data in read mode
Exp_BTC = np.loadtxt(os.path.join(current_dir,'exp_BTC.txt'))
Cum_Exp_Zeroth = np.cumsum(Exp_BTC[:, 0] * Exp_BTC[:, 1])
Exp_Zeroth = np.sum(Exp_BTC[:, 0] * Exp_BTC[:, 1])
Exp_first = np.sum(Exp_BTC[:, 0]**2 * Exp_BTC[:, 1])/2
Exp_second = np.sum(Exp_BTC[:, 0]**3 * Exp_BTC[:, 1])/3
Exp_first_norm = np.sum(Exp_first/Exp_Zeroth)
Exp_second_norm = np.sum((Exp_second/Exp_Zeroth)-((Exp_first/Exp_Zeroth)**2))

print(Exp_Zeroth)
print(Exp_first)
print(Exp_second)
print(Exp_first_norm)
print(Exp_second_norm)
l = len(Exp_BTC)

# Creating output.ins, output.dat and running check
with open(os.path.join(current_dir, 'output.ins'), 'w') as f:
    f.write('pif #\n')
    # Write number of data of zeroth temporal moment to the file
    for i in range(l):
        f.write(f'l1 (o{i+1})19:26\n')
with open(os.path.join(current_dir, 'measure.obf'), 'w') as f:
    # Write experimental zeroth temporal moment to the file
    for i in range(l):
        f.write(f'o{i+1} {Exp_BTC[i,1]}\n')
os.system('cmd /k "inschek output.ins"')
os.system('cmd /k "inschek output.ins output.dat"')
os.system('cmd /k "pestgen hydrus_pest input.par measure.obf"')

# Edit .pst File to input and output files
# Open hydrus_pest.pst file for reading
with open('hydrus_pest.pst', 'r') as f:
    # Read the contents of the file into a list of lines
    lines = f.readlines()

# Modify model command line (17th from the top)
lines[21] = lines[21].replace('-1.000000E+10', '1.000000E-10')
lines[21] = lines[21].replace('1.000000E+10', '0.5')
lines[22] = lines[22].replace('-1.000000E+10', '1.000000E-10')
lines[23] = lines[23].replace('-1.000000E+10', '1.000000E-10')
lines[23] = lines[23].replace('1.000000E+10', '0.5')
lines[24] = lines[24].replace('-1.000000E+10', '1.000000E-10')

lines[25] = lines[25].replace('-1.000000E+10', '1.000000E-10')
lines[26] = lines[26].replace('-1.000000E+10', '1.000000E-10')
lines[27] = lines[27].replace('-1.000000E+10', '1.000000E-10')
lines[27] = lines[27].replace('1.000000E+10', '0.5')
lines[28] = lines[28].replace('-1.000000E+10', '1.000000E-10')
lines[29] = lines[29].replace('-1.000000E+10', '1.000000E-10')

# Modify model command line (5th from the bottom)
lines[-5] = lines[-5].replace('model', 'Run_hydrus.py')
lines[-3] = lines[-3].replace('model.tpl', 'input.tpl')
lines[-3] = lines[-3].replace('model.inp', 'input.dat')
lines[-2] = lines[-2].replace('model.ins', 'output.ins')
lines[-2] = lines[-2].replace('model.out', 'output.dat')

# Open the file for writing
with open('hydrus_pest.pst', 'w') as f:
    # Write the modified lines to the file
    f.writelines(lines)

os.system('cmd /k "pestchek hydrus_pest"')
os.system('cmd /k "pest hydrus_pest"')

# Storing data in excel sheet
Exp_BTC = np.loadtxt(os.path.join(current_dir,'exp_BTC.txt'))
Sim_BTC = np.loadtxt(os.path.join(current_dir,'Sim_BTC.txt'))
Exp_Zeroth = np.loadtxt(os.path.join(current_dir,'zeroth_Exp.txt'))
Sim_Zeroth = np.loadtxt(os.path.join(current_dir,'output.dat'))

# Calculating First and Second temporal moment
Sim_first = np.sum(Sim_BTC[:, 0]**2 * Sim_BTC[:, 1])/2
Sim_second = np.sum(Sim_BTC[:, 0]**3 * Sim_BTC[:, 1])/3
Sim_first_norm = np.sum(Sim_first)/np.sum(Sim_Zeroth)
Sim_second_norm = np.sum((Sim_second/Sim_Zeroth)-((Sim_first/Sim_Zeroth)**2))

# Calculate error
d = Exp_BTC[:, 1]-Sim_BTC[:, 1]
mse = np.mean(d**2)
mae = np.mean(abs(d))
rmse = np.sqrt(mse)
r2 = 1-(sum(d**2)/sum((Exp_BTC[:, 1]-np.mean(Exp_BTC[:, 1]))**2))

# Create a DataFrame from the NumPy arrays
df = pd.DataFrame({'Time':Exp_BTC[:, 0],'Exp_BTC': Exp_BTC[:, 1], 'Sim_BTC': Sim_BTC[:, 1], 'Exp_Zeroth': Exp_Zeroth, 'Sim_Zeroth': Sim_Zeroth,
                  'Exp_First':Exp_first_norm,'Sim_First':Sim_first_norm,'Exp_Second':Exp_second_norm,'Sim_Second':Sim_second_norm,
                  'MSE':mse,'MAE':mae,'RMSE':rmse,'R2':r2})

# Write the DataFrame to an Excel file
df.to_excel('output.xlsx', index=False)
    

# Execute Hydrus batch file
# os.system('cmd /k "run_hydrus "C:\Program Files\PC-Progress\HYDRUS 5.01 64-bit\Bin\H2D_Dual64.exe" return.txt"')
