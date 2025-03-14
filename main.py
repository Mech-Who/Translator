'''
Author: HuShuhan 873933169@qq.com
Date: 2025-03-10 14:37:08
LastEditors: HuShuhan 873933169@qq.com
LastEditTime: 2025-03-13 15:16:40
FilePath: \Translator\main.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# -*- coding: utf-8 -*-

from tool.translator.translator import AliTranslator
from tool.config import AliyunConfig


def main():
    print("Hello from translator!")
    text = input("please give me your text:")
    from_lang = input("please input your text lang code(chinese for 'zh', english for 'en'):")
    to_lang = input("please input your target lang code(chinese for 'zh', english for 'en'):")
    config = AliyunConfig()
    translator = AliTranslator(config.ACCESS_KEY_ID, config.ACCESS_KEY_SECRET, config.ENDPOINT, config.QPS)
    res = translator.translate(text, from_lang, to_lang)
    print(res)


if __name__ == "__main__":
    main()
