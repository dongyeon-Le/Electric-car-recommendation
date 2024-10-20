import pandas as pd
from sqlalchemy import create_engine

# 데이터베이스 연결 정보 설정
db_url = "mysql+pymysql://ash:Dkstlgud0208!@119.200.223.190:3306/project"
engine = create_engine(db_url)

# CSV 파일을 DataFrame으로 로드
file_path = r'Z:\share\시형\참조.csv'
df = pd.read_csv(file_path, encoding='utf-8-sig')

# 컬럼 이름을 데이터베이스 테이블에 맞게 수정
df = df.rename(columns={'충전 속도': '충전속도'})

# DataFrame을 SQL 테이블로 저장
df.to_sql('apt_charger', con=engine, if_exists='append', index=False)