import asyncio
import os.path
from pathlib import Path

import langid
import nonebot
from configs.config import NICKNAME, Config
from mockingbirdforuse import MockingBird
from mockingbirdforuse.log import logger as mocking_logger
from mockingbirdforuse.log import default_filter
# from nonebot import Driver, export, on_command
from nonebot import Driver, on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
from nonebot.log import logger as nonebot_logger
from nonebot.params import ArgStr, CommandArg
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me
from nonebot.typing import T_State
from utils.utils import is_number

from .data_source import get_voice
from .download import check_resource, download_resource
from .config import MOCKINGBIRD_PATH, Manager

__zx_plugin_name__ = "MockingBird"
__plugin_usage__ = """
usage：
    @Bot说 [你想要bot说的话]
    显示模型 显示所有模型
""".strip()
__plugin_des__ = "利用MockingBird生成语音并发送"
__plugin_cmd__ = [
    "说", f"{NICKNAME}说",
    "MockingBird",
    "mockingbird",
]
__plugin_type__ = ("来点语音吧~",)
__plugin_superuser_usage__ = """
usage： 
    显示模型
    修改模型 [序号]\[模型名称]
    开启/关闭tts 切换使用腾讯TTS(需要配置secret_key)
    重载模型 进行模型重载(并没有什么卵用，或许以后内存泄漏解决会有用？)
    调整/修改精度 修改语音合成精度(对TTS无效)
    调整/修改句长 修改语音合成最大句长(对TTS无效)
    更新模型 更新模型列表
""".strip()
__plugin_version__ = 1.0
__plugin_author__ = "AkashiCoin"
__plugin_block_limit__ = {"rst": f"{NICKNAME}说话没有那么快啦..."}

Config.add_plugin_config(
    "mockingbird",
    "USE_TTS",
    False,
    name="TTS语音是否启用",
    help_="是否使用TTS语音，需要配置tecent_secret_id和key，在 https://console.cloud.tencent.com/tts 启用",
    default_value=False,
)
Config.add_plugin_config(
    "mockingbird",
    "TENCENT_SECRET_ID",
    "",
    name="TTS的tencent_secret_id",
    help_="TTS的tencent_secret_id，在 https://console.cloud.tencent.com/cam/capi 设置",
    default_value="",
)
Config.add_plugin_config(
    "mockingbird",
    "TENCENT_SECRET_KEY",
    "",
    name="TTS的tencent_secret_key",
    help_="TTS的tencent_secret_key，在 https://console.cloud.tencent.com/cam/capi 设置",
    default_value="",
)

driver: Driver = nonebot.get_driver()
# export = export()

mockingbird_path = Path(MOCKINGBIRD_PATH)
mocking_logger = nonebot_logger  # 覆盖使用nonebot的logger
default_filter.level = driver.config.log_level

mockingbird = MockingBird()

@driver.on_startup
async def init_mockingbird():
    global part
    # global export
    model_name = Manager.get_config(config_name="model")
    model_path = mockingbird_path / model_name
    try:
        if not model_path.exists():
            mocking_logger.info("MockingBird 模型不存在...开始下载模型...")
            model_path.parent.mkdir(parents=True, exist_ok=True)
        if not await check_resource(mockingbird_path, model_name):
            if await download_resource(mockingbird_path, model_name, Manager.get_model_info(model_name)):
                mocking_logger.info("模型下载成功...")
            else:
                mocking_logger.error("模型下载失败，请检查网络...")
                return False
        mocking_logger.info("开始加载 MockingBird 模型...")
        mockingbird.load_model(
            Path(os.path.join(mockingbird_path, "encoder.pt")),
            Path(os.path.join(mockingbird_path, "g_hifigan.pt")),
            # Path(os.path.join(mockingbird_path, "wavernn.pt"))
        )
        mockingbird.set_synthesizer(Path(os.path.join(model_path, f"{model_name}.pt")))
        return True
    except Exception as e:
        return f"{type(e)}：{e}"


voice = on_command("说", aliases={"语音"}, block=True, rule=to_me(), priority=4)

view_model = on_command(
    "显示所有模型", aliases={"MockingBird模型", "显示模型", "所有模型"}, block=True, priority=5
)

change_model = on_command(
    "修改模型", aliases={"MockingBird模型修改"}, block=True, permission=SUPERUSER, priority=5
)

reload_mockingbird = on_command(
    "重载模型", aliases={"MockingBird模型重载"}, block=True, permission=SUPERUSER, priority=5
)

switch_tts = on_command(
    "开启tts", aliases={"关闭tts"}, block=True, permission=SUPERUSER, priority=5
)

adjust_accuracy = on_command(
    "调整语音精度", aliases={"调整精度", "修改精度"}, block=True, permission=SUPERUSER, priority=5
)

adjust_steps = on_command(
    "调整语音句长", aliases={"调整句长", "修改句长"}, block=True, permission=SUPERUSER, priority=5
)

update_model_list = on_command(
    "更新模型",
    aliases={"更新MockingBird", "模型更新"},
    block=True,
    permission=SUPERUSER,
    priority=5,
)


@voice.handle()
async def _(state: T_State, arg: Message = CommandArg()):
    args = arg.extract_plain_text().strip()
    if args:
        state["words"] = args


@voice.got("words", prompt=f"想要让{NICKNAME}说什么话呢?")
async def _(state: T_State, words: str = ArgStr("words")):
    words = words.strip().replace("\n", "").replace("\r", "")
    if Config.get_config("mockingbird", "USE_TTS"):
        record = await get_voice(words)
        if record:
            await voice.finish(MessageSegment.record(record))
        else:
            await voice.finish("出错了，请稍后再试")
    if langid.classify(words)[0] == "ja":
        record = await get_voice(words)
    # 加入tts英文
    elif langid.classify(words)[0] == "en":
        record = await get_voice(words)

    else:
        record = await asyncio.get_event_loop().run_in_executor(
            None,
            mockingbird.synthesize,
            str(words),
            mockingbird_path / Manager.get_config(config_name="model") / "record.wav",
            "HifiGan",
            0,
            Manager.get_config(config_name="voice_accuracy"),
            Manager.get_config(config_name="max_steps"),
        )
    await voice.finish(MessageSegment.record(record))


@view_model.handle()
async def _():
    msg = "当前加载的模型为:{}\n".format(Manager.get_config(config_name="model"))
    msg += "当前精度: {} , 最大句长: {}\n".format(
        Manager.get_config(config_name="voice_accuracy"),
        Manager.get_config(config_name="max_steps"),
    )
    msg += "可以修改的模型列表:"
    for i, model_name in enumerate(Manager._list):
        msg += "\n{}. {} --- {}".format(i, model_name, Manager.get_model_info(model_name)["nickname"])
    await view_model.finish(msg)


@change_model.handle()
async def _(arg: Message = CommandArg()):
    args = arg.extract_plain_text().strip()
    if args.isnumeric():
        args = Manager._list[int(args)]
        if args is None:
            await change_model.finish("该模型不存在...")
    if args not in list(Manager._list):
        await change_model.finish("该模型不存在...")
    else:
        if args == Manager.get_config(config_name="model"):
            await change_model.finish("该模型正在使用，请勿重复加载...")
        Manager.set_config(config_name="model", value=args)
        msg = await init_mockingbird()
        if isinstance(msg, str):
            await change_model.finish(f"修改失败...错误信息:{msg}")
        else:
            await change_model.finish(f"修改MockingBird模型为{args}成功...")


@reload_mockingbird.handle()
async def reload_model():
    msg = await init_mockingbird()
    if isinstance(msg, str):
        await reload_mockingbird.finish(f"重载失败...错误信息:{msg}")
    else:
        await reload_mockingbird.finish(f"重载MockingBird模型成功...")


@switch_tts.handle()
async def _(event: MessageEvent):
    global use_tts
    msg = event.get_plaintext().strip()
    if Config.get_config("mockingbird", "TENCENT_SECRET_KEY") == "":
        await switch_tts.finish("无法启用TTS，请先配置tencent_secret_key...")
    if msg.startswith("开启"):
        Config.set_config("mockingbird", "USE_TTS", True)
        Config.save(save_simple_data=True)
        await switch_tts.finish("已开启使用tts...")
    else:
        Config.set_config("mockingbird", "USE_TTS", False)
        Config.save(save_simple_data=True)
        await switch_tts.finish("已关闭tts，使用MockingBird语音...")


@adjust_accuracy.handle()
async def _(arg: Message = CommandArg()):
    args = arg.extract_plain_text().strip()
    if not is_number(args):
        await adjust_accuracy.finish("请输入数字...")
    num = int(args)
    if num > 2 and num < 10:
        Manager.set_config(config_name="voice_accuracy", value=num)
        msg = await init_mockingbird()
        if isinstance(msg, str):
            await adjust_accuracy.finish(f"调整失败...错误信息:{msg}")
        await adjust_accuracy.finish(f"已修改精度为: {num}")
    else:
        await adjust_accuracy.finish("请输入3-9以内的数字！")


@adjust_steps.handle()
async def _(arg: Message = CommandArg()):
    args = arg.extract_plain_text().strip()
    if not is_number(args):
        await adjust_steps.finish("请输入数字...")
    num = int(args)
    if num > 199 and num < 2001:
        Manager.set_config(config_name="max_steps", value=num)
        msg = await init_mockingbird()
        if isinstance(msg, str):
            await adjust_steps.finish(f"调整失败...错误信息:{msg}")
        await adjust_steps.finish(f"已修改最大句长为: {num}")
    else:
        await adjust_steps.finish("请输入200-2000以内的数字！")


@update_model_list.handle()
async def _():
    msg = Manager.update_model_list()
    if isinstance(msg, str):
        await update_model_list.finish(msg)
    else:
        await update_model_list.finish("模型列表更新成功!")
