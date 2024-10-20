import pandas as pd
from sqlalchemy import create_engine

# 1. 데이터베이스 연결 설정
# MariaDB 연결 URL
db_url = "mysql+pymysql://ash:Dkstlgud0208!@119.200.223.190:3306/project"
engine = create_engine(db_url)

# 2. CSV 파일을 DataFrame으로 로드 (Windows 네트워크 경로 사용)
file_path = r'Z:\share\시형\아파트.csv'  # 경로에 특수 문자가 있으므로 r''로 raw string 사용
df = pd.read_csv(file_path, encoding='utf-8-sig')

# 3. DataFrame을 SQL 테이블로 저장
df.to_sql('apt', con=engine, if_exists='append', index=False)