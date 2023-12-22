# encoding:utf-8

from hashlib import md5
from base64 import urlsafe_b64encode
from datetime import datetime
from common.log import logger
from random import randint
import os
import json


class Model(object):
    # Item数据排序
    # 0：任务ID
    # 1：时间信息 - 格式为：%Y-%m-%d    eg:2023-12-1
    # 2：备注内容
    # 3：自定义消息内容 - 使用“x”占位，如“距离考试还有x天”
    def __init__(self, item):
        super().__init__()

        # ID - 随机生成任务ID
        self.taskId = self.get_short_id()

        # 时间信息
        timeValue = item[1]
        try:
            # 判断时间格式是否正确
            datetime.strptime(timeValue, "%Y-%m-%d")
            self.dateStr = timeValue
            logger.info(timeValue)
        except:
            logger.info("时间格式错误")
            raise ValueError("时间格式错误")

        # 消息内容
        self.custom_message = item[2]

        # 备注内容
        self.remark = item[3]

    # 获取格式化后的Item
    def get_formatItem(self):
        item = (self.taskId, self.dateStr, self.custom_message, self.remark)
        return item

    # 计算任务ID
    def get_short_id(self):
        # 生成一个三位随机数作为ID
        short_id = randint(100, 999)
        
        # 检查ID是否重复
        tasks = JsonOP().readJson()
        if short_id in tasks:
            short_id = self.get_short_id()
        
        return short_id


class TaskManager(object):
    def __init__(self):
        super().__init__()
        logger.info("[TimeTaskTool] 1")

    # 读取Task
    def readTask(self):
        task_dict = JsonOP().readJson()
        return task_dict

    # 添加任务
    def addTask(self, taskModel: Model):
        task_dict = JsonOP().readJson()
        task_dict[taskModel.taskId] = (
            taskModel.taskId,
            taskModel.dateStr,
            taskModel.custom_message,
            taskModel.remark,
        )

        JsonOP().saveJson(task_dict)
        return taskModel.taskId

    # 删除任务
    def rmTask(self, taskId):
        task_dict = JsonOP().readJson()
        if taskId in task_dict:
            taskinfo = task_dict.pop(taskId)
            JsonOP().saveJson(task_dict)
            return taskinfo
        return None


class JsonOP(object):
    __file_name = "CountdownTask.json"
    __dir_name = os.path.dirname(__file__)
    __file_path = os.path.join(__dir_name, __file_name)

    def __init__(self):
        super().__init__()
        if not os.path.exists(self.__file_path):
            self.saveJson({})
            logger.info(f"创建任务文件{self.__file_path}")

    def readJson(self):
        dir_name = os.path.dirname(__file__)
        self.__file_path = os.path.join(dir_name, self.__file_path)
        # 尝试读json文件
        try:
            with open(self.__file_path, "r") as file:
                tasks = json.load(file)
                return tasks
        except:
            return self.resetJson()

    def saveJson(self, tasks: dict = {}):
        dir_name = os.path.abspath(__file__)
        self.__file_path = os.path.join(dir_name, self.__file_path)
        # 尝试写json文件
        try:
            with open(self.__file_path, "w") as file:
                json.dump(tasks, file, indent=4)
        except:
            self.resetJson()

    def resetJson(self):
        with open(self.__file_path, "r") as file:
            deleted_file = file.read()
            # 出错重置
            self.saveJson({})
            logger.info("任务文件因出错重置，原文件内容为")
            logger.info(deleted_file)
            return {}
