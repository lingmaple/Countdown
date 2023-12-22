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
    # 指令前缀
    command_prefix = "cd"

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

        # 处理任务
        if content.startswith(self.command_prefix):
            logger.info("[Countdown] 检测到Conutdown任务:{}".format(content))

            # 去除前缀
            content = content.replace(f"{self.command_prefix}", "", 1).strip()

            # 指令匹配
            if content.startswith("run"):
                self.runTask(content, e_context)
            elif content.startswith("add"):
                self.addTask(content, e_context)
            elif content.startswith("rm"):
                self.rmTask(content, e_context)
            elif content.startswith("ls"):
                self.lsTask(content, e_context)
            else:
                reply_text = "指令格式有误，请检查\n#help Countdown查看帮助信息"
                self.reply(reply_text, e_context)

    # 执行任务
    def runTask(self, content, e_context: EventContext):
        # 获取任务编号
        taskId = content.split(" ")[1]

        task_dict = self.taskManager.readTask()

        # 判断任务是否存在
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

            # 自定义回复
            if message != "":
                # 替换占位符
                message = message.replace("x", "{}", 1)
                reply_text = message.format(day)
            # 默认回复
            else:
                if day >= 0:
                    # 倒数日
                    reply_text = f"距离目标日{dateStr}还有{day}天"
                else:
                    # 纪念日
                    reply_text = f"目标日{dateStr}已经过去{-day}天了"
        # 未找到任务
        else:
            reply_text = f"执行任务失败，未知任务编号 {taskInfo[0]}"

        # 回复
        self.reply(reply_text, e_context)

    # 添加任务
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

        if len(wordsArray) == 4:
            custom_message = wordsArray[3]

        if len(wordsArray) > 4:
            reply_text = "指令格式有误，请检查\n#help Countdown查看帮助信息"
            self.reply(reply_text, e_context)
            return

        # taskInfo格式：
        # 0：任务ID
        # 1：时间信息 - 格式为：%Y-%m-%d    eg:2023-12-1
        # 2：备注内容
        # 3：自定义消息内容 - 使用“x”占位，如“距离考试还有x天”
        taskInfo = ("", dateStr, remark, custom_message)
        try:
            # 构造taskInfo
            taskModel = Model(taskInfo)
            # 保存task
            self.taskManager.addTask(taskModel)
            reply_text = f"添加任务成功\n" + self.outputTask({taskInfo})

        except:
            # 构造函数出错
            logger.info(dateStr)
            reply_text = "指令格式有误，请检查\n#help Countdown查看帮助信息"

        self.reply(reply_text, e_context)

    # 删除任务
    def rmTask(self, content, e_context: EventContext):
        # 任务编号
        taskId = content.split(" ")[1]

        taskInfo = self.taskManager.rmTask(taskId)
        if taskInfo:
            reply_text = f"删除任务成功\n" + self.outputTask({taskInfo})
        else:
            reply_text = f"删除任务失败，未知任务编号{taskId}\n"

        # 回复
        self.reply(reply_text, e_context)

    # 罗列所有任务
    def lsTask(self, content, e_context: EventContext):
        task_dict = self.taskManager.readTask()
        reply_text = "任务列表\n" + self.outputTask(task_dict)
        self.reply(reply_text, e_context)

    # 输出任务
    def outputTask(self, task_dict: dict):
        # 输出格式
        # 【000】2023-12-01
        # 备注 自定义消息
        content = "任务列表\n"
        for taskinfo in task_dict:
            tmp = f"【{taskinfo[0]}】{taskinfo[1]}\n" + f"{taskinfo[2]} {taskinfo[3]}\n"
            content = content + tmp
        str1 = "使用提示"
        str2 = f"添加任务：{self.command_prefix} add <时间> [备注] [消息]\n"
        str3 = f"删除任务：{self.command_prefix} rm <任务编号>\n"
        str4 = f"执行任务：{self.command_prefix} run <任务编号>\n"
        str5 = f"罗列任务：{self.command_prefix} ls\n"
        content = content + str1 + str2 + str3 + str4 + str5
        return content

    # 回复消息
    def reply(self, reply_message, e_context: EventContext):
        # 回复内容
        reply = Reply()
        reply.type = ReplyType.TEXT
        reply.content = reply_message
        e_context["reply"] = reply
        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑

    def get_help_text(self, **kwargs):
        str1 = f"添加任务：{self.command_prefix} add <时间> [备注] [消息]\n"
        str2 = f"\t<时间> 必选 目标日期 格式为“年-月-日” 如“2023-12-1”\n"
        str3 = f"\t[备注] 可选 该任务的备注 如“考试倒计时”\n"
        str4 = f"\t[消息] 可选 该任务的消息 如“距离考试x天” 使用“x”占位\n"
        str5 = f"\t例:{self.command_prefix} add 2023-12-1 考试倒计时 距离考试还有x天\n"
        text1 = str1 + str2 + str3 + str5

        str1 = f"删除任务：{self.command_prefix} rm <任务编号>\n"
        str2 = f"\t例:{self.command_prefix} rm 001\n"
        text2 = str1 + str2

        str1 = f"执行任务：{self.command_prefix} run <任务编号>\n"
        str2 = f"\t例:{self.command_prefix} run 001\n"
        text3 = str1 + str2

        str1 = f"罗列任务：{self.command_prefix} ls\n"
        str2 = f"\t例:{self.command_prefix} ls\n"
        text4 = str1 + str2

        help_text = "Countdown倒计时插件使用帮助\n" + text1 + text2 + text3 + text4
        return help_text
