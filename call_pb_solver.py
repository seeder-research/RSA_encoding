import subprocess
import time
import os

def call_solver(pb_file, timeout=300):
    start_time = time.time()  # Start timer
    
    try:
        # Start the process
        process = subprocess.Popen(['roundingsat', pb_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Wait for the process to finish or timeout
        stdout, stderr = process.communicate(timeout=timeout)
        
        solving_time = time.time() - start_time  # Calculate time if process finishes
        
        # Print the solver output for debugging purposes
        # print("Solver output (stdout):")
        # print(stdout)  # Print the standard output
        # print("Solver error (stderr):")
        # print(stderr)  # Print the standard error (if any)
        print(f"Solving time: {solving_time:.2f} seconds")

        return solving_time, False  # False indicates no timeout (no cutoff)
        
    except subprocess.TimeoutExpired:
        print(f"Process for {pb_file} killed due to timeout.")
        return timeout, True  # Return timeout and True for cutoff
    
    except subprocess.CalledProcessError as e:
        print(f"Process for {pb_file} failed with error: {e}")
        solving_time = time.time() - start_time
        return solving_time, False  # If there's an error, we still return time but no cutoff

# Ensure the directory exists for saving solving times
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# To store the solving times and cutoff information
folders = ['no_reduction_PB', 'convexhull_reduction_PB', 'union_rectangle_reduction_PB', 'all_reduction_PB']

for folder in folders:
    solving_times = []  # Clear solving times for each folder
    for i in range(100):
        PB_file = f"{folder}/pb_constraints_{i}.txt"
        print(f"Solving problem {i} from {folder}...")

        solving_time, cutoff = call_solver(PB_file)  # Call the solver and get solving time and cutoff status
        solving_times.append((i, solving_time, cutoff))  # Record problem number, time, and whether cutoff occurred

        if cutoff:
            print(f"Problem {i} exceeded the time limit of {solving_time:.2f} seconds (cutoff).")
        else:
            print(f"Problem {i} solved in {solving_time:.2f} seconds")
    
    # Ensure the directory for saving solving time exists
    save_dir = 'solving_time'
    ensure_directory_exists(save_dir)

    savefile = os.path.join(save_dir, f"{folder}_solving_time_300s.txt")
    
    # Save the results to a file
    with open(savefile, 'w') as f:
        for problem_number, solve_time, cutoff in solving_times:
            cutoff_str = "cutoff" if cutoff else "solved"
            f.write(f"Problem {problem_number}: {solve_time:.2f} seconds ({cutoff_str})\n")
