import pickle
import re
import csv
import itertools

scenes = ['near_soft', 'near_loud', 'far', 'whisper']
USER_NUM = 102
SENTENCE_NUM = 119

def emb_numbers(s):
    re_digits = re.compile(r'(\d+)')
    pieces = re_digits.split(s)
    pieces[1::2] = map(int, pieces[1::2])
    return pieces

#
# def sort_strings_with_emb_numbers(alist):
#     aux = [(emb_numbers(s), s) for s in alist]
#     aux.sort()
#     return [s for __, s in aux]
#
#
# def sort_strings_with_emb_numbers2(alist):
#     return sorted(alist, key=emb_numbers)


def convert():
    file_w = open('./output/asr_result.txt', 'w')
    with open('./output/asr_result', 'rb') as file:
        data = pickle.load(file)
        for key in sorted(data.keys(), key=emb_numbers):
            file_w.write(str(key) + ':' + str(data[key]) + '\n')
    file_w.close()

    file_e_w = open('./output/asr_result_error_lines.txt', 'w')
    with open('./output/asr_result_error_lines', 'rb') as file:
        data = pickle.load(file)
        for line in sorted(data, key=emb_numbers):
            file_e_w.write(str(line) + '\n')
    file_w.close()


def get_group(user):
    group = None
    if 1 <= user <= 25 or user == 101:
        group = 0
    if 26 <= user <= 50:
        group = 1
    if 51 <= user <= 75 or user == 102:
        group = 2
    if 76 <= user <= 100:
        group = 3
    return group


def get_scene_num(scene):
    num = None
    for i in range(len(scenes)):
        if scene == scenes[i]:
            num = i
            break
    return num+1


def check_num():
    file = open('./output/asr_result.txt', 'r')
    data = file.readlines()
    file.close()

    file_e_w = open('./output/num_error.txt', 'w')
    for user in range(1, USER_NUM+1):
        group = get_group(user)
        for scene in scenes:
            scene_num = get_scene_num(scene)
            csv_writer = csv.writer(open('./output/separated/user-{}-scene-{}.csv'.format(user, scene_num), 'w'))
            header = ['asr_result', 'correct_answer']
            csv_writer.writerow(header)
            asr_result = []
            pattern = re.compile("./user{}/{}/.+\n".format(user, scene))
            for line in data:
                if re.match(pattern, line):
                    asr_result.append(line.strip().split(":")[1])
            correct_answer = get_answer(group, scene_num)
            csv_writer.writerows(itertools.zip_longest(asr_result, correct_answer, fillvalue=""))
            if len(asr_result) != SENTENCE_NUM:
                file_e_w.write("{}\tuser-{}-scene-{}\n".format(len(asr_result)-SENTENCE_NUM, user, scene_num))
    file_e_w.close()


def get_answer(group, scene_num):
    assert 0 <= group <= 3
    assert 1 <= scene_num <= 4
    csv_data = csv.DictReader(open("./output/answer/{}.csv".format(group), 'r', encoding='gbk'))
    next(csv_data)
    answer = []
    for line in csv_data:
        answer.append(line["场景{}".format(scene_num)])
    return answer


if __name__ == '__main__':
    convert()
    check_num()
    # get_answer()
