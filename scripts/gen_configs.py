#!/usr/bin/env python3

"""
生成Toybox配置文件
"""

import os
import re
from pathlib import Path

def gen_configs():
    config_file = "/home/user/toybox/.config"
    output_dir = "/home/user/toybox/generated"
    
    # 确保输出目录存在
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 生成config.h
    with open(os.path.join(output_dir, "config.h"), "w") as config_h:
        config_h.write("")
    
    with open(config_file, "r") as f:
        lines = f.readlines()
    
    with open(os.path.join(output_dir, "config.h"), "a") as config_h:
        for line in lines:
            line = line.strip()
            # 处理启用的配置项: CONFIG_*_=y
            match = re.match(r'^CONFIG_([A-Z0-9_]+)=y$', line)
            if match:
                symbol = match.group(1)
                config_h.write(f"#define CFG_{symbol} 1\n")
                config_h.write(f"#define USE_{symbol}(...) __VA_ARGS__\n")
                config_h.write(f"#define SKIP_{symbol}(...)\n")
                
                # 添加特殊别名
                if symbol == "TOYBOX_HELP":
                    config_h.write("#define CFG_HELP 1\n")
                continue
            
            # 处理禁用的配置项: # CONFIG_*_ is not set
            match = re.match(r'^#\s*CONFIG_([A-Z0-9_]+)\s+is\s+not\s+set$', line)
            if match:
                symbol = match.group(1)
                config_h.write(f"#define CFG_{symbol} 0\n")
                config_h.write(f"#define USE_{symbol}(...)\n")
                config_h.write(f"#define SKIP_{symbol}(...) __VA_ARGS__\n")
                
                # 添加特殊别名
                if symbol == "TOYBOX_HELP":
                    config_h.write("#define CFG_HELP 0\n")
                continue
            
            # 处理带值的配置项: CONFIG_*_=value
            match = re.match(r'^CONFIG_([A-Z0-9_]+)=(.*)$', line)
            if match:
                symbol = match.group(1)
                value = match.group(2).strip()
                if value == "n":
                    value = "0"
                elif value == "y":
                    value = "1"
                config_h.write(f"#define CFG_{symbol} {value}\n")
                config_h.write(f"#define USE_{symbol}(...) __VA_ARGS__\n")
                config_h.write(f"#define SKIP_{symbol}(...)\n")
                
                # 添加特殊别名
                if symbol == "TOYBOX_HELP":
                    config_h.write(f"#define CFG_HELP {value}\n")
    
    print("Generated config.h")

    # 生成newtoys.h和options.h
    with open(os.path.join(output_dir, "newtoys.h"), "w") as newtoys_h:
        newtoys_h.write("")
    
    with open(os.path.join(output_dir, "options.h"), "w") as options_h:
        options_h.write("// Command options strings and help texts\n")

    # Add toybox multiplexer command if CONFIG_TOYBOX is enabled
    with open(config_file, "r") as f:
        config_content = f.read()
    
    with open(os.path.join(output_dir, "newtoys.h"), "a") as newtoys_h, \
         open(os.path.join(output_dir, "options.h"), "a") as options_h:
        
        if "CONFIG_TOYBOX=y" in config_content:
            newtoys_h.write('USE_TOYBOX(NEWTOY(toybox, "l", TOYFLAG_USR|TOYFLAG_BIN))\n')
            options_h.write('#define OPTSTR_toybox "l"\n')
            options_h.write('#define HELP_toybox "Toybox multiplexer"\n')

        # 为启用的命令添加定义
        if "CONFIG_CAT=y" in config_content:
            newtoys_h.write('USE_CAT(NEWTOY(cat, "uvte", TOYFLAG_BIN))\n')
            options_h.write('#define OPTSTR_cat "uvte"\n')
            options_h.write('#define HELP_cat "usage: cat [-uvtAbeEnstTvxXy] [FILE...] Concatenate files to stdout"\n')

        if "CONFIG_LS=y" in config_content:
            newtoys_h.write('USE_LS(NEWTOY(ls, "(sort):(color):;(full-time)(show-control-chars)\377(block-size)#=1024<1\241(group-directories-first)\376ZgoACFHLNRSUXabcdfhilmnopqrstuwx", TOYFLAG_BIN))\n')
            options_h.write('#define OPTSTR_ls "(sort):(color):;(full-time)(show-control-chars)\377(block-size)#=1024<1\241(group-directories-first)\376ZgoACFHLNRSUXabcdfhilmnopqrstuwx"\n')
            options_h.write('#define HELP_ls "usage: ls [opts] [path...] List directory contents"\n')

    print("Generated newtoys.h")

    # 生成flags.h - 为所有命令的选项字符串中出现的字母生成标志
    with open(os.path.join(output_dir, "flags.h"), "w") as flags_h:
        flags_h.write("// generated/flags.h - 自动生成的标志定义\n")
        flags_h.write("\n")

        # 创建一个临时文件存储所有需要的FLAG
        temp_flags = set()

        # 为cat命令添加FLAG
        for char in "uvte":
            temp_flags.add(char)

        # 为ls命令添加FLAG (excluding 'l' which is handled separately for toybox)
        for char in "aqbgACFHLNRSUXdfhikmnpqrstuvwZoscx":
            temp_flags.add(char)

        # 添加特殊标志名称 for ls command
        temp_flags.add("full_time")
        temp_flags.add("show_control_chars")
        temp_flags.add("color")
        temp_flags.add("sort")
        temp_flags.add("block_size")
        temp_flags.add("group_directories_first")
        temp_flags.add("1")
        temp_flags.add("f")
        temp_flags.add("g")
        temp_flags.add("h")
        temp_flags.add("n")
        temp_flags.add("X21")
        temp_flags.add("X7E")

        # Add the toybox 'l' flag first
        flags_h.write("#define FLAG_l (1ULL<<0)\n")

        # Track used positions, starting with 0 already used
        used_positions = {0}
        counter = 1  # Start from 1 since 0 is taken by 'l'

        # Sort flags to ensure consistent order
        sorted_flags = sorted(temp_flags)
        
        for flag_name in sorted_flags:
            if flag_name and flag_name != "l":  # 'l' is already handled
                # Find next unused position
                while counter in used_positions:
                    counter = (counter + 1) % 64
                flags_h.write(f"#define FLAG_{flag_name} (1ULL<<{counter})\n")
                used_positions.add(counter)
                counter = (counter + 1) % 64

    print("Generated flags.h")

if __name__ == "__main__":
    gen_configs()
