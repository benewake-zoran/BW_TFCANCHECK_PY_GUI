from ctypes import *
import ctypes
import time
import math
import CAN


CMD_FRAME_HEADER = 0x5A  # 接收指令的帧头5A
DIS_DIFF = 20  # 允许测距误差范围
FPS_DIFF = 20  # 允许帧率误差范围
SingleRangeCmd = (0x5A, 0x04, 0x04, 0x62)  # 单次测距指令
candll = ctypes.windll.LoadLibrary('./ControlCAN.dll')


# 清空指定CAN通道的缓冲区
def clearBuffer_CAN(self):
    canclear = candll.VCI_ClearBuffer(CAN.nDeviceType, self.nDeviceInd, self.nCANInd)
    if canclear != 1:
        print('canclear failed!')
    else:
        print('canclear success!')
    time.sleep(0.5)


# 发送JSON文件里的指令
def sendCmd_CAN(self):
    str_cmd = self.data[self.index]['cmd']  # JSON 文件里 cmd 为字符串类型
    dec_cmd = [int(x, 16) for x in str_cmd.split()]  # 将字符串按空格分割成字符串列表，并将每个字符串转换为十六进制数值
    len_dec_cmd = len(dec_cmd)
    print('dec_cmd', dec_cmd, 'len_dec_cmd', len_dec_cmd)
    ubyte_8array = ctypes.c_ubyte * 8  # 定义一个8字节数据数组
    ubyte_3array = ctypes.c_ubyte * 3  # 定义一个3字节保留数组
    recv = ubyte_3array(0, 0, 0)
    # 定义CAN 帧结构
    ID = int(self.lineEdit_txID.text().replace(' ', ''), 16)
    TIMESTAMP = 0
    TIMEFLAG = 0
    SENDTYPE = 1
    REMOTEFLAG = int(self.data[self.index]['remoteflag'])  # json里是数据帧还是远程帧
    EXTERNFLAG = int(self.data[self.index]['externflag'])  # json里是标准帧还是扩展帧
    DATALEN = 8  # len(self.data[self.index]['cmd'].split())
    RESERVED = recv
    # 每次发送单帧，以提高发送效率
    Length = 1
    # 发送指令小于 8 时直接发送，大于 8 时切片发送
    if len_dec_cmd <= 8:
        txarray_cmd = ubyte_8array(*dec_cmd)  # 将指令存入数组中
        list_cmd_dec = list(txarray_cmd)  # 表示为列表显示，以便观察
        list_cmd_hex = list(hex(i)[2:].zfill(2).upper() for i in list_cmd_dec)  # 转换为十六进制显示
        print('list_cmd:', 'DEC', list_cmd_dec, 'HEX', list_cmd_hex)
        # 定义CAN 帧结构
        DATA = txarray_cmd
        # CAN 帧结构实例化
        tx_vci_can_obj = CAN.VCI_CAN_OBJ(ID, TIMESTAMP, TIMEFLAG, SENDTYPE, REMOTEFLAG, EXTERNFLAG, DATALEN, DATA, RESERVED)
        # 发送函数。返回值为实际发送成功的帧数
        canTransmit = candll.VCI_Transmit(CAN.nDeviceType, self.nDeviceInd, self.nCANInd, ctypes.byref(tx_vci_can_obj), Length)
        print('canTransmit', canTransmit)
        if canTransmit == -1:
            print('canTransmit failed!')
        else:
            print('canTransmit success!')
        # print('txID:', hex(tx_vci_can_obj.ID), ',txTimeStamp:', tx_vci_can_obj.TimeStamp, ',txTimeFlag:', tx_vci_can_obj.TimeFlag, ',txSendType:', tx_vci_can_obj.SendType)
        # print('txRemoteFlag:', tx_vci_can_obj.RemoteFlag, ',txExternFlag:', tx_vci_can_obj.ExternFlag, ',txDataLen:', tx_vci_can_obj.DataLen)
        print('txData:', list(tx_vci_can_obj.Data), ',txReserved:', list(tx_vci_can_obj.Reserved))
    else:
        dec_cmd_list = [dec_cmd[i:i + 8] for i in range(0, len(dec_cmd), 8)]
        print('dec_cmd_list:', dec_cmd_list)
        for i in range(len(dec_cmd_list)):
            print('dec_cmd_list[i]:', dec_cmd_list[i])
            txarray_cmd = ubyte_8array(*dec_cmd_list[i])
            DATA = txarray_cmd
            tx_vci_can_obj = CAN.VCI_CAN_OBJ(ID, TIMESTAMP, TIMEFLAG, SENDTYPE, REMOTEFLAG, EXTERNFLAG, DATALEN, DATA, RESERVED)
            canTransmit = candll.VCI_Transmit(CAN.nDeviceType, self.nDeviceInd, self.nCANInd, ctypes.byref(tx_vci_can_obj), Length)
            print('canTransmit', canTransmit)
            if canTransmit == -1:
                print('canTransmit failed!')
            else:
                print('canTransmit success!')
            # print('txID:', hex(tx_vci_can_obj.ID), ',txTimeStamp:', tx_vci_can_obj.TimeStamp, ',txTimeFlag:', tx_vci_can_obj.TimeFlag, ',txSendType:', tx_vci_can_obj.SendType)
            # print('txRemoteFlag:', tx_vci_can_obj.RemoteFlag, ',txExternFlag:', tx_vci_can_obj.ExternFlag, ',txDataLen:', tx_vci_can_obj.DataLen)
            print('txData:', list(tx_vci_can_obj.Data), ',txReserved:', list(tx_vci_can_obj.Reserved))
    print('------------------------------')
    time.sleep(0.1)


# 接收回显指令
def recvData_CAN(self):
    self.rx = ''
    # 接收的帧结构体VCI_CAN_OBJ数组
    rx_vci_can_obj = CAN.VCI_CAN_OBJ_ARRAY(2500)
    Len = 2500  # 接收的帧结构体数组的长度（本次接收的最大帧数，实际返回值小于等于这个值）
    WaitTime = 0  # 保留参数
    # 接收函数。此函数从指定的设备CAN通道的接收缓冲区中读取数据,返回实际读取的帧数
    canReceive = candll.VCI_Receive(CAN.nDeviceType, self.nDeviceInd, self.nCANInd, ctypes.byref(rx_vci_can_obj.ADDR), Len, WaitTime)
    print('canReceive', canReceive)
    if canReceive == -1:
        print('canReceive failed!')
    else:
        print('canReceive success!')
        print('obj size:', rx_vci_can_obj.SIZE)

    dataid_list = []  # 接收 id 列表
    datacmd_list = []  # 接收 cmd 列表
    # 遍历结构体数组中的每个元素,将其中的 Data 部分转化为 tuple 显示
    for i in range(rx_vci_can_obj.SIZE):
        data_id = rx_vci_can_obj.STRUCT_ARRAY[i].ID
        data_tuple = tuple(rx_vci_can_obj.STRUCT_ARRAY[i].Data)
        dataid_list.append(data_id)
        datacmd_list.append(data_tuple)
        if tuple(rx_vci_can_obj.STRUCT_ARRAY[i].Data)[0] == CMD_FRAME_HEADER:  # 判断帧头 5A
            print('head is 5A')
            if tuple(rx_vci_can_obj.STRUCT_ARRAY[i].Data)[2] == int(self.data[self.index]['cmd'].split()[2], 16) or self.data[self.index]['cmd'].split()[2] == '3F':  # 判断功能码
                print('cmd id code is same or sendcmd id code is 3F')
                rxid = hex(rx_vci_can_obj.STRUCT_ARRAY[i].ID)  # 取出 CAN 接收id
                self.label_rxID.setText(rxid)  # 显示在接收id标签上
                rx = tuple(rx_vci_can_obj.STRUCT_ARRAY[i].Data)
                rxlen = tuple(rx_vci_can_obj.STRUCT_ARRAY[i].Data)[1]  # 取出接收指令的长度
                print('rxlen:', rxlen)
                # 接收指令小于 8 时直接接收，大于 8 时累加接收
                if rxlen <= 8:  # 若指令长度小于8
                    rx_tuple = rx[:rxlen]
                    rxhex_str = ' '.join([format(i, '02X') for i in rx_tuple])
                    self.rx = rxhex_str  # self.rx 为接收指令（字符串类型）
                    print('rx_tuple:', rx_tuple)
                    print('hex_str:', rxhex_str)
                    print('self.rx:', self.rx)
                    break
                else:  # 若指令长度大于8
                    n = int(rxlen / 8)
                    print('n', n)
                    for j in range(n):
                        print('j', j)
                        rx += tuple(rx_vci_can_obj.STRUCT_ARRAY[i + 1].Data)
                        i = i + 1
                        print('rx:', rx)
                    if self.data[self.index]['cmd'] == '5A 05 56 00 B5':  # 若TF03系列发送检查序列号指令，接收指令需进行处理
                        print('send TF03 SN')
                        rx_list = []
                        for i in range(0, len(rx), 8):  # 每8个字节进行分割，取前6个字节
                            rx_list.append(rx[i:i + 6])
                        print('rx_list', rx_list)
                        rx_tuple = ()
                        for j in rx_list:  # 拼接指令
                            rx_tuple += j
                    else:
                        rx_tuple = rx[:rxlen]
                    rxhex_str = ' '.join([format(i, '02X') for i in rx_tuple])
                    self.rx = rxhex_str  # self.rx 为接收指令（字符串类型）
                    print('rx_tuple:', rx_tuple)
                    print('hex_str:', rxhex_str)
                    print('self.rx:', self.rx)
                    break
    # print('dataid_list:', dataid_list)
    # print('--------------------------------')
    # print('datacmd_list', datacmd_list)
    print('--------------------------------')


# 根据配置标签名称对rx进行处理和回显正误判断
def recvAnalysis_CAN(self):
    if self.data[self.index]['name'] == '序列号' or self.data[self.index]['name'] == 'SerialNumber':
        if self.rx != '' and self.rx.split()[2] == '12':  # TF02-i、TFmini-i 序列号检查
            SN_rxhex = self.rx.split()[3:17]  # # 取出序列号字节数组
            print('SN_rxhex', SN_rxhex)
            SN_rxstr = ''.join([chr(int(x, 16)) for x in SN_rxhex])
            self.widgetslist[self.index].setText(SN_rxstr)
            print('序列号是：', SN_rxstr)
            print('------------------------------')
        elif self.rx != '' and self.rx.split()[2] == '56':  # TF03 序列号检查
            SN_rxhex = self.rx.split()[4:18]
            SN_rxstr = ''.join([chr(int(x, 16)) for x in SN_rxhex])
            self.widgetslist[self.index].setText(SN_rxstr)
            print('序列号是：', SN_rxstr)
            print('------------------------------')
    elif self.data[self.index]['name'] == '固件版本' or self.data[self.index]['name'] == 'FirmwareVer':
        if self.rx != '' and self.rx.split()[2] == '01':
            version_rxhex = self.rx.split()[3:6][::-1]  # 取出固件版本字节数组并反转
            print('version_rxhex', version_rxhex)
            # 每两个字符由hex转为int，用'.'连接为str
            version_rxstr = '.'.join([str(int(i, 16)) for i in version_rxhex])
            print('version_rxstr', version_rxstr)
            self.widgetslist[self.index].setText(version_rxstr)
            print('固件版本是：', version_rxstr)
            print('------------------------------')
    elif self.data[self.index]['name'] == '输出帧率' or self.data[self.index]['name'] == 'FrameRate':
        if self.rx != '' and self.rx.split()[2] == '03':
            frame_rxhex = self.rx.split()[3:5][::-1]  # 取出输出频率字节数组并反转
            print('frame_rxhex', frame_rxhex)
            self.frame = int(''.join(frame_rxhex), 16)  # 将列表中的元素拼接成一个字符串,然后转十进制
            print('self.frame', self.frame)
            self.widgetslist[self.index].setText(str(self.frame) + ' (Hz)')
            print('输出帧率是：', self.frame)
            print('------------------------------')
    elif self.data[self.index]['widget'] == 'QLabel':
        self.widgetslist[self.index].setText(self.rx)
        print('--------------------------------')


# 判断期望值和检查值是否相同
def recvJudge_CAN(self):
    if self.data[self.index]['widget'] == 'QLabel' or self.data[self.index]['widget'] == 'QLineEdit':
        if self.data[self.index]['std'] == '' and self.widgetslist[self.index].text() != '':
            self.labelReturnlist[self.index].setText('OK')
            self.labelReturnlist[self.index].setStyleSheet('color: green')
        elif self.data[self.index]['name'] == '输出帧率' or self.data[self.index]['name'] == 'FrameRate':
            if self.data[self.index]['std'] != '':
                stdfps = int(self.data[self.index]['std'])
            else:
                stdfps = 0
            if self.rx != '':
                if abs(stdfps - self.frame) <= DIS_DIFF:
                    self.labelReturnlist[self.index].setText('OK')
                    self.labelReturnlist[self.index].setStyleSheet('color: green')
                    print('Framerate is Correct')
                else:
                    self.labelReturnlist[self.index].setText('NG')
                    self.labelReturnlist[self.index].setStyleSheet('color: red')
                    print('Framerate is Error')
            else:
                self.labelReturnlist[self.index].setText('NG')
                self.labelReturnlist[self.index].setStyleSheet('color: red')
                print('Framerate rx is Empty')
        elif self.data[self.index]['std'] == self.widgetslist[self.index].text() and self.widgetslist[self.index].text() != '':
            self.labelReturnlist[self.index].setText('OK')
            self.labelReturnlist[self.index].setStyleSheet('color: green')
        else:
            self.labelReturnlist[self.index].setText('NG')
            self.labelReturnlist[self.index].setStyleSheet('color: red')
    elif self.data[self.index]['widget'] == 'QComboBox':
        if self.data[self.index]['std'] == '' and self.widgetslist[self.index].currentText() != '':
            self.labelReturnlist[self.index].setText('OK')
            self.labelReturnlist[self.index].setStyleSheet('color: green')
        elif self.data[self.index]['std'] == self.widgetslist[self.index].currentText():
            self.labelReturnlist[self.index].setText('OK')
            self.labelReturnlist[self.index].setStyleSheet('color: green')
        else:
            self.labelReturnlist[self.index].setText('NG')
            self.labelReturnlist[self.index].setStyleSheet('color: red')


# 检查测距
def checkDis_CAN(self):
    # clearBuffer_CAN(self)
    rx_vci_can_obj = CAN.VCI_CAN_OBJ_ARRAY(2500)
    Len = 2500
    WaitTime = 0
    canReceive = candll.VCI_Receive(CAN.nDeviceType, self.nDeviceInd, self.nCANInd, ctypes.byref(rx_vci_can_obj.ADDR), Len, WaitTime)
    print('canReceive', canReceive)
    if canReceive == -1:
        print('canReceive failed!')
        self.rx = ''
        dist = None
        self.widgetslist[self.index].setText('')
    elif canReceive == 0:  # 接收帧数为0，尝试发送单次测距
        ubyte_8array = ctypes.c_ubyte * 8
        ubyte_3array = ctypes.c_ubyte * 3
        recv = ubyte_3array(0, 0, 0)
        # 定义CAN 帧结构
        ID = int(self.lineEdit_txID.text().replace(' ', ''), 16)
        TIMESTAMP = 0
        TIMEFLAG = 0
        SENDTYPE = 1
        REMOTEFLAG = int(self.data[self.index]['remoteflag'])  # json里是数据帧还是远程帧
        EXTERNFLAG = int(self.data[self.index]['externflag'])  # json里是标准帧还是扩展帧
        DATALEN = 8  # len(self.data[self.index]['cmd'].split())
        DATA = ubyte_8array(*SingleRangeCmd)
        RESERVED = recv
        # 每次发送单帧，以提高发送效率
        Length = 1
        tx_vci_can_obj = CAN.VCI_CAN_OBJ(ID, TIMESTAMP, TIMEFLAG, SENDTYPE, REMOTEFLAG, EXTERNFLAG, DATALEN, DATA, RESERVED)
        canTransmit = candll.VCI_Transmit(CAN.nDeviceType, self.nDeviceInd, self.nCANInd, ctypes.byref(tx_vci_can_obj), Length)
        print('canTransmit', canTransmit)
        time.sleep(1)
        canReceive = candll.VCI_Receive(CAN.nDeviceType, self.nDeviceInd, self.nCANInd, ctypes.byref(rx_vci_can_obj.ADDR), Len, WaitTime)
        print('canReceive', canReceive)
        if canReceive == -1:
            self.rx = ''
            print('canReceive failed!')
            dist = None
            self.widgetslist[self.index].setText('')
        elif canReceive == 0:
            print('canReceive is None!')
            self.rx = ''
            self.widgetslist[self.index].setText('')
            dist = None
        else:
            dist_tuple = tuple(rx_vci_can_obj.STRUCT_ARRAY[0].Data)
            self.rx = ' '.join([format(i, '02X') for i in dist_tuple])  # self.rx 为接收指令（字符串类型）
            dist_hex = dist_tuple[:2][::-1]
            dist_str = ''.join([format(i, '02X') for i in dist_hex])
            dist = int(dist_str, 16)
            print('dist_tuple:', dist_tuple, 'dist_hex:', dist_hex)
            print('dist_str:', dist_str, 'dist:', dist)
            self.widgetslist[self.index].setText(str(dist) + ' (cm)')
    else:  # 接收帧数不为0，获得测距
        print('canReceive success!')
        print('obj size:', rx_vci_can_obj.SIZE)
        dist_tuple = tuple(rx_vci_can_obj.STRUCT_ARRAY[0].Data)
        self.rx = ' '.join([format(i, '02X') for i in dist_tuple])
        dist_hex = dist_tuple[:2][::-1]
        dist_str = ''.join([format(i, '02X') for i in dist_hex])
        dist = int(dist_str, 16)
        print('dist_tuple:', dist_tuple, 'dist_hex:', dist_hex)
        print('dist_str:', dist_str, 'dist:', dist)
        self.widgetslist[self.index].setText(str(dist) + ' (cm)')

    # 判断测距结果是否正确
    if self.data[self.index]['std'] != '':
        stddis = int(self.data[self.index]['std'])
    else:
        stddis = 0
    if self.data[self.index]['std'] == '' and self.widgetslist[self.index].text() != '':
        self.labelReturnlist[self.index].setText('OK')
        self.labelReturnlist[self.index].setStyleSheet('color: green')
        print('Distance is Correct')
    elif dist is not None:
        if abs(stddis - dist) <= DIS_DIFF:
            self.labelReturnlist[self.index].setText('OK')
            self.labelReturnlist[self.index].setStyleSheet('color: green')
            print('Distance is Correct')
        else:
            self.labelReturnlist[self.index].setText('NG')
            self.labelReturnlist[self.index].setStyleSheet('color: red')
            print('Distance is Error')
    else:
        self.labelReturnlist[self.index].setText('NG')
        self.labelReturnlist[self.index].setStyleSheet('color: red')
        print('Distance is Error')
    print('std disVal:', stddis, 'actual disVal:', dist)
    print('--------------------------------')


# 检查其他标签
def checkOther_CAN(self):
    # clearBuffer_CAN(self)
    rx_vci_can_obj = CAN.VCI_CAN_OBJ_ARRAY(2500)
    Len = 2500
    WaitTime = 0
    canReceive = candll.VCI_Receive(CAN.nDeviceType, self.nDeviceInd, self.nCANInd, ctypes.byref(rx_vci_can_obj.ADDR), Len, WaitTime)
    print('canReceive', canReceive)
    if canReceive == -1:
        print('canReceive failed!')
        self.rx = ''
        self.widgetslist[self.index].setText('')
    elif canReceive == 0:  # 接收帧数为0，尝试发送单次测距
        ubyte_8array = ctypes.c_ubyte * 8
        ubyte_3array = ctypes.c_ubyte * 3
        recv = ubyte_3array(0, 0, 0)
        # 定义CAN 帧结构
        ID = int(self.lineEdit_txID.text().replace(' ', ''), 16)
        TIMESTAMP = 0
        TIMEFLAG = 0
        SENDTYPE = 1
        REMOTEFLAG = int(self.data[self.index]['remoteflag'])  # json里是数据帧还是远程帧
        EXTERNFLAG = int(self.data[self.index]['externflag'])  # json里是标准帧还是扩展帧
        DATALEN = 8  # len(self.data[self.index]['cmd'].split())
        DATA = ubyte_8array(*SingleRangeCmd)
        RESERVED = recv
        # 每次发送单帧，以提高发送效率
        Length = 1
        tx_vci_can_obj = CAN.VCI_CAN_OBJ(ID, TIMESTAMP, TIMEFLAG, SENDTYPE, REMOTEFLAG, EXTERNFLAG, DATALEN, DATA, RESERVED)
        canTransmit = candll.VCI_Transmit(CAN.nDeviceType, self.nDeviceInd, self.nCANInd, ctypes.byref(tx_vci_can_obj), Length)
        print('canTransmit', canTransmit)
        time.sleep(1)
        canReceive = candll.VCI_Receive(CAN.nDeviceType, self.nDeviceInd, self.nCANInd, ctypes.byref(rx_vci_can_obj.ADDR), Len, WaitTime)
        print('canReceive', canReceive)
        if canReceive == -1:
            print('canReceive failed!')
            self.rx = ''
            self.widgetslist[self.index].setText('')
        elif canReceive == 0:
            print('canReceive is None!')
            self.rx = ''
            self.widgetslist[self.index].setText('')
        else:
            cmd_tuple = tuple(rx_vci_can_obj.STRUCT_ARRAY[0].Data)
            self.rx = ' '.join([format(i, '02X') for i in cmd_tuple])
            dist_hex = cmd_tuple[:2][::-1]
            dist_str = ''.join([format(i, '02X') for i in dist_hex])
            dist = int(dist_str, 16)
            strength_hex = cmd_tuple[2:4][::-1]
            strength_str = ''.join([format(i, '02X') for i in strength_hex])
            strength = int(strength_str, 16)
            print('cmd_tuple:', cmd_tuple, 'dist_hex:', dist_hex, 'strength_hex:', strength_hex)
            print('dist_str:', dist_str, 'dist:', dist, 'strength_str:', strength_str, 'strength', strength)
            self.widgetslist[self.index].setText('D=' + str(dist) + ';S=' + str(strength))
    else:  # 接收帧数不为0，获得测距
        print('canReceive success!')
        print('obj size:', rx_vci_can_obj.SIZE)
        cmd_tuple = tuple(rx_vci_can_obj.STRUCT_ARRAY[0].Data)
        self.rx = ' '.join([format(i, '02X') for i in cmd_tuple])
        dist_hex = cmd_tuple[:2][::-1]
        dist_str = ''.join([format(i, '02X') for i in dist_hex])
        dist = int(dist_str, 16)
        strength_hex = cmd_tuple[2:4][::-1]
        strength_str = ''.join([format(i, '02X') for i in strength_hex])
        strength = int(strength_str, 16)
        print('cmd_tuple:', cmd_tuple, 'dist_hex:', dist_hex, 'strength_hex:', strength_hex)
        print('dist_str:', dist_str, 'dist:', dist, 'strength_str:', strength_str, 'strength', strength)
        self.widgetslist[self.index].setText('D=' + str(dist) + ';S=' + str(strength))

    # 判断结果是否正确
    if self.data[self.index]['std'] == '' and self.widgetslist[self.index].text() != '':
        self.labelReturnlist[self.index].setText('OK')
        self.labelReturnlist[self.index].setStyleSheet('color: green')
    elif self.data[self.index]['std'] == self.widgetslist[self.index].text() and self.widgetslist[self.index].text() != '':
        self.labelReturnlist[self.index].setText('OK')
        self.labelReturnlist[self.index].setStyleSheet('color: green')
    else:
        self.labelReturnlist[self.index].setText('NG')
        self.labelReturnlist[self.index].setStyleSheet('color: red')
    print('--------------------------------')


# 检查输出帧率
def checkFrame_CAN(self):
    timestamp_list = []
    Len = 2500
    WaitTime = 0
    rx_vci_can_obj = CAN.VCI_CAN_OBJ_ARRAY(2500)
    canReceive = candll.VCI_Receive(CAN.nDeviceType, self.nDeviceInd, self.nCANInd, ctypes.byref(rx_vci_can_obj.ADDR), Len, WaitTime)
    print('canReceive:', canReceive)
    if canReceive == -1:
        print('canReceive failed!')
        self.rx = ''
        self.widgetslist[self.index].setText('')
    elif canReceive == 0:
        self.frame = 0
        self.rx = ' '
        self.widgetslist[self.index].setText(str(round(self.frame)) + ' (Hz)')
    else:
        for i in range(rx_vci_can_obj.SIZE):
            timestamp = rx_vci_can_obj.STRUCT_ARRAY[i].TimeStamp  # 取出设备接收到某一帧的时间标识
            if timestamp != 0:
                timestamp_list.append(timestamp)
        timestamp_count = len(timestamp_list)  # 计算时间标识个数
        timestamp_diff = timestamp_list[-1] - timestamp_list[0]  # 计算时间标识差值
        recvrate = timestamp_diff / timestamp_count  # 计算接收速率
        self.frame = 100 * (100 / recvrate)  # 计算输出帧率
        self.widgetslist[self.index].setText(str(round(self.frame)) + ' (Hz)')
        rx = tuple(rx_vci_can_obj.STRUCT_ARRAY[0].Data)
        self.rx = ' '.join([format(i, '02X') for i in rx])
        print('rx:', rx, 'self.rx:', self.rx)
        print('timestamp_diff:', timestamp_diff, 'timestamp_count:', timestamp_count, 'recvrate:', recvrate, 'self.frame:', self.frame)
    recvJudge_CAN(self)
