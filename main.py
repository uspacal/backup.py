import argparse
from datetime import datetime, timedelta
import shutil
import os
import json
import uuid
import subprocess
import threading
import time
import secrets
import binascii
import time

# du --apparent-size -sm DEST
def r_dir_size(path: str):
    import subprocess 
    cmd = 'du'
    temp = subprocess.Popen([cmd, '--apparent-size', '-sm', path], stdout = subprocess.PIPE) 
    return temp.communicate()[0].decode().split('\t')[0] + ' MB'
    
def generate_random_hex_id(length):
    num_bytes = (length + 1) // 2
    random_bytes = secrets.token_bytes(num_bytes)
    hex_id = binascii.hexlify(random_bytes).decode('utf-8')[:length]
    return hex_id
    
def copy_tree(src: str, dst: str):
    import shutil
    shutil.copytree(src, dst, symlinks=False, ignore=None, ignore_dangling_symlinks=False, dirs_exist_ok=False)
    
def own_filename_time(directory: str, time_stamp: datetime, bu_id: str):
    directory = directory.replace('/', '_')[1:]
    return f'{directory}{time_stamp.strftime("%Y-%m-%d_%H-%M-%S")}_{bu_id}'

def create_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        return True
    else:
        return False
    
def background_function(backup_path, backup_size):
    def state():
        current_size = r_dir_size(backup_path)
        current_perc = int(int(current_size.split(' ')[0]) / int(backup_size.split(' ')[0]) * 100)
        print(f'{bcolors.OKGREEN}progress: {bcolors.ENDC} {current_size} / {backup_size} ({current_perc}%)', end='\r')
        time.sleep(1)
        
    time.sleep(1)
    global backup_done
    while not backup_done:
        state()
    else:
        state()
        print('')      

def main():
    ### argparser ###
    parser = argparse.ArgumentParser(
                        prog='simpleBackup',
                        description='kaeses simply tool to backup data to a mounted filesystem',
                        epilog='feel free to suggest changes')
    parser.add_argument('src_dir')
    parser.add_argument('dst_dir')
    parser.add_argument('-v', '--verbose',
                        action='store_true')
    parser.add_argument('-c', '--custom',
                        action='store_true')
    args = parser.parse_args()
    
    start_time = datetime.now()
    src_dir_size = r_dir_size(args.src_dir)
    
    prefix = f'{bcolors.HEADER}backup:{bcolors.ENDC}'
    # copy paste: print(f'{prefix}  {bcolors.OKCYAN}{}{bcolors.ENDC}')
    print(f'{prefix} source: {bcolors.OKCYAN}{args.src_dir}{bcolors.ENDC} -> destination: {bcolors.OKCYAN}{args.dst_dir}{bcolors.ENDC}')
    if args.verbose:
        print(f'{prefix} start: {bcolors.OKCYAN}{start_time.strftime("%Y-%m-%d %H:%M:%S")}{bcolors.ENDC}')
        print(f'{prefix} source: {bcolors.OKCYAN}{args.src_dir}{bcolors.ENDC} size: {bcolors.OKCYAN}{src_dir_size}{bcolors.ENDC}')
    
    if create_directory(args.dst_dir):
        if args.verbose:
            print(f'{prefix} {args.dst_dir}: {bcolors.OKGREEN}created{bcolors.ENDC}')
    else:
        if args.verbose:
            print(f'{prefix} {args.dst_dir}: {bcolors.OKGREEN}alredy exists{bcolors.ENDC}')
    
    random_hex_id = generate_random_hex_id(8)
    
    bu_folder_name = own_filename_time(args.src_dir, start_time, random_hex_id)
    full_backup_path = os.path.join(args.dst_dir, bu_folder_name)
    
    if args.verbose:
        print(f'{prefix} backup id: {bcolors.OKCYAN}{random_hex_id}{bcolors.ENDC}')
        print(f'{prefix} full backup path: {bcolors.OKCYAN}{full_backup_path}{bcolors.ENDC}')
        
    global backup_done
    backup_done = False
    
    background_thread = threading.Thread(target=background_function, args=(full_backup_path, src_dir_size))
    background_thread.start()
    
    if args.verbose:
        print(f'{prefix} copying files: {bcolors.OKGREEN}started{bcolors.ENDC}')
     
    copy_tree(args.src_dir, full_backup_path)
    
    backup_done = True
    background_thread.join()
    
    if args.verbose:
        print(f'{prefix} copying files: {bcolors.OKGREEN}completed{bcolors.ENDC}')
    
    if args.verbose:
        end_time = datetime.now()
        print(f'{prefix} end: {bcolors.OKCYAN}{end_time.strftime("%Y-%m-%d %H:%M:%S")}{bcolors.ENDC}')
        delta = end_time - start_time
        print(f'{prefix} time: {bcolors.OKCYAN}{delta}{bcolors.ENDC}')
    
### colors ###
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == "__main__":
    main()
