import pandas as pd
import requests
import time

# 네이버 지도 API 정보
client_id = '4i2qbbvpg9'  # 네이버 API 클라이언트 ID
client_secret = 'Nuqjv69noZ2UzMHQVa41mIFToQb8mV8uqxjKuory'  # 네이버 API 클라이언트 시크릿

# 데이터 로드
file_path = r'Z:\share\시형\충전소2.csv'
df = pd.read_csv(file_path, encoding='utf-8-sig')

# 네이버 지도 API를 이용해 주소로 위도와 경도 찾기
def get_lat_lng(address):
    url = f"https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret
    }
    params = {"query": address}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['meta']['totalCount'] > 0:
            lat = data['addresses'][0]['y']
            lng = data['addresses'][0]['x']
            return f"{lat},{lng}"
    return None

# 위도경도가 없는 경우 주소로 위도와 경도 검색
for index, row in df[df['위도경도'].isnull()].iterrows():
    address = row['주소']
    print(f"Fetching coordinates for: {address}")
    lat_lng = get_lat_lng(address)
    if lat_lng:
        print(f"Found coordinates: {lat_lng}")
        df.at[index, '위도경도'] = lat_lng
    else:
        print(f"No coordinates found for: {address}")

# 업데이트된 DataFrame을 저장
output_path = r'Z:\share\시형\충전소3.csv'
df.to_csv(output_path, encoding='utf-8-sig', index=False)
print(f"Updated CSV saved to {output_path}")
