# -*- coding: utf-8 -*-

import json
import random
import urllib
from abc import ABC, abstractmethod
from hashlib import md5
from typing import List, Tuple

import requests
from alibabacloud_alimt20181012 import models as alimt_20181012_models

# Aliyun SDK
from alibabacloud_alimt20181012.client import Client as alimt20181012Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient

# Tencent SDK
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tmt.v20180321 import models, tmt_client

# Volc SDK
from volcengine.ApiInfo import ApiInfo
from volcengine.base.Service import Service
from volcengine.Credentials import Credentials
from volcengine.ServiceInfo import ServiceInfo

"""
Baidu Reference:
- Please refer to `https://api.fanyi.baidu.com/doc/21` for complete api document
- For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
- other reference: https://blog.csdn.net/qq_45776114/article/details/143796521
"""

"""
Tencent Reference:
- API Explorer: `https://console.cloud.tencent.com/api/explorer?Product=tmt&Version=2018-03-21&Action=TextTranslate`
- API Center: `https://cloud.tencent.com/document/api/551/15619`
"""


def make_md5(s, encoding="utf-8"):
    return md5(s.encode(encoding)).hexdigest()


class TranslatorUnavailableError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class Translator(ABC):
    @abstractmethod
    def translate(
        self, query: str, from_lang: str = "auto", to_lang: str = "zh"
    ) -> str:
        pass


class BaiduTranslator(Translator):
    def __init__(self, app_id: str, app_key: str, url: str, qps: int) -> None:
        self.app_id = app_id
        self.app_key = app_key
        self.url = url
        self.qps = qps

    def translate(
        self, query: str, from_lang: str = "auto", to_lang: str = "zh"
    ) -> str:
        """
        :param query: str 要翻译的文段
        :param from_lang: str query的语种，默认为'自动检测'
        :param to_lang: str 目标语种，默认为'zh'（中文）
        请求返回的结果结构如下：
        {
            "from": "zh",
            "to": "en",
            "trans_result": [
                {
                    "src": "我爱你，亲爱的中国！",
                    "dst": "I love you, dear China!"
                }
            ]
        }
        :return: str 返回的请求中的trans_result.dst字段内容
        """
        salt, sign = self.gen_salt_sign(query)

        # Build request
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "appid": self.app_id,
            "q": query,
            "from": from_lang,
            "to": to_lang,
            "salt": salt,
            "sign": sign,
        }

        # Send request
        try:
            response = requests.post(self.url, params=payload, headers=headers)
            response = response.json()
            return response["trans_result"][0]["dst"]
        except KeyError as err:
            raise Exception(f"Wrong key: {err}, from dict: {err}")
        except Exception as err:
            raise Exception(f"Request error: {err}")

    def gen_salt_sign(self, query: str) -> Tuple[str, str]:
        salt = random.randint(32768, 65536)
        return salt, make_md5(self.app_id + query + str(salt) + self.app_key)


class TencentTranslator(Translator):
    def __init__(
        self, secret_id: str, secret_key: str, endpoint: str, region: str, qps: int
    ):
        cred = credential.Credential(secret_id, secret_key)
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        httpProfile = HttpProfile()
        httpProfile.endpoint = endpoint
        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        self.client = tmt_client.TmtClient(cred, region, clientProfile)
        self.qps = qps

    def translate(
        self, query: str, from_lang: str = "auto", to_lang: str = "zh"
    ) -> str:
        try:
            request = models.TextTranslateRequest()
            params = {
                "SourceText": query,
                "Source": from_lang,
                "Target": to_lang,
                "ProjectId": 0,
            }
            request.from_json_string(json.dumps(params))
            response = self.client.TextTranslate(request)
            # TODO: 验证返回值
            return response
        except TencentCloudSDKException as err:
            print(err)
            raise Exception(str(err))

    def translate_batch(
        self, querys: List[str], from_lang: str = "auto", to_lang: str = "zh"
    ):
        try:
            # 实例化一个请求对象,每个接口都会对应一个request对象
            request = models.TextTranslateBatchRequest()
            params = {
                "Source": from_lang,
                "Target": to_lang,
                "ProjectId": 0,
                "SourceTextList": querys,
            }
            request.from_json_string(json.dumps(params))
            # 返回的resp是一个TextTranslateBatchResponse的实例，与请求对象对应
            response = self.client.TextTranslateBatch(request)
            # TODO: 验证返回值
            return response
        except TencentCloudSDKException as err:
            print(err)
            raise Exception(str(err))


class AliTranslator(Translator):
    def __init__(
        self, access_key_id: str, access_key_secret: str, endpoint: str, qps: int
    ):
        self.config = open_api_models.Config(
            access_key_id=access_key_id, access_key_secret=access_key_secret
        )
        self.config.endpoint = endpoint
        self.qps = qps
        self.client = alimt20181012Client(self.config)

    def translate(
        self, query: str, from_lang: str = "auto", to_lang: str = "zh"
    ) -> str:
        translate_general_request = alimt_20181012_models.TranslateGeneralRequest(
            format_type="text",
            source_language=from_lang,
            target_language=to_lang,
            source_text=query,
            scene="general",
            context="",
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            response = self.client.translate_general_with_options(
                translate_general_request, runtime
            )
            # TODO: 处理返回值
            return response
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)

    def translate_professional(
        self,
        query: str,
        from_lang: str = "auto",
        to_lang: str = "zh",
        scene: str = "social",
    ):
        translate_request = alimt_20181012_models.TranslateRequest(
            format_type="text",
            target_language=to_lang,
            source_language=from_lang,
            source_text=query,
            scene=scene,
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            response = self.client.translate_with_options(translate_request, runtime)
            # TODO: 处理返回值
            return response
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)

    async def translate_batch(
        self,
        querys: List[str],
        from_lang: str = "auto",
        to_lang: str = "en",
        scene: str = "social",
        api_type: str = "translate_standard",
    ):
        querys = {str(i): q for i, q in enumerate(querys)}
        querys = json.dumps(querys)
        get_batch_translate_request = alimt_20181012_models.GetBatchTranslateRequest(
            format_type="text",
            target_language=to_lang,
            source_language=from_lang,
            scene=scene,
            api_type=api_type,
            source_text=querys,
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            response = await self.client.get_batch_translate_with_options_async(
                get_batch_translate_request, runtime
            )
            # TODO: 处理返回值
            return response
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)


class VolcanoTranslator(Translator):
    def __init__(
        self,
        access_key_id: str,
        access_key_secret: str,
        endpoint: str,
        region: str,
        qps: int,
    ) -> str:
        service_info = ServiceInfo(
            endpoint,
            {"Content-Type": "application/json"},
            Credentials(access_key_id, access_key_secret, "translate", region),
            5,
            5,
        )
        k_query = {"Action": "TranslateText", "Version": "2020-06-01"}
        api_info = {"translate": ApiInfo("POST", "/", k_query, {}, {})}
        self.service = Service(service_info, api_info)
        self.qps = qps

    def translate(
        self, query: str, from_lang: str = "auto", to_lang: str = "zh"
    ) -> str:
        body = {"TargetLanguage": to_lang, "TextList": [query]}
        if from_lang != "auto":
            body = {"SourceLanguage": from_lang, **body}
        try:
            response = self.service.json("translate", {}, json.dumps(body))
            # TODO: 处理返回值
            return json.loads(response)
        except Exception as error:
            raise Exception(f"API call exception: {error}")


class XiaoNiuTranslator(Translator):
    def __init__(self, api_key: str, url: str, qps: int):
        self.api_key = api_key
        self.url = url
        self.qps = qps

    def translate(self, query: str, from_lang: str = "en", to_lang: str = "zh") -> str:
        data = {
            "from": from_lang,
            "to": to_lang,
            "apikey": self.api_key,
            "src_text": query,
        }
        data_en = urllib.parse.urlencode(data)
        request = self.url + "?&" + data_en
        response = urllib.request.urlopen(request).read()
        res_dict = json.loads(response)
        # TODO: 检查返回结果
        if "tgt_text" in res_dict:
            return res_dict["tgt_text"]
        else:
            return response

    def translate_batch(
        self, querys: List[str], from_lang: str = "en", to_lang: str = "zh"
    ) -> str:
        url = "http://api.niutrans.com/NiuTransServer/translationArray"
        data = {
            "from": "en",
            "to": "zh",
            "apikey": "您的apikey",
            "src_text": ["Allright", "Yes", "Good"],
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=data, headers=headers)
        # TODO: 检查返回值
        if response.status_code == 200:
            print("请求成功:", response.json())
            return response.json()
        else:
            print("请求失败:", response.status_code)
            return response
