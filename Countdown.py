# encoding:utf-8

import plugins
from plugins.Countdown.utils import *
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from plugins import *
from datetime import datetime


@plugins.register(
    name="Countdown",
    desire_priority=100,
    hidden=True,
    desc="Countdown to winter vacation ",
    version="0.1",
    author="user",
)
class Countdown(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info("[Countdown] inited")
        self.taskManager = TaskManager()

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type not in [ContextType.TEXT]:
            return
        content = e_context["context"].content
        logger.debug("[Countdown] on_handle_context. content: %s" % content)

        # 指令前缀
        command_prefix = "cd"
        if content.startswith(command_prefix):
            # 处理任务
            print("[Countdown] 捕获到Conutdown任务:{}".format(content))

            content = content.replace(f"{command_prefix}", "", 1).strip()

            if content.startswith("run"):
                self.runTask(content, e_context)
            elif content.startswith("add"):
                self.addTask(content, e_context)
            elif content.startswith("rm"):
                self.rmTask(content, e_context)
            elif content.startswith("ls"):
                self.lsTask(content, e_context)
            else:
                # return help
                pass

    def runTask(self, content, e_context: EventContext):
        # 任务编号
        taskId = content.split(" ")[1]

        task_dict = self.taskManager.readTask()

        if taskId in task_dict:
            # taskInfo格式：
            # 0：任务ID
            # 1：时间信息 - 格式为：%Y-%m-%d    eg:2023-12-1
            # 2：备注内容
            # 3：自定义消息内容 - 使用“x”占位，如“距离考试还有x天”
            taskInfo = task_dict[taskId]
            logger.debug(f"执行任务{taskInfo[0]}")

            dateStr = taskInfo[1]
            date = datetime.strptime(dateStr, "%Y-%m-%d").date()
            message = taskInfo[3]

            # 计算天数
            today = datetime.today().date()
            diff = date - today
            day = diff.days

            if message != "":
                message = message.replace("x", "{}", 1)
                reply_text = message.format(day)
            elif day >= 0:
                # 倒数日
                reply_text = f"距离目标日{dateStr}还有{day}天"
            else:
                # 纪念日
                reply_text = f"目标日{dateStr}已经过去{-day}天了"
        else:
            reply_text = f"未知任务{taskInfo[0]}"

        # 回复
        self.replay_use_default(reply_text, e_context)

        """
        if content == "Countdown":
            target_date = datetime(2024, 1, 27).date()
            today = datetime.today().date()
            diff = target_date - today

            reply = Reply()
            reply.type = ReplyType.TEXT
            reply.content = f"距离xx还有{diff.days}天"
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
        """

    def addTask(self, content, e_context: EventContext):
        # 时间信息
        dateStr = ""
        # 备注内容
        remark = ""
        # 自定义消息内容
        custom_message = ""

        logger.info(content)
        wordsArray = content.split(" ")
        logger.info(wordsArray)

        if len(wordsArray) >= 2:
            dateStr = wordsArray[1]

        if len(wordsArray) >= 3:
            remark = wordsArray[2]

        if len(wordsArray) >= 4:
            custom_message = wordsArray[3]

        # taskInfo格式：
        # 0：任务ID
        # 1：时间信息 - 格式为：%Y-%m-%d    eg:2023-12-1
        # 2：备注内容
        # 3：自定义消息内容 - 使用“x”占位，如“距离考试还有x天”
        taskInfo = ("", dateStr, remark, custom_message)
        # try:
        # 构造taskInfo
        taskModel = Model(taskInfo)
        # 保存task
        taskId = self.taskManager.addTask(taskModel)
        # 返回消息
        reply_text = f"Add success{taskId}"
        # except:
        # 构造函数出错
        # logger.info(dateStr)
        # reply_text = "格式出错，请检查\n#help Countdown查看帮助信息"

        self.replay_use_default(reply_text, e_context)

    def rmTask(self, content, e_context: EventContext):
        # 任务编号
        taskId = content.split(" ")[1]

        taskInfo = self.taskManager.rmTask(taskId)
        if taskInfo:
            reply_text = f"删除任务成功\n{taskId}\n{taskInfo}"
        else:
            reply_text = f"删除任务失败，未知任务{taskId}\n"

        # 回复
        self.replay_use_default(reply_text, e_context)

    def lsTask(self, content, e_context: EventContext):
        task_dict = self.taskManager.readTask()
        reply_text = str(task_dict)
        self.replay_use_default(reply_text, e_context)

    # 使用默认的回复
    def replay_use_default(self, reply_message, e_context: EventContext):
        # 回复内容
        reply = Reply()
        reply.type = ReplyType.TEXT
        reply.content = reply_message
        e_context["reply"] = reply
        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑

    def get_help_text(self, **kwargs):
        help_text = "寒假倒计时\n关键字“Countdown”"
        return help_text
