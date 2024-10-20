import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from datetime import datetime

# 1. 데이터 불러오기 (예: 'used_car.csv' 파일)
data = pd.read_csv('Z:/share/시형/used_car.csv', encoding='euc-kr')

# 2. '가격비율' 열 생성: 신차 가격 대비 중고차 가격 비율
data['가격비율'] = data['가격'] / data['신차가격']

# 3. 출고일을 DateTime으로 변환 후 사용 연수 계산
data['출고일'] = pd.to_datetime(data['출고일'], errors='coerce')
today = datetime.now()
data['사용연수'] = today.year - data['출고일'].dt.year - ((today.month < data['출고일'].dt.month) | (
            (today.month == data['출고일'].dt.month) & (today.day < data['출고일'].dt.day)))

# 4. 학습 데이터 준비: '차종', '사용연수', '주행거리', '신차가격'을 포함
X = pd.get_dummies(data[['차종', '사용연수', '주행거리', '신차가격']], columns=['차종'])
y = data['가격비율']

# 5. 데이터 분할
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 6. XGBoost 모델 초기화 및 학습
xgb_model = XGBRegressor(random_state=42)
xgb_model.fit(X_train, y_train)


# 7. 예측 함수 정의
def predict_price(car_type, initial_price, years_used, total_km):
    # 예측 데이터 준비
    input_data = pd.DataFrame({
        '사용연수': [years_used],
        '주행거리': [total_km],
        '신차가격': [initial_price]
    })

    # 학습 데이터의 모든 열을 포함하도록 열 추가 및 초기화
    input_data = pd.concat(
        [input_data, pd.DataFrame(columns=[col for col in X.columns if col not in input_data.columns])], axis=1)
    input_data.fillna(0, inplace=True)  # 누락된 열 값 0으로 채움
    input_data = input_data.infer_objects()  # 데이터 타입 유추하여 명시적으로 지정

    # 해당 차종 열을 1로 설정 (존재하지 않는 차종이면 모두 0)
    if f'차종_{car_type}' in input_data.columns:
        input_data[f'차종_{car_type}'] = 1

    # 예측 수행
    input_data = input_data[X.columns]  # 열 순서 맞춤
    predicted_ratio = xgb_model.predict(input_data)
    predicted_price = predicted_ratio[0] * initial_price
    return predicted_price


# 8. 예시 예측: 차종, 신차 가격, 사용 연수, 주행 거리
predicted_price = predict_price('SUV', 55000000, 5, 50000)
print(f"Predicted Price: {predicted_price:.2f} KRW")

predicted_price = predict_price('준중형', 45000000, 1, 10000)
print(f"Predicted Price: {predicted_price:.2f} KRW")
