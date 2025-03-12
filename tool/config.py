'''
Author: HuShuhan 873933169@qq.com
Date: 2025-03-10 16:42:40
LastEditors: HuShuhan 873933169@qq.com
LastEditTime: 2025-03-10 16:42:44
FilePath: \Translator\tool\translator\config.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import os
from dataclasses import dataclass
from typing import *

class LangUnit(NamedTuple):
    name: str = "Unknown"
    code: str = "Unknown"
    auto_detect: bool = False
    ch_cap: str = "-"

LANG_LIST: List[LangUnit]= [
    LangUnit(name="自动检测", code="auto"),
    LangUnit(name="中文", code="zh", auto_detect=True, ch_cap="Z"),
    LangUnit(name="繁体中文", code="zht", auto_detect=True, ch_cap="F"),
    LangUnit(name="英语", code="en", auto_detect=True, ch_cap="Y"),
    LangUnit(name="韩语", code="kor", auto_detect=True, ch_cap="H"),
    LangUnit(name="日语", code="jp", auto_detect=True, ch_cap="R")
]

baidu_app_id = os.environ["BAIDU_APP_ID"] # "20230315001600893"
baidu_app_key = os.environ["BAIDU_APP_ID"] # "lX8Eo5cdAfAPmBcaKxmy"
@dataclass
class BaiduConfig:
    APP_ID: str = baidu_app_id
    APP_KEY: str = baidu_app_key
    ENDPOINT: str = 'http://api.fanyi.baidu.com'
    API_PATH: str = '/api/trans/vip/translate'
    QPS: int = 10


tencent_secret_id = os.environ["TENCENT_SECRET_ID"]
tencent_secret_key = os.environ["TENCENT_SECRET_KEY"]
@dataclass
class TencentConfig:
    SECRET_ID: str = tencent_secret_id
    SECRET_KEY: str = tencent_secret_key
    ENDPOINT: str = "tmt.tencentcloudapi.com"
    REGION: str = "ap-guangzhou"
    QPS: int = 5


aliyun_access_key_id = os.environ["ALIYUN_ACCESS_KEY_ID"]
aliyun_access_key_secret = os.environ["ALIYUN_ACCESS_KEY_SECRET"]
@dataclass
class AliyunConfig:
    ACCESS_KEY_ID: str = aliyun_access_key_id
    ACCESS_KEY_SECRET: str = aliyun_access_key_secret
    ENDPOINT: str = "mt.aliyuncs.com"
    MODE: str = "general"
    QPS: int = 50


volc_access_key_id = os.environ["VOLC_ACCESS_KEY_ID"]
volc_access_key_secret = os.environ["VOLC_ACCESS_KEY_SECRET"]
@dataclass
class VolcConfig:
    ACCESS_KEY_ID: str = volc_access_key_id
    ACCESS_KEY_SECRET: str = volc_access_key_secret
    ENDPOINT: str = 'translate.volcengineapi.com'
    REGION: str = "cn-north-1"
    QPS: int = 10


xiaoniu_key = os.environ["XIAONIU_KEY"]
@dataclass
class XiaoNiuConfig:
    APP_KEY: str = xiaoniu_key
    URL: str = "http://api.niutrans.com/NiuTransServer/translation"
    QPS: int = 5
