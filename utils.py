#!/usr/bin/python
# -*- coding: UTF-8 -*-

from hashlib import md5
from base64 import urlsafe_b64encode
from datetime import datetime
from common.log import logger
import os
import json


class Model(object):
    # Item数据排序
    # 0：唯一ID
    # 1：时间信息 - 格式为：HH:mm:ss
    # 2：备注内容
    # 3：自定义消息内容
    def __init__(self, item):
        super().__init__()

        # ID - 获取当前时间生成唯一ID
        self.taskId = self.get_short_id(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # 时间信息
        timeValue = item[1]
        tempTimeStr = ""
        if isinstance(timeValue, datetime):
            # 变量是 datetime.time 类型（Excel修改后，openpyxl会自动转换为该类型，本次做修正）
            tempTimeStr = timeValue.strftime("%H:%M:%S")
        elif isinstance(timeValue, str):
            tempTimeStr = timeValue
        else:
            # 其他类型
            print("其他类型时间，暂不支持")
        self.timeStr = tempTimeStr

        # 消息内容
        self.custom_message = item[2]

        # 备注内容
        self.remarks = item[3]

    # 获取格式化后的Item
    def get_formatItem(self):
        item = (self.taskId, self.timeStr, self.custom_message, self.remarks)
        return item

    # 计算唯一ID
    def get_short_id(self, string):
        # 使用 MD5 哈希算法计算字符串的哈希值
        hash_value = md5(string.encode()).digest()

        # 将哈希值转换为一个 64 进制的短字符串
        short_id = urlsafe_b64encode(hash_value)[:8].decode()
        return short_id


class TaskManager(object):
    def __init__(self):
        super().__init__()
        logger.info("[TimeTaskTool] 1")

    # 读取Task
    def readTask(self):
        tempArray = ExcelTool().readExcel()
        self.convetDataToModelArray(tempArray)

    # 执行task
    def runTask(self, model: TimeTaskModel):
        # 非cron，置为已消费
        if not model.isCron_time():
            model.is_today_consumed = True
            # 置为消费
            ExcelTool().write_columnValue_withTaskId_toExcel(model.taskId, 14, "1")

        print(
            f"😄执行定时任务:【{model.taskId}】，任务详情：{model.circleTimeStr} {model.timeStr} {model.eventStr}
        ")
        # 回调定时任务执行
        self.timeTaskFunc(model)

        # 任务消费
        if not model.is_featureDay():
            obj = ExcelTool()
            obj.write_columnValue_withTaskId_toExcel(model.taskId, 2, "0")
            # 刷新数据
            self.refreshDataFromExcel()

    # 添加任务
    def addTask(self, taskModel: TimeTaskModel):
        taskList = ExcelTool().addItemToExcel(taskModel.get_formatItem())
        self.convetDataToModelArray(taskList)
        return taskModel.taskId

    # 删除任务
    def rmTask():
        pass


class JsonOP(object):
    __file_name = "CountdownTask.json"

    def __init__(self):
        super().__init__()
        file_path = self.getPath(self.__file_name)
        if not os.path.exists(file_path):
            self.createJson(self.__file_name)
            logger.info("任务文件不存在")

    def getPath(file_name: str = __file_name):
        dir_name = os.path.dirname(__file__)
        file_path = os.path.join(dir_name, file_name)
        return file_path

    def createJson(self, file_name: str = __file_name):
        with open(file_name, "w") as file:
            json.dump({}, file)

    def readJson(self, file_name: str = __file_name):
        dir_name = os.path.dirname(__file__)
        file_path = os.path.join(dir_name, file_name)
        if not os.path.exists(file_path):
            self.createJson(self.__file_name)
        with open(file_path, "r") as file:
            tasks = json.load(file)
        return tasks

    def saveJson(self, file_name: str = __file_name, tasks: dict = {}):
        dir_name = os.path.dirname(__file__)
        file_path = os.path.join(dir_name, file_name)
        with open(file_path, "w") as file:
            json.dump(tasks, file)
