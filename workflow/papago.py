#!/usr/bin/python
# encoding: utf-8

import sys
sys.path.append("lib")

import os
from workflow import Workflow3
import urllib
import json
import re


log = None

def is_able_to_translate(source_to_destination):
    supported = [{'source': 'ko', 'destination': 'en'},
                 {'source': 'ko', 'destination': 'ja'},
                 {'source': 'ko', 'destination': 'zh-CN'},
                 {'source': 'ko', 'destination': 'zh-TW'},
                 {'source': 'ko', 'destination': 'es'},
                 {'source': 'ko', 'destination': 'fr'},
                 {'source': 'ko', 'destination': 'ru'},
                 {'source': 'ko', 'destination': 'vi'},
                 {'source': 'ko', 'destination': 'th'},
                 {'source': 'ko', 'destination': 'id'},
                 {'source': 'ko', 'destination': 'de'},
                 {'source': 'ko', 'destination': 'it'},
                 {'source': 'zh-CN', 'destination': 'zh-TW'},
                 {'source': 'zh-CN', 'destination': 'ja'},
                 {'source': 'zh-TW', 'destination': 'ja'},
                 {'source': 'en', 'destination': 'ja'},
                 {'source': 'en', 'destination': 'zh-CN'},
                 {'source': 'en', 'destination': 'zh-TW'},
                 {'source': 'en', 'destination': 'fr'},
                 {'source': 'en', 'destination': 'ko'},
                 {'source': 'ja', 'destination': 'ko'},
                 {'source': 'zh-CN', 'destination': 'ko'},
                 {'source': 'zh-TW', 'destination': 'ko'},
                 {'source': 'es', 'destination': 'ko'},
                 {'source': 'fr', 'destination': 'ko'},
                 {'source': 'ru', 'destination': 'ko'},
                 {'source': 'vi', 'destination': 'ko'},
                 {'source': 'th', 'destination': 'ko'},
                 {'source': 'id', 'destination': 'ko'},
                 {'source': 'de', 'destination': 'ko'},
                 {'source': 'it', 'destination': 'ko'},
                 {'source': 'zh-TW', 'destination': 'zh-CN'},
                 {'source': 'ja', 'destination': 'zh-CN'},
                 {'source': 'ja', 'destination': 'zh-TW'},
                 {'source': 'ja', 'destination': 'en'},
                 {'source': 'zh-CN', 'destination': 'en'},
                 {'source': 'zh-TW', 'destination': 'en'},
                 {'source': 'fr', 'destination': 'en'}]

    return source_to_destination in supported


def get_response(url, data):
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", os.getenv("client_id"))
    request.add_header("X-Naver-Client-Secret", os.getenv("client_secret"))

    log.debug('data: %s' % data.encode('utf-8'))

    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    status = response.getcode()
    if status == 200:
        contents =  response.read()
        return json.loads(contents.decode('utf-8'))
    else:
        return None


def find_language_code(sentence):
    encoded = urllib.parse.quote(sentence)
    data = "query=" + encoded
    url = "https://openapi.naver.com/v1/papago/detectLangs"
    return get_response(url, data)


def get_translated_data(sentence, source, destination):
    encoded = urllib.parse.quote(sentence)
    data = "source=%s&target=%s&text=%s" % (source, destination, encoded)
    url = "https://openapi.naver.com/v1/papago/n2mt"
    return get_response(url, data)


def get_lang_argument(sentence):
    code = re.search('(ko|en|zh-cn|zh-tw|es|fr|ru)', str(sentence))
    if code:
        log.debug("code: %s" % code.group(1))
        return code.group(1)


def get_source_to_destination(lang_argument, sentence):
    lang_code = find_language_code(sentence)['langCode']
    if lang_code is None:
        return None

    if lang_argument and lang_code != lang_argument:
        return {'source': lang_code, 'destination': lang_argument}
    else:
        if lang_code == 'ko':
            return {'source': lang_code, 'destination': 'en'}
        else:
            return {'source': lang_code, 'destination': 'ko'}


def change_lang_code_for_chinese(source_to_destination):
    source = source_to_destination['source']
    if source.startswith("zh-"):
        source = source[:3] + source[3:].upper()

    destination = source_to_destination['destination']
    if destination.startswith("zh-"):
        destination = destination[:3] + destination[3:].upper()

    return {'source': source, 'destination': destination}


def main(wf):
    args = wf.args[0]

    end_mark = re.search('\s+$', args)
    if end_mark:
        encoded_args = args.encode('utf-8')
        log.debug(u"encoded_args: %s" % encoded_args)

        lang_argument = None
        sentence = encoded_args.strip()
        if encoded_args.startswith('-lang='.encode('utf-8')):
            lang_argument = get_lang_argument(encoded_args)

        log.debug(u"get_code: %s" % lang_argument)
        if lang_argument:
            tmp_idx = len('-lang=%s' % lang_argument)
            sentence = encoded_args[tmp_idx:].strip()

        log.debug(u"sentence: %s" % sentence)
        if sentence.strip():
            source_to_destination = get_source_to_destination(lang_argument, sentence)
            if source_to_destination is None:
                source_to_destination = {'source': 'unk', 'destination': 'ko'}
            else:
                source_to_destination = change_lang_code_for_chinese(source_to_destination)

            if is_able_to_translate(source_to_destination):
                log.debug(u"source_to_destination: %s" % source_to_destination)
            else:
                log.warn("Not supported for translation. source_to_destination: %s" % source_to_destination)
                wf.add_item(title=u'%s -> %s 번역은 지원하지 않습니다.' % (source_to_destination['source'], source_to_destination['destination']))
                wf.send_feedback()
                return

            response = get_translated_data(sentence, source_to_destination['source'], source_to_destination['destination'])

            if response:
                translated = response['message']['result']['translatedText']
                log.debug('translated: %s' % translated)
                length = 60
                splits = [translated[i: i + length] for i in range(0, len(translated), length)]
                for index in range(len(splits)):
                    log.debug('a: %s' % splits[index])
                    wf.add_item(title=u'%s' % splits[index], arg=translated, valid=True)\
                        .add_modifier(key='cmd', subtitle='Open Papago...')
                    if index >= 5:
                        break
            else:
                log.warn('There is no result after translation.')
                wf.add_item(title=u'번역할 수 없습니다. sentence: %s' % sentence, valid=False)

            wf.send_feedback()
        else:
            wf.add_item(title=u'아..뭐 번역하려고 했지?', valid=False)
            wf.send_feedback()
    else:
        log.debug("args: %s" % args)
        wf.add_item(title=u'문장 마지막에 반드시 공백을 1개 이상 입력해주세요.', valid=False)
        wf.send_feedback()


if __name__ == u"__main__":
    wf = Workflow3()
    log = wf.logger
    sys.exit(wf.run(main))
