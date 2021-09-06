#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os, sys

from solver import BoardStr

def main(input_file):
    """
    parser = argparse.ArgumentParser(description='gen_boardstr')
    parser.add_argument('input', nargs=None, default=None, type=str,
        help='Path to input problem file')
    parser.add_argument('-t', '--terminals', action='store', nargs='?', default='initial', type=str,
        help='Terminals order (initial, edgefirst, or random) (default: initial)')
    parser.add_argument('-s', '--seed', action='store', nargs='?', default=12345, type=int,
        help='Random seed')
    args = parser.parse_args()
    """

    # 問題ファイルの読み込み
    """
    with open(args.input, 'r') as f:
        lines = f.readlines()
    """
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # 問題ファイルを boardstr に変換
    # boardstr = BoardStr.conv_boardstr(lines, args.terminals, args.seed)
    boardstr = BoardStr.conv_boardstr(lines, 'initial', 12345)

    # 表示
    print(boardstr)
    return boardstr


if __name__ == '__main__':
    main()
