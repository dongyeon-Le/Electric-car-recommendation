import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from matplotlib.font_manager import FontProperties

# Nanum Gothic 폰트 설정
font_path = 'C:/Users/user/Desktop/NanumGothic.ttf'
font_prop = FontProperties(fname=font_path)

# SQLAlchemy를 사용하여 데이터베이스 연결 설정
db_connection_str = 'mysql+mysqlconnector://ash:Dkstlgud0208!@119.200.223.190/project'
engine = create_engine(db_connection_str)

# 특정 시 이름을 입력 받음
input_city = '서울특별시'  # 예시: 입력한 시 이름으로 변경

# SQL 쿼리 실행 (테이블에서 데이터를 가져오기)
query = "SELECT 도, 시, 평균 AS 지자체보조금_평균 FROM subsidy_avg ORDER BY 지자체보조금_평균 DESC;"
data = pd.read_sql(query, engine)

# 데이터 정렬 및 특정 시 정보 가져오기
data_sorted = data.sort_values(by='지자체보조금_평균', ascending=False).reset_index(drop=True)
city_data = data_sorted[data_sorted['시'] == input_city]

# 전체 평균 계산
overall_avg = data['지자체보조금_평균'].mean()

# 특정 시의 등수 확인
city_rank = data_sorted[data_sorted['시'] == input_city].index[0] + 1
total_count = len(data_sorted)

# 등수 출력
print(f"{input_city}의 평균 보조금은 전체에서 상위 {city_rank}위에 있으며, 총 {total_count}개 지역 중에서 비교됩니다.")

# 1대1 비교 그래프 생성
plt.figure(figsize=(8, 6))
plt.bar(['전체 평균', f'{input_city}'], [overall_avg, city_data['지자체보조금_평균'].values[0]], color=['gray', 'blue'])
plt.ylabel('Average Local Subsidy', fontproperties=font_prop)
plt.title(f'Comparison of {input_city} vs Overall Average', fontproperties=font_prop)
plt.xticks(fontproperties=font_prop)
plt.yticks(fontproperties=font_prop)
plt.tight_layout()
plt.show()
