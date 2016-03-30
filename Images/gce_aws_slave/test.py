#!/usr/bin/env python
# -*- coding: UTF-8 -*-



#格式：\033[显示方式;前景色;背景色m
#显示方式：0（关闭所有效果），1（高亮），4（下划线），5（闪烁），7（反色），8（不可见）。
#前景色以3开头，背景色以4开头，具体颜色值有：0（黑色），1（红色），2（绿色），3（黄色），4（蓝色），5（紫色），6（青色），7（白色）。即前景绿色为32，背景蓝色为44。
import os
from datetime import datetime

COLOR_SCHEME = {"fore": {
    'black'    : 30,
    'red'      : 31,   #  红色
    'green'    : 32,   #  绿色
    'yellow'   : 33,   #  黄色
    'blue'     : 34,   #  蓝色
    'purple'   : 35,   #  紫红色
    'cyan'     : 36,   #  青蓝色
    'white'    : 37,   #  白色
    },
    'back':{
    'black'    : 40,
    'red'      : 41,   #  红色
    'green'    : 42,   #  绿色
    'yellow'   : 43,   #  黄色
    'blue'     : 44,   #  蓝色
    'purple'   : 45,   #  紫红色
    'cyan'     : 46,   #  青蓝色
    'white'    : 47,   #  白色
    },
    'mode': {'normal': 0,
    'bold'      : 1,   #  高亮显示
    'underline' : 4,   #  使用下划线
    'blink'     : 5,   #  闪烁
    'invert'    : 7,   #  反白显示
    'hide'      : 8,   #  不可见
    },
    'default' :
    {
        'end' : 0,
    },
}

info_style = "\033[%s;%sm" %(COLOR_SCHEME['mode']['bold'], COLOR_SCHEME['fore']['green'], )
debug_style = "\033[%s;%sm" %(COLOR_SCHEME['mode']['bold'], COLOR_SCHEME['fore']['blue'])
warning_style = "\033[%s;%sm" %( COLOR_SCHEME['mode']['bold'], COLOR_SCHEME['fore']['yellow'])
error_style = "\033[%s;%sm" %(COLOR_SCHEME['mode']['bold'], COLOR_SCHEME['fore']['red'])
default = "\033[0m"



LEVELS = {
    'DEBUG':    10,
    'INFO':   20,
    'WARNING': 30,
    'ERROR':   40,
}


LOG_LEVEL = 20


def info(message, log_level = LOG_LEVEL):
    prefix = "%s  INFO> " %(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    if log_level <= 20:
        msg = info_style + prefix + message + default
        print msg

def warning(message, log_level = LOG_LEVEL):
    prefix = "%s  WARNING> " % datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if log_level <= 30:
        msg = warning_style + prefix + message + default
        print msg


def error(message, log_level = LOG_LEVEL):
    prefix = "%s  WARNING> " % datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if log_level <= 40:
        msg = error_style + prefix + message + default
        print msg


def debug(message, log_level = LOG_LEVEL):
    prefix = "%s  WARNING> " % datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if log_level <= 10:
        msg = debug_style + prefix + message + default
        print msg



debug("asdfasdf", 10)
