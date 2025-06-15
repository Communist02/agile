import asyncio
import os
import shutil
import subprocess
import json
from pathlib import Path


class MissingDestination(Exception):
    pass


class CheckRclone:
    def __init__(self, rclone):
        self.rclone = rclone

    def __call__(self, rclone):
        if rclone:
            return rclone
        if not rclone:
            pyrclonec = f'{Path.home()}/.pyrclonec'
            if Path(pyrclonec).exists():
                with open(pyrclonec) as f:
                    rclone = f.read().rstrip()
            else:
                print(
                    'Could not find rclone in your PATH. Enter it manually '
                    'and the program will remember it.')
                rclone = input('Path to rclone binary: ')
                if not Path(rclone).exists():
                    print('The rclone path you entered does not exist.')
                    raise FileNotFoundError
                else:
                    with open(pyrclonec, 'w') as f:
                        f.write(rclone)
            return rclone


class Rclone(CheckRclone):
    tasks: list = []
    rclone = shutil.which('rclone')
    debug = True

    def __init__(self, debug: bool = True):
        self.debug = debug

    async def _stream_process(self, process: subprocess.Popen[bytes]):
        index = len(self.tasks)
        self.tasks.append(
            {'current_size': 0, 'speed': 0, 'estimated': '-', 'full_size': 0, 'is_done': False})
        loop = asyncio.get_running_loop()

        while True:
            line = await loop.run_in_executor(None, process.stdout.readline)
            if not line:
                break
            s: str = line.decode()
            if 'ETA' in s:
                s = s.split('Transferred:')[1]
                s = s.strip()
                s = s.replace(',', '')
                # print(s)  # 66.996 MiB / 81.884 MiB 82% 5.003 MiB/s ETA 2s
                current_size = float(s.split(' ')[0])
                size_unit = s.split(' ')[1]
                full_size = float(s.split(' ')[3])
                size_unit_full_size = s.split(' ')[4]
                speed = float(s.split(' ')[6])
                size_unit_speed = s.split(' ')[7]
                estimated = s.split(' ')[9]

                match size_unit:
                    case 'KiB':
                        current_size *= 1024
                    case 'MiB':
                        current_size *= 1048576
                    case 'GiB':
                        current_size *= 1073741824
                    case 'TiB':
                        current_size *= 1099511627776

                match size_unit_full_size:
                    case 'KiB':
                        full_size *= 1024
                    case 'MiB':
                        full_size *= 1048576
                    case 'GiB':
                        full_size *= 1073741824
                    case 'TiB':
                        full_size *= 1099511627776

                match size_unit_speed:
                    case 'KiB/s':
                        speed *= 1024
                    case 'MiB/s':
                        speed *= 1048576
                    case 'GiB/s':
                        speed *= 1073741824
                    case 'TiB/s':
                        speed *= 1099511627776

                self.tasks[index]['current_size'] = current_size
                self.tasks[index]['full_size'] = full_size
                self.tasks[index]['speed'] = speed
                self.tasks[index]['estimated'] = estimated
                if full_size != 0 and current_size == full_size:
                    break
            elif 'error' in s:
                print(s)
        self.tasks[index]['is_done'] = True

    async def async_process(self, subcommand, arg1='', arg2='', arg3='', arg4='', *args):
        if subcommand in ['copy', 'copyto', 'move', 'sync', 'bisync', 'copyurl']:
            progress = True
            P = '-P'
        else:
            progress = False
            P = ''

        _args = ' '.join(args)
        command = f'{self.rclone} {subcommand} {arg1} {arg2} {arg3} {arg4} {P} {_args}'

        if self.debug:
            print(f'Executing: {command}')

        process = subprocess.Popen(command, shell=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if progress:
            await self._stream_process(process)

        loop = asyncio.get_running_loop()
        OUT, _ = await loop.run_in_executor(None, process.communicate)
        OUT = OUT.decode()

        if subcommand == 'size':
            total_objects = int(OUT.split('Total objects: ')[
                                1].split(' (')[1].split(')')[0])
            total_size = int(OUT.split('Total size: ')[1].split(
                ' (')[1].split(')')[0].split(' Byte')[0])
            return {'total_objects': total_objects, 'total_size': total_size}
        elif subcommand == 'lsjson' or subcommand == 'config' and arg1 == 'dump' or subcommand == 'about':
            try:
                return json.loads(OUT)
            except json.decoder.JSONDecodeError:
                return {}
        elif subcommand == 'lsf':
            return OUT.rstrip().split('\n')
        elif subcommand == 'config' and 'file' in command:
            return OUT.strip().split('\n')[-1]
        else:
            return OUT

    def sync_process(self, subcommand, arg1='', arg2='', arg3='', arg4='', communicate=True, *args):
        if subcommand in ['copy', 'copyto']:
            P = '-P'
        else:
            P = ''

        _args = ' '.join(args)
        command = f'{self.rclone} {subcommand} {arg1} {arg2} {arg3} {arg4} {P} {_args}'

        if self.debug:
            print(f'Executing: {command}')

        if not communicate and os.name == 'nt':
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        else:
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if communicate:
            OUT, _ = process.communicate()
            OUT = OUT.decode()

            if subcommand == 'size':
                total_objects = int(OUT.split('Total objects: ')[
                                    1].split(' (')[1].split(')')[0])
                total_size = int(OUT.split('Total size: ')[1].split(
                    ' (')[1].split(')')[0].split(' Byte')[0])
                return {'total_objects': total_objects, 'total_size': total_size}
            elif subcommand == 'lsjson' or subcommand == 'config' and arg1 == 'dump' or subcommand == 'about' or subcommand == 'config providers':
                return json.loads(OUT)
            elif subcommand == 'lsf':
                return OUT.rstrip().split('\n')
            elif subcommand == 'config' and 'file' in command:
                return OUT.strip().split('\n')[-1]
            else:
                return OUT
        else:
            return process

    async def mkdir(self, folder_path: str):
        return await self.async_process('mkdir', f'"{folder_path}"')

    def copy(self, source_path: str, destination_path: str):
        return self.sync_process('copy', f'"{source_path}"', f'"{destination_path}"', '--create-empty-src-dirs', communicate=False)

    async def lsjson(self, path: str, max_depth: int = -1):
        return await self.async_process('lsjson', f'"{path}"', f'--max-depth {max_depth}')

    def search(self, path: str, max_depth: int = -1):
        return self.sync_process('lsjson', f'"{path}"', f'--max-depth {max_depth}', communicate=False)

    def listremotes(self, long=False) -> str | dict[str]:
        if long:
            remotes = self.sync_process('listremotes', '--long')
            if remotes != '':
                remotes = remotes[:-1]
                remotes = remotes.split('\n')
                result = []
                for remote in remotes:
                    result.append({'name': remote.split(
                        ':')[0], 'type': remote.split(':')[-1].strip()})
                return result
            else:
                return []
        else:
            return self.sync_process('listremotes')

    def config(self, command: str, arg1: str = '', arg2: str = '', arg3: str = ''):
        return self.sync_process('config', command, arg1, arg2, arg3)

    def mount(self, remote: str, mount_point: str = '', arg: str = ''):
        return self.sync_process('mount', f'"{remote}"', f'"{mount_point}"', arg, communicate=False)
    
    def providers(self):
        return self.sync_process('config providers')
    
    def create_remote(self, remote_name, remote_type, args='', **kwargs):
        for key, value in kwargs.items():
            match value:
                case str():
                    args += f' {key}="{value}"'
                case int():
                    args += f' {key}={value}'
                case bool():
                    args += f' {key}={str(value).lower()}'
        return self.sync_process(f'config create "{remote_name}" {remote_type} {args}')

    def serve(self, serve_type: str, path: str, username: str = '', password: str = '', address: str = '', read_only: bool = False, args: str = ''):
        if read_only:
            args += ' --read-only'
        if username:
            args += f' --user {username}'
        if password:
            args += f' --pass {password}'
        if address:
            args += f' --addr {address}'
        return self.sync_process('serve', serve_type, f'"{path}"', args, communicate=False)

    async def execute(self, command):
        return await self.async_process(subcommand=command, _execute=True)

    async def deletefile(self, path: str):
        return await self.async_process('deletefile', f'"{path}"')

    async def purge(self, path: str):
        return await self.async_process('purge', f'"{path}"')

    async def moveto(self, source_path: str, destination_path: str):
        return await self.async_process('moveto', f'"{source_path}"', f'"{destination_path}"')

    async def about(self, remote_name: str):
        return await self.async_process('about', f'"{remote_name}"', '--json')

    async def is_dir(self, path: str):
        p = subprocess.Popen(f'{self.rclone} deletefile "{path}" --dry-run',
                             shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        loop = asyncio.get_running_loop()
        OUT, ERROR = await loop.run_in_executor(None, p.communicate)
        return 'ERROR :' in ERROR.decode()

    def __getattr__(self, attr):
        def wrapper(*args, **kwargs):
            return self.sync_process(attr, *args, **kwargs)
        return wrapper
