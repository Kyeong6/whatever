import importlib
import argparse
import time
import os
import psutil


# 시간 측정 시작
start = time.time()

# 현재 프로세스의 ID 가져오기
pid = os.getpid()
py = psutil.Process(pid)


preprocessing = importlib.import_module('Data_preprocessing')
training = importlib.import_module('Training')

def parse_arguments():
    parser = argparse.ArgumentParser(description='LSTM 데이터세트 학습 도구.')
    # subparsers = parser.add_subparsers()

    parser.add_argument('-f','--filename', help='전처리한 파일 이름을 입력합니다. 기본은 ./Output/Data_preprocessing/preprocessed.csv 파일입니다.', 
                        default='./Output/Data_preprocessing/preprocessed.csv') 
    parser.add_argument('-c', '--criteria', help='원본 데이터의 통계 파일 이름을 입력합니다.' ,default='./Output/Data_preprocessing/criteria.csv')
    # 시퀀스 설정
    parser.add_argument('-w', '--window_size', help='윈도우 사이즈를 정합니다. 기본은 7 입니다.',  type=int, default=7) 
    parser.add_argument('-p', '--periods', help='예측 윈도우 사이즈를 정합니다. 기본은 1 입니다.', type=int, default=1)
    
    # 하이퍼 파라미터 튜닝
    parser.add_argument('-hp', '--hyper_parameters',  action='store_true', help='하이퍼 파라미터를 튜닝합니다. -e(--epochs), -b(--batch_size) 를 통해 변경할 수 있습니다.')
    parser.add_argument('-e', '--epochs', help='epoch를 정합니다.', type=int, default=700 ) 
    parser.add_argument('-b', '--batch_size', help='batch size를 정합니다.', type=int, default=32)

    parser.add_argument('-l', '--learning', action='store_true', help='특정한 값으로 모델을 학습합니다. (-w 7, -p 1, -hp, -e 700, -b 32)') # 모델 학습에 대한 인자
 
    return parser.parse_args()

def main():
    args = parse_arguments()

    if args.learning: 
        training.training(7, 1)

    else:
        # 데이터 읽어오기
        df = training.read_data(args.filename)
    
        # 학습 데이터 / 테스트 데이터 분할
        train, val, test = training.train_test_split(df)

        # 학습 / 테스트 데이터 추가 확인
        print("Train and Test data split done.")
        print("Train data example:")
        print(train.head())
        print("Validation data example:")
        print(val.head())
        print("Test data example:")
        print(test.head())
        
        # 데이터 스케일링
        sc = training.data_scaling(train)

        # x_train, y_train, x_val, y_val, x_test 생성
        x_train, y_train = training.create_train(train, args.window_size, args.periods, sc)
        x_val, y_val = training.create_train(val, args.window_size, args.periods, sc)
        x_test = training.create_x_test(test, args.window_size, sc)

        # 모델 생성
        lstm_model, history = training.lstm_arch(x_train, y_train, x_val, y_val, args.periods, args.epochs, args.batch_size)

        # 학습 곡선 그리기
        training.plot_learning_curves(history)

        # 모델 성능 평가 
        plot = training.lstm_performance(lstm_model, sc, x_test, test, args.epochs, args.batch_size)

        # 스케일러, 모델, 그래프 저장
        # training.save_output(sc, lstm_model, plot)
        training.save_output(sc, lstm_model)
        
if __name__ == '__main__':
    main()

# 종료와 함께 수행시간 출력
print(f"{time.time()-start: .4f} sec")

# CPU 및 MEM 사용량 출력
cpu_usage = os.popen("ps aux | grep " + str(pid) + " | grep -v grep | awk '{print $3}'").read().strip()
memory_usage = round(py.memory_info()[0] / 2.**30, 2)

print("cpu usage\t\t:", cpu_usage, "%")
print("memory usage\t\t:", memory_usage, "GB")