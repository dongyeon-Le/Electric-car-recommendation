import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from sqlalchemy import create_engine
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split


# MySQL 데이터베이스 연결 및 데이터 로드
def load_data_from_mysql():
    engine = create_engine("mysql+mysqlconnector://ash:Dkstlgud0208!@119.200.223.190:3306/project")
    query = "SELECT 출고일, 주행거리, 가격, 신차가격 FROM used_car"
    data = pd.read_sql(query, engine)
    return data


# 모델 학습 함수
def train_model():
    data = load_data_from_mysql()
    today = datetime.now()
    data['출고일'] = pd.to_datetime(data['출고일'] + '-01')
    data['운행일'] = (today - data['출고일']).dt.days
    X = data[['운행일', '주행거리', '신차가격']]
    y = data['가격']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = GradientBoostingRegressor(random_state=42)
    model.fit(X_train, y_train)
    return model


# 연도별 가격 예측
def predict_yearly_depreciation(years, mileage, new_price, model):
    yearly_prices = []
    for year in range(1, years + 1):
        운행일 = year * 365
        input_data = pd.DataFrame([[운행일, mileage, new_price]], columns=['운행일', '주행거리', '신차가격'])
        predicted_price = model.predict(input_data)
        yearly_prices.append(predicted_price[0])
    return yearly_prices


# 연도별 가격 추이 그래프 생성 및 표시
def generate_yearly_depreciation_graph(yearly_data, title):
    fig, ax = plt.subplots()
    ax.plot(range(1, len(yearly_data) + 1), yearly_data, marker='o', color='blue')
    ax.set_xlabel('연도')
    ax.set_ylabel('예상 가격 (원)')
    ax.set_title(title)

    # 그래프 표시
    plt.show()


# 예제 사용 (10년간 가격 하락 추이 예측)
model = train_model()
yearly_data = predict_yearly_depreciation(15, 100000, 30000000, model)
generate_yearly_depreciation_graph(yearly_data, "연도별 차량 가격 하락 추이")
