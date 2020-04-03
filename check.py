import pickle

with open('./output/asr_result_', 'rb') as file:
    data = pickle.load(file)
    print(len(data))
    print(data)