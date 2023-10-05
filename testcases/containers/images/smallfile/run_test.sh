#!/bin/bash

python3 smallfile_cli.py --top /testdir --min-dirs-per-sec=2 --threads 4 --file-size 1024 --files 1024 --fsync Y --operation create && \
python3 smallfile_cli.py --top /testdir --min-dirs-per-sec=2 --threads 4 --file-size 1024 --files 1024 --fsync Y --operation delete

