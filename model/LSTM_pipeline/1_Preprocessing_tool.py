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

def parse_arguments():
    parser = argparse.ArgumentParser(description='LSTM 데이터세트 전처리 도구.')
    # subparsers = parser.add_subparsers()
    parser.add_argument('-f','--filename', help='파일 이름을 입력합니다.') 
    
    parser.add_argument('-t', '--time', choices=['min', 'hourly', 'daily'], help='데이터의 시간 간격을 변경합니다. min, hour, day 중에서 선택할 수 있습니다.') 

    parser.add_argument('-n', '--normal_range', action='store_true', help='정상 범위를 정합니다. 기본은 UIF, LIF 이고, -m1(--min) 이나 -m2(--max)를 통해 정상 범위를 지정할 수 있습니다.')
    parser.add_argument('-m1', '--min', help='정상 범위의 최솟값을 지정합니다.', type=float) # default=None
    parser.add_argument('-m2', '--max', help='정상 범위의 최댓값을 지정합니다.', type=float)
    
    parser.add_argument('-l','--level', help='이상치 허용 기준을 정수로 입력합니다. 기본값은 10 입니다.', type=int, default=10)

    parser.add_argument('-w', '--week', choices=['all', 'weekday', 'weekend'], help='주말 또는 평일 데이터를 구합니다. 기본값은 전체(all)입니다.', default='all')

    parser.add_argument('-p', '--preprocess', action='store_true', help='특정한 값으로 데이터를 전처리합니다. (-t: min, -n, -l: 10, -w: all) ') # 전처리에 대한 인자
 
    return parser.parse_args()


def main():
    args = parse_arguments()

    if not args.preprocess: 
        # 데이터 읽어오기
        df = preprocessing.read_data(args.filename) 
        # # 결측치 보정
        df = preprocessing.Missing(df) 

        if args.time is not None: 
            # 1시간 간격 병합
            # time_interval = {'hourly': '1H', 'daily': '1D'}.get(args.time)
            
            # 10분 간격 병합
            time_interval = {'min': '10T','hourly': '1H', 'daily': '1D'}.get(args.time)
            df = preprocessing.TimeIntervalData(df,time_interval)

        if args.normal_range:
            # 이상치 보정
            df, table = preprocessing.Anomalous(df, args.level, args.max, args.min)

        # 평일 / 주말 데이터 구하기    
        if args.week in ['weekday', 'weekend']:
            df = preprocessing.week(df,args.week)

        # 전처리한 데이터 저장
        preprocessing.save_data(df, table)
    else:
        # 데이터 전처리 : 시간 병합(daily), 이상치 보정(level: 10%, 정상범위: UIF or LIF), 전체 데이터(week: all)
        preprocessing.Data_preprocessing(args.filename, args.level)

if __name__ == '__main__':
    main()

# 종료와 함께 수행시간 출력
print(f"{time.time()-start: .4f} sec")

# CPU 및 MEM 사용량 출력
cpu_usage = os.popen("ps aux | grep " + str(pid) + " | grep -v grep | awk '{print $3}'").read().strip()
memory_usage = round(py.memory_info()[0] / 2.**30, 2)

print("cpu usage\t\t:", cpu_usage, "%")
print("memory usage\t\t:", memory_usage, "GB")