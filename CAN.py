import os
import time
from ctypes import *
import ctypes

nDeviceType = 4  # USBCAN-2A或USBCAN-2C或CANalyst-II
# nDeviceInd = 0  # 第1个设备
# nCANInd = 0  # 第1个通道  可获取通道下拉列表值
ACCCODE = 0x80000000  # 过滤验收码
ACCMASK = 0xFFFFFFFF  # 过滤屏蔽码
RESERVED = 0  # 系统保留
FILTER = 1  # 滤波方式接收所有类型
MODE = 0  # 工作模式为正常模式
# 波特率与总线时序寄存器 Timing0 Timing1 设置对照字典
bauddict = {'250kbps': [0x01, 0x1C],
            '1000kbps': [0x00, 0x14],
            '20kbps': [0x18, 0x1C],
            '33.33kbps': [0x09, 0x6F],
            '40kbps': [0x87, 0xFF],
            '50kbps': [0x09, 0x1C],
            '66.66kbps': [0x04, 0x6F],
            '80kbps': [0x83, 0xFF],
            '100kbps': [0x04, 0x1C],
            '125kbps': [0x03, 0x1C],
            '160kbps': [0x01, 0x7F],
            '200kbps': [0x81, 0xFA],
            '400kbps': [0x80, 0xFA],
            '500kbps': [0x00, 0x1C],
            '666kbps': [0x80, 0xB6],
            '800kbps': [0x00, 0x16],
            }

candll = ctypes.windll.LoadLibrary('./ControlCAN.dll')


# 初始化 CAN 的配置
class VCI_INIT_CONFIG(Structure):
    _fields_ = [('AccCode', ctypes.c_uint),   # 验收码
                ('AccMask', ctypes.c_uint),   # 屏蔽码
                ('Reserved', ctypes.c_uint),  # 系统保留
                ('Filter', ctypes.c_ubyte),   # 滤波方式 =1为接收所有类型 =2为只接收标准帧 =3为只接受扩展帧
                ('Timing0', ctypes.c_ubyte),  # 波特率定时器 0（BTR0）
                ('Timing1', ctypes.c_ubyte),  # 波特率定时器 1（BTR1）
                ('Mode', ctypes.c_ubyte)      # 模式 =0表示正常模式（相当于正常节点），=1表示只听模式（只接收，不影响总线），=2表示自发自收模式（环回模式）
                ]


# CAN 帧结构
class VCI_CAN_OBJ(Structure):
    _fields_ = [('ID', ctypes.c_uint),            # 帧ID。32位变量，数据格式为靠右对齐
                ('TimeStamp', ctypes.c_uint),     # 设备接收到某一帧的时间标识
                ('TimeFlag', ctypes.c_ubyte),     # 是否使用时间标识，为1时TimeStamp有效，TimeFlag和TimeStamp只在此帧为接收帧时意义
                ('SendType', ctypes.c_ubyte),     # 发送帧类型  =0时为正常发送  =1时为单次发送
                ('RemoteFlag', ctypes.c_ubyte),   # 是否是远程帧  =0时为为数据帧  =1时为远程帧（数据段空）
                ('ExternFlag', ctypes.c_ubyte),   # 是否是扩展帧  =0时为标准帧（11位ID）  =1时为扩展帧（29位ID）
                ('DataLen', ctypes.c_ubyte),      # 数据长度 DLC (<=8)，即CAN帧Data有几个字节 约束了后面Data[8]中的有效字节
                ('Data', ctypes.c_ubyte * 8),     # CAN帧的数据
                ('Reserved', ctypes.c_ubyte * 3)  # 系统保留
                ]


# CAN 帧结构体数组
class VCI_CAN_OBJ_ARRAY(Structure):
    _fields_ = [('SIZE', ctypes.c_uint16),
                ('STRUCT_ARRAY', ctypes.POINTER(VCI_CAN_OBJ))
                ]

    def __init__(self, num_of_structs):
        self.STRUCT_ARRAY = ctypes.cast((VCI_CAN_OBJ * num_of_structs)(), ctypes.POINTER(VCI_CAN_OBJ))  # 结构体数值
        self.SIZE = num_of_structs  # 结构体长度
        self.ADDR = self.STRUCT_ARRAY[0]  # 结构体数值地址


# 结构体包含USB-CAN系列接口卡的设备信息
class VCI_BOARD_INFO(Structure):
    _fields_ = [('hw_Version', ctypes.c_ushort),
                ('fw_Version', ctypes.c_ushort),
                ('dr_Version', ctypes.c_ushort),
                ('in_Version', ctypes.c_ushort),
                ('irq_Num', ctypes.c_ushort),
                ('can_Num', ctypes.c_byte),
                ('str_Serial_Num', ctypes.c_char * 20),
                ('str_hw_Type', ctypes.c_char * 40),
                ('Reserved', ctypes.c_ushort)
                ]
