import pandas as pd
import pymysql

# MySQL 연결 설정
connection = pymysql.connect(
    host='119.200.223.190',
    user='ash',
    password='Dkstlgud0208!',
    database='project',
    charset='utf8mb4'
)

# CSV 파일 불러오기
df = pd.read_csv('전기차_보조금2.csv')

# 테이블에 데이터 삽입
try:
    with connection.cursor() as cursor:
        for index, row in df.iterrows():
            sql = """
            INSERT INTO subsidy (도, 시, 차종, 제조사, 모델명, 국가보조금, 지자체보조금)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                row['도'],
                row['시'],
                row['차종'],
                row['제조사'],
                row['모델명'],
                row['국가보조금'],
                row['지자체보조금']
            ))
    connection.commit()
finally:
    connection.close()