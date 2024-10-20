import pandas as pd
from sqlalchemy import create_engine

# 데이터베이스 연결 정보 설정
db_url = "mysql+pymysql://ash:Dkstlgud0208!@119.200.223.190:3306/project"
engine = create_engine(db_url)

# CSV 파일을 DataFrame으로 로드
file_path = r'Z:\share\시형\subsidy_avg.csv'
df = pd.read_csv(file_path, encoding='utf-8-sig')

# DataFrame을 SQL 테이블로 저장
df.to_sql('subsidy_avg', con=engine, if_exists='append', index=False)