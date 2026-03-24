import os

import psutil

def list_processes(search_name):
    my_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name']):
        if search_name.lower() in proc.info['name'].lower() and proc.info['pid'] != my_pid:
            print(f'pid: {proc.info['pid']}, name: {proc.info['name']}')

def find_processes_by_name(process_name):
    """
    Return a list of processes matching the given name.
    """
    found_processes = []
    # Iterate over all running processes
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Check if process name matches the given name (case-insensitive)
            if process_name.lower() in proc.info['name'].lower():
                found_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return found_processes