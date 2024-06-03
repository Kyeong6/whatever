## **Python 경로 다루기 : os 및 os.path**

### Why?

로컬 환경에서 예제 csv 파일을 다룰 때는 본인이 위치해있는 폴더에 csv 파일을 놔두고 분석을 수행하기에 경로 설정 문제를 겪지 않는다. 

하지만, 분석 프로젝트를 협업으로 진행한다면? 팀원들마다 파일의 위치가 다르기 때문에 문제가 발생한다.

(팀원들의 OS차이, Desktop에 디렉토리를 위치시키지 않고 또 다른 디렉토리에 프로젝트 디렉토리를 넣은 경우 등..)

이런 상황을 해결하기 위해 모든 환경에서 돌아가도록 절대 경로, 상대 경로 등 경로를 정확히 지정해줘야하는데 이때 사용하는 것이 `os 및 os.path` 이다.

### os

- os.chdir(path) : 경로 변경
    - path, 즉 경로를 설정하면 해당 경로로 변경이 가능
- os.getcwd : 현재 경로 확인
    - 이용 방법
    
    ```python
    os.getcwd()
    path = os.getcwd() + '{file 경로}'
    os.chdir(path)
    os.getcwd()
    ```
    

### os.path

- os.path는 폴더명이나 파일명을 확인하고 존재유무를 파악할 수 있게 해주는 module

- os.path.abspath : 절대 경로 반환

```python
PATH = os.getcwd()
os.path.abspath(PATH)
```

- os.path.basename : PATH의 기본이름 반환
    - PATH = “/User/Users/Desktop/train.csv”일 경우 train.csv가 기본 이름에 해당
    
    ```python
    PATH.split('\\')[-1] == os.path.basename(PATH) # True 출력 , 즉 동일하다는 의미
    ```
    
- os.path.dirname : PATH의 directory 명 반환
    - PATH = “/User/Users/Desktop/os/train.csv”일 경우 디렉토리 명인 os 출력
    
    ```python
    os.path.dirname(PATH)
    ```
    
- os.path.split : dirname의 경우 입력 경로의 폴더 경로까지 반환, basename일 경우 파일이름만 출력한다. dirname과 basename을 동시에 확인하고자 할 때는 os.path.split을 사용하여 tuple 형태로 반환
    - DIRNAME과 BASENAME에 각각 폴더명과 파일명 담김

```python
os.path.dirname(PATH)

DIRNAME, BASENAME = os.path.split(PATH)
```

## Python 명령행 옵션 : argparse

### Argparse란?

Python script를 개발할 때, 호출 당시 인자값을 이용해 실행하고 싶을 경우 내장함수인 argparse 모듈을 사용하여 원하는 기능을 개발할 수 있다.

**기본**

```python
import argparse
parser = argparse.ArgumentParser(description=".", epilog=".")
```

argparse 모듈을 설치 후 parser 변수에 값인 argparse.ArgumentParser() 함수 인자로 해당 인자에 따른 문자열을 넣는다면 -h 옵션을 사용하여 문자열을 출력할 수 있다.

**상세 내용**

```python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("square", type=int, help="display a square of number")
parser.add_argument("-v", "--verbose", type=int, choices=[0,1,2],
										help="increase output verbosity")
arg = paser.parse_args()
answer = args.square
```

parser.add_argument() 함수를 통해 명령행 옵션의 다양성을 부여할 수 있다. 

- data type 설정
- choices를 통한 값 선택 가능(이후 조건문을 통해 값들을 통한 다른 로직 실행 가능)

최종적으로 args를 통해 접근하여 square와 같은 명령행을 통해 얻은 값 사용이 가능하다.

**추가적인 정보**

```python
parser.add_argument("-v", "--verbose", action="store_true", default=10)
```

`action="store_true"` 옵션은 값이 -v의 값(해당 옵션)이 입력되면 True를 출력하고 아니면 False를 출력하는 기능이다.

`default=값(int) or 'all'` 은 명령행 옵션을 실행하였을 때 기본값을 설정할 수 있다. 

## 결측치 채우기 : 선형 보간(Linear interpolation)

<aside>
💡 선형 보간법은 1차원 직선상에서 두 점의 값이 주어졌을 때 
그 사이의 값을 추정하기 위해 직선 거리에 따라 선형적으로 계산(비례식)하는 방법이다.

</aside>

### 필요한 상황

![week4_01](https://github.com/Kyeong6/whatever/assets/100195725/9bc95d9f-bd9d-456a-a0c2-5485ebf6992c)


위 그림처럼 직선 위에 점 a,b가 존재하고 이들 사이에 점 c가 존재한다. 

선형 보간법을 이용하면 점 c의 y좌표를 알 수 있다. 

### 적용 방법

![week4_02](https://github.com/Kyeong6/whatever/assets/100195725/16c62f7b-b7b0-49a3-be4a-fb55167fe0ae)


- 점 c는 `a와 b 사이 어딘가` 에 있는 점이라는 사실만 알 수 있다.
- 점 c의 `x 좌표를 임의로 지정`하면 선형 보간법을 사용하여 점 c의 y좌표까지 알아낼 수 있다.

![week4_03](https://github.com/Kyeong6/whatever/assets/100195725/eaa886b0-68dc-4248-ae29-95217dc2ade7)


- 해당 예시에서는 점 c의 x좌표를 4.9로 임의로 정함
- 점 a,b,c의 x좌표는 다음과 같다 → (2, 4.9, 7.4)

![week4_04](https://github.com/Kyeong6/whatever/assets/100195725/cb2e09d0-a643-4652-a8e3-d82593a34157)


- 이해를 돕기위해 일렬로 늘어뜨리면 다음과 같은 그림이다.
- d(전체 거리) = b - a (x좌표)
- d1 (a~c거리) = c - a (x좌표)
- d2 (c~b거리) = b - c (x좌표)

- 이때 `d1에 대한 d의 배율`을 구함
- d1 / d = 0.58이므로 백분율로 환산하면 58%를 의미
- 즉, 전체거리에서 58%만큼 움직이면 c가 나온다는 의미

![week4_05](https://github.com/Kyeong6/whatever/assets/100195725/737518fe-6add-42ac-a9fe-c7a4a0502778)


- 배율을 구하였다면 c의 y좌표를 구할 수 있다
- 전체거리(d) = b - a (y좌표)
- `d x 배율 + a의 y좌표`  = c의 y좌표

## 데이터의 정상성

<aside>
💡 시계열 데이터를 분석하는 목적<br/></br>
1. 시간에 따른 데이터의 패턴 파악하기 위함(계절성, 추세와 같은 변동성)<br/></br>
2. 분석된 패턴에 기반한 예측 모형을 통해 시계열 예측을 하기 위함

</aside>

즉, 시계열 분석은 과거의 값의 패턴을 분석해서 미래의 값을 추정하기위한 것이다. 

이때 가장 기본적인 것은 시계열 데이터가 `정상성` 을 유지해야 한다는 것이다.

### Why?

왜 정상성을 유지해야하나?

이론적으로 정상성을 띈다는 말은 시계열 데이터가 시점과 상관없이 일정한 평균과 분산을 가진다는 의미이다. 

어떤 시점에 데이터를 측정해도 일정한 변동폭(정규분포를 따르는 잡음)을 가진다는 의미이다.

결국엔 다른 시점간의 데이터끼리 i.i.d(independent and identically distributed)를 만족

반대로 비정상성 시계열 데이터는 시점에 따라 평균과 분산이 다르고, 변동폭이 불규칙하기 때문에 과거 관측 데이터의 분석으로는 미래의 데이터 예측하기가 어렵다. 

회귀 분석에서의 오차 정규성, 등분산성을 만족해야 회귀 분석 결과를 믿을 수 있는 것처럼, 시계열 분석에서는 정상성을 만족해야지 결과에 대한 신뢰성이 있다.

### Example

> 시계열의 평균과 분산이 일정, 특정한 트렌드(추세)가 존재하지 않는 성질 의미
> 

- 정상성

![week4_06](https://github.com/Kyeong6/whatever/assets/100195725/6f372a38-3ae2-4905-b06c-04c2af6484fa)


![week4_07](https://github.com/Kyeong6/whatever/assets/100195725/e183f31e-83b1-43fe-874f-f9da41b0aa94)


지그재그 모양을 수평으로 막 그린 형태

- 정상성 x

![week4_08](https://github.com/Kyeong6/whatever/assets/100195725/465f04b2-6ec8-4962-aeef-8f163d03c576)


![week4_09](https://github.com/Kyeong6/whatever/assets/100195725/0de6e9fb-b810-4052-b1fe-66d7c5fb997b)


a,c는 추세가 존재

## nvidia-smi 확인

<aside>
💡 nvidia에서 제공하는 GPU driver를 OS에 맞게 설치해야하는데, GPU driver 설치 후에 정보를 확인할 수 있도록 하는 명령어가 nvidia-smi

</aside>

![week4_10](https://github.com/Kyeong6/whatever/assets/100195725/995195af-2bbe-415d-ba45-c6eaa9a049e2)


1. Driver version : 현재 설치되어 사용하고 있는 nvidia GPU의 driver version
2. CUDA version : 현재 사용하고 있는 driver와 호환이 잘 되는 CUDA의 version, 추천의 의미이지 현재 설치되어 사용하고 있는 CUDA version x
3. GPU Fan : 현재 설치되어 있는 GPU 번호 및 fan이 장착되어 있는 GPU의 fan 성능 표현(%)
4. Name : GPU model명 
    
    4-2. Temp : 현재 GPU의 온도를 섭씨로 표현(70 ~ 80도 안정)
    
    4-3. Perf : Performance의 약자로 P0 ~ P12까지 존재하며 숫자가 작아질수록 good performance
    
    4-4. Persistence-M : Persistence-Mode로 on/off 존재, default mode는 off이며 on이 되면 power limit을 설정할 수 있다. 즉, power를 얼마나 지속할 지 설정이 가능하다. GPU 사용 시에 지연 시간을 아끼는 장점이 있지만, 전력을 더 낭비
    
    4-5. Pwr:Usage/Cap : GPU의 현재 전력의 사용량 및 최대 용량 표현
    
5. Bus-Id : Main board마다 가지고 있는 PCI slot에 부여된 Bus-Id, 이를 통해서 사용하는 GPU 번호와 main board의 PCI slot을 매칭 가능(중요 부분)
    
    5-2. Disp.A : Linux 설치 시에 Desktop version과 Server version이 존재, Desktop version의 경우 화면 출력을 GPU card로 하는 것이 좋고 기본적으로 off이지만 모니터를 연결한 출력 포트의 GPU의 경우 on이 되어 GPU card에 출력 되고 있음을 의미
    
    5-3. Memory-Usage : 현재 사용하고 있는 GPU의 memory와 GPU의 총 memory 표현(총 memory를 넘게 사용하면 `CUDA Out of memory` 발생)
    
6. GPU-Util : GPU의 현재 성능을 %로 표현, 즉 현재 해당 GPU의 사용량 표현
    
    6-2. Volatile Uncorr.ECC : on인 상태에서는 error count가 발생해서 0에서 점점 숫자가 증가, 이러한 경우 system hang이 발생해서 동작하지 않고, 응답하지 않는 상태가 되어 system 운영 불가능 그래서 보통 off로 설정하고 작업 진행
    
    6-3. Compute M. : Compute-Mode를 보여주고 있는 것으로 default는 0번. 1번은 exclusive thread mode, 2번은 prohibited mode, 3번은 exclusive process mode 의미 
    
    6-4. MIG M. : NVIDIA GPU를 slice하는 기능으로, MIG M은 MIG-Mode의 약자이고, MIG는 Multi-Instance GPU의 약자이다. CUDA application을 실행 시 최대 7개의 개별 GPU instance로 안전하게 분할하여 여러 사용자에게 별도으이 GPU를 제공하여 작업을 가속화하는데 도움을 줌, 여러 개의 instance를 지원하는 MIG는 NVIDIA A100 모델에서만 지원이 되고 이외에도 필요조건 존재 
    

![week4_11](https://github.com/Kyeong6/whatever/assets/100195725/76f256d2-b029-4199-ba47-62f16bb8fc22)


- GPU 0 ~ 7번 까지의 Process ID 등 현재 사용 중인 정보 보여줌
- GPU의 번호에 따라 PID를 확인하여 GPU가 실행 중인 process 확인이 가능

**nvidia-smi Live Memory Check**

GPU를 사용하여 작업하다보면 `out of memery` 가 뜨는 문제가 발생한다. 이를 방지하기 위해 실시간으로 GPU의 현재 memory 상황을 보고 싶을 때 `watch` 명령어를 이용한다.

```bash
watch -d -n 1 nvidia-smi
```

- -n 뒤의 숫자는 시간 간격을 의미, 즉 1은 1초마다 갱신
- -d 는 update 되는 부분 하이라이트 표시

## LSTM 개념

### LSTM Networks

LSTM은 RNN의 한 종류로, 긴 의존 기간을 필요로 하는 학습을 수행할 능력을 가지고 있다.(기존 RNN의 한계를 극복)

LSTM은 긴 의존 기간의 문제를 피하기 위해 명시적으로 설계되었다. 즉, 긴 시간 동안의 정보를 기억하는 것은 모델의 **기본적인 행동**으로 설정하고 모델이 그것을 배우기 위해서 노력하지 않도록 한 것이다.

**RNN**

![week4_12](https://github.com/Kyeong6/whatever/assets/100195725/5587e811-2c9c-4ac8-a9b9-53edaf90b9d4)


RNN은 neural network 모듈(green box)을 반복시키는 체인과 같은 형태를 하고 있다. 기본적인 RNN에서 이렇게 반복되는 모듈은 굉장히 단순한 구조를 가지고 있다. 

예를 들어, tanh layer 한 층을 들 수 있다.

**LSTM**

![week4_13](https://github.com/Kyeong6/whatever/assets/100195725/6828e798-99ba-47cc-ba87-e93e452709ad)


LSTM도 RNN과 같이 체인 구조를 가지고 있지만, 각 반복 모듈은 다른 구조를 가지고 있다. 4개의 layer가 **특별한 방식**으로 서로 정보를 주고 받도록 설계되어 있다. 

**이해를 돕기위한 기호 설명**

![week4_14](https://github.com/Kyeong6/whatever/assets/100195725/697d7c50-1d92-40dc-a9f1-21cdb7871d21)


각 선(Line) : 한 노드의 output을 다른 노드의 input으로 vector 전체를 보내는 흐름을 나타낸다. 

분홍색 동그라미 : vector 합과 같은 pointwise operation을 나타낸다. (사칙연산 개념)

노란색 박스 : 학습된 neural network layer

합쳐지는 선 : concatenation을 의미

갈라지는 선 : 정보를 복사해서 다른 쪽을 보내는 fork 의미

### LSTM 아이디어

![week4_15](https://github.com/Kyeong6/whatever/assets/100195725/e60af677-0be7-45e0-8e34-db87dd48e46f)


LSTM의 핵심은 **cell state**, 위 그림에서 수평으로 그어진 윗 선에 해당한다.

cell state는 컨베이어 벨트와 같아서, 작은 linear interaction만을 적용시키면서 전체 체인을 계속 구동시킨다. 정보가 전혀 바뀌지 않고 그대로 흐르게만 하는 것은 매우 쉽게 할 수 있다.

![week4_16](https://github.com/Kyeong6/whatever/assets/100195725/9b6380a9-6192-4804-b80c-b823d4f0cf85)


LSTM은 cell state에 뭔가를 더하거나 없앨 수 있는 능력이 존재하는데, 이를 **gate**라고 불리는 구조에 의해서 조심스럽게 제어된다.

Sigmoid layer는 0과 1사이의 숫자를 내보내는데, 해당 값은 각 컴포넌트가 얼마나 정보를 전달해야 하는지에 대한 척도를 의미한다. 값이 0이라면 “아무 것도 넘기지 말라”는 의미이고, 값이 1이라면 “모든 것을 넘겨라”라는 의미가 된다. 

LSTM은 3개의 gate를 가지고 있고, 이 gate들은 cell state를 보호하고 제어한다.

### LSTM 과정

LSTM의 첫 단계는 cell state로부터 어떤 정보를 버릴 것인지를 정하는 것으로 sigmoid layer에 의해 결정된다. 그러므로 이 단계의 gate를 **forget gate layer**라고 부른다.

이 단계에서는 h_(t-1)과 x_t을 받아서 0과 1 사이의 값을 C_(t-1)에 보내준다. 해당 값이 1이면 **모든 정보 보존**, 0이면 **버리기**가 된다

**예제**

이전 단어들을 바탕으로 다음 단어를 예측하는 언어 모델 문제로 생각해보면, 여기서 cell state는 현재 주어의 성별 정보를 가지고 있을 수도 있어서 그 성별에 맞는 대명사가 사용되도록 준비하고 있을 수도 있다. 그런데, 새로운 주어가 왔을 때 우리는 기존 주어의 성별 정보를 생각하고 싶지 않을 것이다. 

h_(t-1) : 이전 단어 

x_t : 새로운 단어

![week4_17](https://github.com/Kyeong6/whatever/assets/100195725/a24b3f42-61e4-47f0-bb92-cbe72f25d9ab)


다음 단계는 앞으로 들어오는 새로운 정보 중 어떤 것을 cell state에 저장할 것인 지를 정한다. 먼저 input gate lyaer라고 불리는 sigmoid layer가 어떤 값을 업데이트할 지 정한다. 그 다음에 tanh layer가 새로운 후보 값들인 ~C_t라는 vector를 만들고, cell state에 더할 준비를 한다. 이렇게 두 단계에서 나온 정보를 합쳐서 state를 업데이트할 재료를 만들게 된다. 

**예제**

기존 주어의 성별을 잊어버리기로 했고, 그 대신 새로운 주어의 성별 정보를 cell state에 더하고 싶을 것이다.

![week4_18](https://github.com/Kyeong6/whatever/assets/100195725/17d42c8d-95f7-4591-94cd-3f713e27fe12)


과거 state인 C_(t-1)를 업데이트해서 새로운 cell state인 C_t를 만들 것이다. 이미 이전 단계에서 어떤 값을 얼마나 업데이트해야 할 지 정해놨으므로 해당 단계에서는 실천만 하면 된다. 

이전 state에 f_t를 곱해서 가장 첫 단계에서 잊어버리기로 정했던 것을 실제로 잊어버린다. 이후 i_t * ~C_t를 더한다. 이 더하는 값은 두 번째 단계에서 업데이트 하기로 한 값을 얼마나 업데이트할 지 정한 만큼 scale한 값이 된다. 

**예제**

실제로 이전 주어의 성별 정보를 없애고, 새로운 정보를 더하게 되는데 이는 지난 단계들에서 다 정했던 것들을 실천만 하는 단계임을 다시 확인할 수 있다.

![week4_19](https://github.com/Kyeong6/whatever/assets/100195725/7db32b0d-9cdf-48f3-8cac-7dd0b88cb1eb)


마지막으로 무엇을 output으로 내보낼 지 정하는 일이 남았다. output은 cell state를 바탕으로 필터된 값이 될 것이다. 가장 먼저, sigmoid layer에 input 데이터를 태워서 cell state의 어느 부분을 output으로 내보낼 지를 정한다. 그리고 나서 cell state를 tanh layer에 태워서 -1과 1사이의 값을 받은 뒤에 방금 전에 계산한 sigmoid gate의 output과 곱해준다. 이렇게 하면 output으로 보내고자 하는 부분만 내보낼 수 있다.

**예제**

주어를 input으로 받았으므로 주어 다음에 오게 될 예측값인 output으로 적절한 답은 아마도 동사 개념의 무언가가 될 것이다. 예를 들어서 최종적인 output은 앞에서 본 주어가 단수형인지 복수형인지에 따라 그 형태가 달라질 수 도 있는 것이다.

![week4_20](https://github.com/Kyeong6/whatever/assets/100195725/4030bc49-c654-49ff-8425-23e34da00ece)


### 정리

![week4_21](https://github.com/Kyeong6/whatever/assets/100195725/13095026-e75f-4835-a5d5-7f0739ce2f9a)
