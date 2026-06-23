#!/bin/python3

import sys


HELP_MESSAGE = """HELP"""

VARS = """
INTERFACE="enp2s0"
SCRIPT_DIR=$(dirname "$0")
QNUM=220
"""

NFT = """
nft delete table inet zapret

nft add table inet zapret

nft add chain inet zapret output { type filter hook output priority 0\\; }

nft add rule inet zapret output oifname \\"$INTERFACE\\" meta mark != 0x40000000 udp dport {%s} counter queue num $QNUM bypass
nft add rule inet zapret output oifname \\"$INTERFACE\\" meta mark != 0x40000000 tcp dport {%s} counter queue num $QNUM bypass

"""

EXEC = "$SCRIPT_DIR/nfqws --daemon --qnum=$QNUM --dpi-desync-fwmark=0x40000000"


def help():
    print(HELP_MESSAGE)
    exit()


def translate(input_path: str, output_path: str) -> None:
    input_file = open(input_path, "r")
    s = input_file.read()
    input_file.close()
    
    output_file = open(output_path, "w")

    s = s[s.index("start"):]
    
    wf_tcp_str = "--wf-tcp="
    wf_tcp_index = s.index(wf_tcp_str)
    tcp = s[wf_tcp_index + len(wf_tcp_str):s.index(" ", wf_tcp_index)]
    tcp = tcp.replace(",%GameFilterTCP%", "")

    wf_udp_str = "--wf-udp="
    wf_udp_index = s.index(wf_udp_str)
    udp = s[wf_udp_index + len(wf_udp_str):s.index(" ", wf_udp_index)]
    udp = udp.replace(",%GameFilterUDP%", "")

    s = s[s.index("--filter-"):]
    strats = []
    for strat in s.split("--new ^"):
        strat = strat.strip()
        if "GameFilter" in strat or "ipset-all.txt" in strat:
            continue

        strat = strat.replace("%BIN%", "$SCRIPT_DIR/bin/")
        strat = strat.replace("%LISTS%list-general-user.txt", "$SCRIPT_DIR/list-general-user.txt")
        strat = strat.replace("%LISTS%", "$SCRIPT_DIR/lists/")
        strats.append(strat)

    output_file.write("#!/bin/sh\n")
    output_file.write(VARS)
    output_file.write(NFT % (udp, tcp))
    output_file.write(EXEC)
    for index, strat in enumerate(strats):
        output_file.write(" \\\n")
        output_file.write("    " + strat)
        if index != len(strats) - 1:
            output_file.write(" --new")

    output_file.close()


def main(args):
    input_file_path = None
    output_file_path = None

    if len(args) < 5 or "-i" not in args or "-o" not in args:
        help()

    i_index = args.index("-i")
    o_index = args.index("-o")
    if 4 in (i_index, o_index):
        help()

    input_file_path = args[i_index + 1]
    output_file_path = args[o_index + 1]

    translate(input_file_path, output_file_path)


if __name__ == "__main__":
    main(sys.argv)
