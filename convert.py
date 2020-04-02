import librosa
import pickle
import time

file_names = ['/Users/lizhaoheng/Downloads/data_original_0']
log_file = './log/convert_log.txt'
target_rate = 16000
to_mono = True
timer = time.perf_counter
output_file = './output/data_' + str(target_rate)
if to_mono:
    output_file = output_file + '_mono'


def convert():
    data_original = []
    for file_name in file_names:
        for line in pickle.load(open(file_name, 'rb')):
            data_original.append(line)
    log('Original data length is {}'.format(len(data_original)))

    percentage = 0
    begin = timer()
    data_convert = []

    for data in data_original[0:3]:
        name = data[0]
        array = librosa.resample(data[1], data[2], target_rate)
        if to_mono:
            array = librosa.to_mono(array)
        data_convert.append((name, array, target_rate))
        if len(data_convert)/len(data_original)-percentage > 0.5:
            log('Now converted {}. Cost time {}'.format(len(data_convert), timer()-begin))

    with open(output_file, 'wb') as file:
        pickle.dump(data_convert, file)

    log('Converted data length is {}. All finished.'.format(len(data_convert)))


def log(msg, init=False):
    mode = ''
    if init:
        mode = 'w'
    else:
        mode = 'a'
    with open(log_file, mode) as file:
        file.write(msg)
        file.write('\n')


def run():
    log('Time: ' + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())), True)
    log('File(s): ' + str(file_names))
    log('Target Rate: ' + str(target_rate))
    log('To Mono: ' + str(to_mono))
    log('Output file: ' + str(output_file))
    print("Program convert.py is now running.\nSee {} for more information.".format(log_file))
    convert()
    print("Program convert.py is now finished.")


if __name__ == '__main__':
    run()
