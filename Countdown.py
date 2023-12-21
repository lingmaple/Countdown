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
                self.runTask(content.replace("run", "", 1), e_context)
            elif content.startswith("add"):
                self.addTask(content.replace("add", "", 1), e_context)
            elif content.startswith("rm"):
                self.rmTask(content.replace("rm", "", 1), e_context)
            elif content.startswith("ls"):
                self.lsTask(content.replace("ls", "", 1), e_context)
            else:
                # return help
                pass

    def runTask(self, content, e_context: EventContext):
        if content == "Countdown":
            target_date = datetime(2024, 1, 27).date()
            today = datetime.today().date()
            diff = target_date - today

            reply = Reply()
            reply.type = ReplyType.TEXT
            reply.content = f"今天距离寒假还有{diff.days}天😉"
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑

    def addTask(self, content, e_context: EventContext):
        # 时间信息
        timeStr = ""
        # 备注内容
        remarks = ""
        # 自定义消息内容
        custom_message = ""

        wordsArray = content.split(" ")

        timeStr = wordsArray[0]

        if len(wordsArray) == 2:
            remarks = wordsArray[1]

        elif len(wordsArray) == 3:
            custom_message = wordsArray[2]

        # taskInfo格式：
        # 0：唯一ID
        # 1：时间信息 - 格式为：HH:mm:ss
        # 2：备注内容
        # 3：自定义消息内容
        taskInfo = ("", timeStr, remarks, custom_message)
        taskModel = Model(taskInfo)

        # 保存task
        taskId = self.taskManager.addTask(taskModel)

        # 返回消息
        reply_text = f"Add success{taskId}"
        self.replay_use_default(reply_text, e_context)

    def rmTask(self, content, e_context: EventContext):
        # 任务编号
        taskId = content.split(" ")[0]

        isExist, taskModel = ExcelTool().write_columnValue_withTaskId_toExcel(taskId, 2, "0")

        taskContent = ""

        if taskModel:
            taskContent = f"{taskModel.circleTimeStr} {taskModel.timeStr} {taskModel.eventStr}"
            if taskModel.isCron_time():
                taskContent = f"{taskModel.circleTimeStr} {taskModel.eventStr}"

        # 回消息
        reply_text = ""
        tempStr = ""

        # 文案
        if isExist:
            tempStr = self.get_default_remind(TimeTaskRemindType.Cancel_Success)
            reply_text = "⏰定时任务，取消成功~\n" + "【任务编号】：" + taskId + "\n" + "【任务详情】：" + taskContent
        else:
            tempStr = self.get_default_remind(TimeTaskRemindType.Cancel_Failed)
            reply_text = "⏰定时任务，取消失败😭，未找到任务编号，请核查\n" + "【任务编号】：" + taskId

        # 拼接提示
        reply_text = reply_text + tempStr
        # 回复
        self.replay_use_default(reply_text, e_context)

    def lsTask(self, content, e_context: EventContext):
        pass

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
