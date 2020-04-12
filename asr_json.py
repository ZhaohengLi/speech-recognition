# coding=utf-8

import sys
import json
import base64
import time
import pickle
import soundfile
import librosa

IS_PY3 = sys.version_info.major == 3

if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    timer = time.perf_counter
else:
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from urllib import urlencode
    if sys.platform == "win32":
        timer = time.clock
    else:
        # On most other platforms the best timer is time.time()
        timer = time.time

API_KEY = 'sjkIptvuwbWbmANnNoPuk8Fu'
SECRET_KEY = '2VKNjrvTFB75RO3AsR6pzEi4wVri7aif'

# 需要识别的文件
OUTPUT_FILE = './output/asr_result'
LOG_FILE_1 = './log/asr_log.txt'
LOG_FILE_2 = './log/asr_connect_log.txt'
PICKLE_FILE = 'output/data_16000_mono.pickle'
AUDIO_FILE = './audio/temp.wav'  # 只支持 pcm/wav/amr 格式，极速版额外支持m4a 格式
# 文件格式
FORMAT = AUDIO_FILE[-3:]  # 文件后缀只支持 pcm/wav/amr 格式，极速版额外支持m4a 格式
CUID = '123456PYTHON'
# 采样率
RATE = 16000  # 固定值

# 普通版

DEV_PID = 1537  # 1537 表示识别普通话，使用输入法模型。根据文档填写PID，选择语言及识别模型
ASR_URL = 'http://vop.baidu.com/server_api'
SCOPE = 'audio_voice_assistant_get'  # 有此scope表示有asr能力，没有请在网页里勾选，非常旧的应用可能没有

#测试自训练平台需要打开以下信息， 自训练平台模型上线后，您会看见 第二步：“”获取专属模型参数pid:8001，modelid:1234”，按照这个信息获取 dev_pid=8001，lm_id=1234
# DEV_PID = 8001 ;   
# LM_ID = 1234 ;

# 极速版 打开注释的话请填写自己申请的appkey appSecret ，并在网页中开通极速版（开通后可能会收费）

# DEV_PID = 80001
# ASR_URL = 'http://vop.baidu.com/pro_api'
# SCOPE = 'brain_enhanced_asr'  # 有此scope表示有极速版能力，没有请在网页里开通极速版

# 忽略scope检查，非常旧的应用可能没有
# SCOPE = False

class DemoError(Exception):
    pass


"""  TOKEN start """

TOKEN_URL = 'http://openapi.baidu.com/oauth/2.0/token'


def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode( 'utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req)
        result_str = f.read()
    except URLError as err:
        log(LOG_FILE_2, 'token http response http code : ' + str(err.code))
        result_str = err.read()
    if (IS_PY3):
        result_str =  result_str.decode()

    log(LOG_FILE_2, result_str)
    result = json.loads(result_str)
    log(LOG_FILE_2, result)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        log(LOG_FILE_2, SCOPE)
        if SCOPE and (not SCOPE in result['scope'].split(' ')):  # SCOPE = False 忽略检查
            raise DemoError('scope is not correct')
        log(LOG_FILE_2, 'SUCCESS WITH TOKEN: %s  EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
        return result['access_token']
    else:
        raise DemoError('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')


"""  TOKEN end """


def log(file, msg, init=False):
    mode = ''
    if init:
        mode = 'w'
    else:
        mode = 'a'
    with open(file, mode) as file:
        file.write(str(msg))
        file.write('\n')


def asr():
    token = fetch_token()

    speech_data = []
    with open(AUDIO_FILE, 'rb') as speech_file:
        speech_data = speech_file.read()

    length = len(speech_data)
    if length == 0:
        raise DemoError('file %s length read 0 bytes' % AUDIO_FILE)
    speech = base64.b64encode(speech_data)
    if (IS_PY3):
        speech = str(speech, 'utf-8')
    params = {'dev_pid': DEV_PID,
              # "lm_id" : LM_ID,    #测试自训练平台开启此项
              'format': FORMAT,
              'rate': RATE,
              'token': token,
              'cuid': CUID,
              'channel': 1,
              'speech': speech,
              'len': length
              }
    post_data = json.dumps(params, sort_keys=False)
    # print post_data
    req = Request(ASR_URL, post_data.encode('utf-8'))
    req.add_header('Content-Type', 'application/json')
    try:
        begin = timer()
        f = urlopen(req)
        result_str = f.read()
        log(LOG_FILE_2, "Request time cost %f" % (timer() - begin))
    except URLError as err:
        log(LOG_FILE_2, 'asr http response http code : ' + str(err.code))
        result_str = err.read()

    if (IS_PY3):
        result_str = str(result_str, 'utf-8')
    log(LOG_FILE_2, result_str)
    return result_str


def run():
    pickle_data = pickle.load(open(PICKLE_FILE, 'rb'))
    log(LOG_FILE_1, 'Pickle data length is {}'.format(len(pickle_data)))

    percentage = 0
    begin = timer()
    data_convert = []

    result = {}
    error_lines = []

    for data in pickle_data:
        try:
            soundfile.write(AUDIO_FILE, data[1], RATE, 'PCM_16', 'LITTLE', 'WAV')

            http_result = asr()
            if not http_result:
                log(LOG_FILE_1, 'When processing {}, got empty http result.'.format(data[0]))
                error_lines.append(data[0])
                continue

            json_result = json.loads(asr())
            if json_result['err_no'] == 0:
                result[data[0]] = json_result['result'][0]
            else:
                log(LOG_FILE_1, 'When processing {}, something went wrong. \n{}'.format(data[0], json_result))
                error_lines.append(data[0])

            time.sleep(1)
            if len(result) / len(pickle_data) - percentage > 0.02:
                percentage = len(result) / len(pickle_data)
                write_result("{}_{:.3}".format(OUTPUT_FILE, percentage), result)
                write_result("{}_error_lines_{:.3}".format(OUTPUT_FILE, percentage), error_lines)
                log(LOG_FILE_1, 'Now converted {} ({}%). Cost time {}'.format(len(result), percentage * 100, timer() - begin))

        except Exception as e:
            log(LOG_FILE_1, 'When processing {}, something UNEXPECTED went wrong.'.format(data[0]))
            error_lines.append(data[0])
            print(str(e))

    write_result(OUTPUT_FILE, result)
    write_result(OUTPUT_FILE + "_error_lines", error_lines)

    log(LOG_FILE_1, 'ASR succeed data length is {}. All finished.'.format(len(result)))
    log(LOG_FILE_1, 'ASR failed data length is {}. All finished.'.format(len(error_lines)))


def write_result(file_name, out):
    with open(file_name, 'wb') as file:
        pickle.dump(out, file)


if __name__ == '__main__':
    log(LOG_FILE_1, 'Time: ' + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())), True)
    log(LOG_FILE_2, 'Time: ' + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())), True)
    log(LOG_FILE_1, 'File(s): ' + str(PICKLE_FILE))
    log(LOG_FILE_1, 'Output_file: ' + OUTPUT_FILE)
    print("Program asr_json.py is now running.\nSee {} and {} for more information.".format(LOG_FILE_1, LOG_FILE_2))
    run()
    print("Program asr_json.py is now finished.")
