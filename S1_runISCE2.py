#############################
# copyRight Author : CAS-aircas Yisen 
# time : 30/08/2025 Saturday
# written in : Beijing China 
# brief introduce : run the runfiles using run.py
# Sometimes the simplest solution is the most elegant one
#############################

import os
import sys
import glob
import argparse
import subprocess
from pathlib import Path
from multiprocessing import cpu_count


def find_run_files(run_files_dir):
    run_path = Path(run_files_dir)
    print(f"run_files path is {run_path}")
    if not run_path.exists():
        raise FileNotFoundError(f"Run files directory does not exist: {run_files_dir}")
    
    if not run_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {run_files_dir}")
    
    # Find all run_* files
    run_files = list(run_path.glob('run_*'))
    
    if not run_files:
        raise FileNotFoundError(f"No run_* files found in {run_files_dir}")
    
    return sorted([str(f) for f in run_files])


def run_stack_processing(run_files_dir, cores=None, expected_files=16):
    """
    Execute ISCE2 stack processing runfiles using run.py
    
    Args:
        run_files_dir (str): Directory containing run files
        cores (int): Number of CPU cores to use
        expected_files (int): Expected number of run files
        
    Returns:
        bool: True if all files processed successfully
    """
    
    # Auto-detect cores if not specified
    if cores is None:
        cores = min(max(cpu_count() // 2, 1), 8)
    
    print(f"Stack processing parameters:")
    print(f"  Run files directory: {run_files_dir}")
    print(f"  CPU cores: {cores}")
    print(f"  Expected run files: {expected_files}")
    
    # Find run files
    try:
        scripts = find_run_files(run_files_dir)
    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"ERROR: {e}")
        return False
    
    print(f"  Found run files: {len(scripts)}")
    
    if len(scripts) != expected_files:
        print(f"WARNING: Expected {expected_files} run files but found {len(scripts)}")
        response = input("Do you want to continue? (y/N): ").lower().strip()
        if response != 'y':
            print("Processing cancelled by user")
            return False
    
    # Create logs directory
    logs_dir = Path(run_files_dir) / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    success_count = 0
    total_files = len(scripts)
    
    # Process each run file
    for i in range(1, expected_files + 1):
        # Find matching script for current step
        matched_scripts = [s for s in scripts if f'run_{i:02d}' in os.path.basename(s)]
        
        if not matched_scripts:
            print(f"WARNING: run_{i:02d} script not found, skipping")
            continue
        
        script = matched_scripts[0]
        script_name = os.path.basename(script)
        log_file = logs_dir / f"log_run{i:02d}.log"
        
        print(f"\n{'='*60}")
        print(f"Step {i:02d}/{expected_files}: Processing {script_name}")
        print(f"{'='*60}")
        
        # Build command
        cmd = ["run.py", "--input", script, "-p", str(cores)]
        
        try:
            with open(log_file, "w") as f:
                result = subprocess.run(
                    cmd, 
                    stdout=f, 
                    stderr=subprocess.STDOUT, 
                    check=True,
                    cwd=run_files_dir
                )
            
            print(f"✓ {script_name} completed successfully")
            print(f"  Log saved to: {log_file}")
            success_count += 1
            
        except subprocess.CalledProcessError as e:
            print(f"✗ ERROR: {script_name} execution failed (return code: {e.returncode})")
            print(f"  Check log file for details: {log_file}")
            return False
        except FileNotFoundError:
            print(f"✗ ERROR: run.py not found. Please ensure ISCE2 is installed and in PATH.")
            return False
        except Exception as e:
            print(f"✗ ERROR: Unexpected error processing {script_name}: {str(e)}")
            return False
    
    print(f"\n{'='*60}")
    print(f"Processing Summary:")
    print(f"  Total files processed: {success_count}/{total_files}")
    print(f"  Success rate: {success_count/total_files*100:.1f}%")
    print(f"  Logs directory: {logs_dir}")
    print(f"{'='*60}")
    
    return success_count == len([s for s in scripts if any(f'run_{i:02d}' in os.path.basename(s) for i in range(1, expected_files + 1))])


def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description='Execute ISCE2 stack processing runfiles using run.py'
    )
    
    parser.add_argument('--run-files-dir', type=str, required=True,
                       help='Directory containing run_* scripts')
    parser.add_argument('--cores', type=int, default=None,
                       help='Number of CPU cores to use (default: auto-detect)')
    parser.add_argument('--expected-files', type=int, default=16,
                       help='Expected number of run files (default: 16)')
    
    return parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    
    # Run stack processing
    success = run_stack_processing(
        args.run_files_dir, 
        args.cores, 
        args.expected_files
    )
    
    sys.exit(0 if success else 1)