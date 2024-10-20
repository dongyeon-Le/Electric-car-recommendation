import csv
import mysql.connector

# MySQL 데이터베이스에 연결
connection = mysql.connector.connect(
    host='119.200.223.190',  # MySQL 서버 주소
    user='ash',  # MySQL 사용자 이름
    password='Dkstlgud0208!',  # MySQL 비밀번호
    database='project',  # 사용할 데이터베이스 이름
    port='3306'  # MySQL 포트
)

cursor = connection.cursor()

# CSV 파일 경로
csv_file_path = "전기차_보조금3.csv"

# CSV 파일 열기
with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        insert_query = """
        INSERT INTO ev_car (차종, 제조사, 모델명)
        VALUES (%s, %s, %s)
        """

        # 행 데이터를 튜플로 변환하여 삽입
        cursor.execute(insert_query, (
            row['차종'], row['제조사'], row['모델명']
        ))

# 커밋하고 연결 닫기
connection.commit()
cursor.close()
connection.close()