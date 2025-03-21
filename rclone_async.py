import asyncio
import shutil
import subprocess
import json
from turtle import speed
import warnings
from pathlib import Path
from glob import glob
from tqdm.asyncio import tqdm
from loguru import logger


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
                logger.warning(
                    'Could not find rclone in your PATH. Enter it manually '
                    'and the program will remember it.')
                rclone = input('Path to rclone binary: ')
                if not Path(rclone).exists():
                    logger.error('The rclone path you entered does not exist.')
                    raise FileNotFoundError
                else:
                    with open(pyrclonec, 'w') as f:
                        f.write(rclone)
            return rclone


class Rclone_async(CheckRclone):
    def __init__(self, debug=False):
        self.rclone = shutil.which('rclone')
        self.tasks = []
        self.debug = debug

    async def _stream_process(self, p: subprocess.Popen[bytes]):
        self.tasks.append({'size': 0, 'speed': 0, 'estimated': 0, 'status': 'Executing'})
        index = len(self.tasks) - 1

        while True:
            line = p.stdout.readline()
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

                self.tasks[index]['size'] = current_size
                self.tasks[index]['full_size'] = full_size
                self.tasks[index]['speed'] = speed
                self.tasks[index]['estimated'] = estimated
                if full_size != 0 and current_size == full_size:
                    break
            elif 'error' in s:
                print(s)
            await asyncio.sleep(0.1)
        self.tasks[index]['status'] = 'Done'

    async def _process(self, subcommand, arg1='', arg2='', arg3='', arg4='', progress=False, _execute=False, *args):
        if subcommand in ['copy', 'move', 'sync', 'bisync', 'copyto', 'copyurl'] and not _execute:
            progress = True
            P = '-P'
        else:
            P = ''

        _args = ' '.join(args)
        _command = f'{self.rclone} {subcommand} {arg1} {arg2} {arg3} {arg4} {P} {_args}'

        if self.debug:
            print(f"Executing: {_command}")

        p = subprocess.Popen(
            _command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        if progress:
            await self._stream_process(p)

        OUT, _ = p.communicate()
        OUT = OUT.decode()

        if subcommand == 'size':
            total_objects = int(OUT.split('Total objects: ')[
                                1].split(' (')[1].split(')')[0])
            total_size = int(OUT.split('Total size: ')[1].split(
                ' (')[1].split(')')[0].split(' Byte')[0])
            return {'total_objects': total_objects, 'total_size': total_size}
        elif subcommand in ['lsjson', 'config'] and arg1 == 'dump':
            return json.loads(OUT)
        elif subcommand == 'lsf':
            return OUT.rstrip().split('\n')
        elif _execute:
            return OUT.rstrip().replace('\t', ' ')
        elif subcommand == 'config' and 'file' in _command:
            return OUT.strip().split('\n')[-1]
        else:
            return OUT

    async def execute(self, command):
        return await self._process(subcommand=command, arg1='', arg2='', arg3='', arg4='', progress=False, _execute=True)

    def delete(*args, **kwargs):
        raise NotImplementedError(
            'delete is a protected command! Use `execute()` instead.')

    def __getattr__(self, attr):
        async def wrapper(*args, **kwargs):
            return await self._process(attr, *args, **kwargs)
        return wrapper
