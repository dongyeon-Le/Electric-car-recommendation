import pandas as pd

# CSV 파일 로드
charging_station_path = r'Z:\share\시형\충전소.csv'
charging_fee_path = r'Z:\share\시형\충전요금.csv'

charging_station_df = pd.read_csv(charging_station_path, encoding='utf-8-sig')
charging_fee_df = pd.read_csv(charging_fee_path, encoding='utf-8-sig')

# 회원가와 비회원가를 담을 새로운 컬럼 추가
charging_station_df['회원가'] = None
charging_station_df['비회원가'] = None

# 충전량과 운영기관을 기준으로 요금을 추가하는 로직
for index, station_row in charging_station_df.iterrows():
    operator = station_row['운영기관']
    charger_type = None

    # `충전량` 칼럼에서 급속/완속을 구분
    if 'dc' in station_row['충전량'].lower():
        charger_type = '급속'
    elif 'ac' in station_row['충전량'].lower():
        charger_type = '완속'

    # 구분이 설정되지 않으면 다음 행으로 넘어감
    if not charger_type:
        continue

    # `충전요금` 데이터프레임에서 `기관명`이 `운영기관`에 포함되어 있는지 검사
    fee_info = charging_fee_df[
        (charging_fee_df['구분'] == charger_type) &
        (charging_fee_df['기관명'].apply(lambda name: name in operator))
        ]

    if not fee_info.empty:
        # 첫 번째 매칭된 결과의 회원가와 비회원가를 할당
        charging_station_df.at[index, '회원가'] = fee_info['회원가'].values[0]
        charging_station_df.at[index, '비회원가'] = fee_info['비회원가'].values[0]
    else:
        # 매칭 안 된 경우 빈칸으로 유지
        charging_station_df.at[index, '회원가'] = ''
        charging_station_df.at[index, '비회원가'] = ''

# 업데이트된 DataFrame을 저장
output_path = r'Z:\share\시형\충전소_with_fees.csv'
charging_station_df.to_csv(output_path, encoding='utf-8-sig', index=False)

print(f"Updated CSV saved to {output_path}")
