import requests

### API KEY 입력 (보안 주의)
client_id = '4i2qbbvpg9'
client_secret = 'Nuqjv69noZ2UzMHQVa41mIFToQb8mV8uqxjKuory'


### 출발/목적지 입력
##### 주의:  문자열로 입력.  "경도,위도" 순서로 입력
start_point = "126.7958500,35.1584118"  # 출발위치  예시 : 서울역
end_point   = "127.5794663,34.9836508"  # 도착위치  예시 : 강남 교보문고
option = 'trafast' # 탐색옵션

### 경로 탐색 요청하기
headers = {
    "X-NCP-APIGW-API-KEY-ID" : client_id,
    "X-NCP-APIGW-API-KEY" : client_secret
}

url = f'https://naveropenapi.apigw.ntruss.com/map-direction-15/v1/driving?start={start_point}&goal={end_point}&option={option}'

r = requests.get(url, headers = headers)
print(r.json())

### 응답결과 정리

summary = r.json().get('route').get(option)[0]['summary']
# 거리(미터)
distance = summary['distance']  # meters 단위

# 소요시간(분)
duration = summary['duration']  # 소요시간 (millisecond 단위)
duration_second = duration / 1000 # 소요시간(초단위)
duration_minute = duration_second / 60 # 소요시간(분단위)

print(distance, duration_minute)  # 거리(미터),  소요시간(분)