import os
import argparse
import pathlib
import time

def submit_jobs(test_run):
    shdir = 'Simulation2/ardfa_sh'
    pathlib.Path(shdir).mkdir(parents=True, exist_ok=True)
    logdir = 'Simulation2/ardfa_logs'
    pathlib.Path(logdir).mkdir(parents=True, exist_ok=True)
    savedir = 'Simulation2/arhdfa_fits'
    
    if test_run:       
        timetypes = ['AR']
        acfs = ['0.0']
        sigmafactors = ['constant']
        ps = [1]
        num_replicates = 1
        thetas = [0]
    else:
        timetypes = ['AR', 'MA','MA5_same', 'MA5_exp']
        acfs = ['0.0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8']
        sigmafactors = ['AR', 'constant']
        ps = [1,2,3,4]
        num_replicates = 100
        thetas = [0,1]

    
    for timetype in timetypes:
        for acf in acfs:
            for sigmafactor in sigmafactors:
                for theta in thetas:
                    for p in ps:
                        for replicate in range(num_replicates):
                            name = f'{timetype}_{acf}_{sigmafactor}_{theta}_{p}_{replicate}'
                            summary_file = pathlib.Path(savedir) / f'summary_{name}.pkl'
                            if summary_file.exists() and summary_file.stat().st_size > 0:
                                print(f'Skipping {name}, summary file already exists')
                                continue
                
                            cmd = f'module load miniconda/22.11.1-1\n' \
                                f'conda activate /work/pi_nick_umass_edu/dongahkim_umass_edu-conda/envs/forecastskill-env\n' \
                                f'python sim2_fit_one_replicate.py --timetype {timetype} --acf {acf} --sigmafactor {sigmafactor} --theta {theta} --p {p} --replicate {replicate} '
                            print(f"Launching {name}")
                            
                            sh_contents = f'#!/bin/bash\n' \
                                        f'#SBATCH --job-name="{name}"\n' \
                                        f'#SBATCH --ntasks=1 \n' \
                                        f'#SBATCH -c 1 # Number of Cores per Task\n' \
                                        f'#SBATCH --nodes=1 # Requested number of nodes\n' \
                                        f'#SBATCH --mem=4000 # Requested Memory\n' \
                                        f'#SBATCH --output="{logdir}/{name}.out" \n' \
                                        f'#SBATCH --error="{logdir}/{name}.err" \n' \
                                        f'#SBATCH --partition cpu # Partition\n' \
                                        f'#SBATCH --time 2:00:00 # Job time limit\n' + cmd
                            
                            shfile = pathlib.Path(shdir) / f'{name}.sh'
                            with open(shfile, 'w') as f:
                                f.write(sh_contents)
                            os.system(f'sbatch {shfile}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run estimation for simulation study, multiple combinations of sample size, theta, condition, and replicate index')
    
    parser.add_argument('--test_run',
                        action=argparse.BooleanOptionalAction,
			help='If specified, run only a small selection of setting for sample size, theta, condition, and replicate index for testing purposes.')
    parser.set_defaults(test_run=False)
    
    args = parser.parse_args()
    
    submit_jobs(**vars(args))

    