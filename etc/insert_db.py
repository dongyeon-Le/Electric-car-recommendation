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
csv_file_path = "C:/ev/etc/all_car.csv"

# CSV 파일 열기
with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)

    # 각 행을 읽고 MySQL에 삽입 98개
    for row in reader:
        def clean_value(value):
            return value if value != '' else None

        insert_query = """
        INSERT INTO car (브랜드, 모델명, 세부모델명, 차종, 트림명, 가격, 전장, 전폭, 전고, 축거, 윤거_전, 윤거_후,
                         오버행_전, 오버행_후, 차음_유리, 자외선_차단유리, 엔진형식, 배기량, 최고출력, 최대토크, 최고속도,
                         제로백, 친환경, 연료, 연료탱크, CO2_배출, 배터리_용량, 배터리_전압, 배터리_제조사, 배터리_종류,
                         충전방식_급속, 충전방식_완속, 충전시간_급속, 충전시간_완속, 에너지소비효율, 복합연비, 고속연비,
                         도심연비, 복합전비, 고속전비, 도심전비, 복합_주행거리, 고속_주행거리, 도심_주행거리, 정속주행,
                         변속기, 굴림방식, 브레이크_전, 브레이크_후, 서스펜션_전, 서스펜션_후, 타이어_전, 타이어_후,
                         휠_전, 휠_후, 주차보조, 주행안전, 보행자_안전, 공회전_제한장치, 에어백, 도어포켓_라이트,
                         엠비언트_라이트, 룸미러, 헤드램프, 헤드램프_부가기능, 주간_주행등, 리어_램프, 전방_안개등,
                         아웃_사이드미러, 주요기능, 승차정원, 시트배열, 시트재질, 동승석, 운전석, 뒷좌석_송풍구,
                         뒷좌석_측면커튼, 뒷좌석_후면커튼, 계기판, 스티어링_휠, 화면크기, 사운드시스템, 스피커,
                         적재량, 적재함_길이, 적재함_너비, 적재함_높이, 트렁크, 트렁크_전_용량, 트렁크_후_용량,
                         에어컨, 엔진시동, 와이퍼, 파워_아웃렛, 온도조절_범위, 루프, 주차_브레이크, 부가기능)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # 행 데이터를 튜플로 변환하여 삽입
        cursor.execute(insert_query, (
            clean_value(row['브랜드']), clean_value(row['모델명']), clean_value(row['세부모델명']), clean_value(row['차종']),
            clean_value(row['트림명']), clean_value(row['가격']), clean_value(row['전장']), clean_value(row['전폭']),
            clean_value(row['전고']), clean_value(row['축거']), clean_value(row['윤거 (전)']), clean_value(row['윤거 (후)']),
            clean_value(row['오버행 (전)']), clean_value(row['오버행 (후)']), clean_value(row['차음 유리']),
            clean_value(row['자외선 차단유리']), clean_value(row['엔진형식']), clean_value(row['배기량']),
            clean_value(row['최고출력']), clean_value(row['최대토크']), clean_value(row['최고속도']),
            clean_value(row['제로백']), clean_value(row['친환경']), clean_value(row['연료']), clean_value(row['연료탱크']),
            clean_value(row['CO₂ 배출']), clean_value(row['배터리 용량']), clean_value(row['배터리 전압']),
            clean_value(row['배터리 제조사']), clean_value(row['배터리 종류']), clean_value(row['충전방식 (급속)']),
            clean_value(row['충전방식 (완속)']), clean_value(row['충전시간 (급속)']), clean_value(row['충전시간 (완속)']),
            clean_value(row['에너지소비효율']), clean_value(row['복합연비']), clean_value(row['고속연비']),
            clean_value(row['도심연비']), clean_value(row['복합전비']), clean_value(row['고속전비']), clean_value(row['도심전비']),
            clean_value(row['복합 주행거리']), clean_value(row['고속 주행거리']), clean_value(row['도심 주행거리']),
            clean_value(row['정속주행']), clean_value(row['변속기']), clean_value(row['굴림방식']),
            clean_value(row['브레이크 (전)']), clean_value(row['브레이크 (후)']), clean_value(row['서스펜션 (전)']),
            clean_value(row['서스펜션 (후)']), clean_value(row['타이어 (전)']), clean_value(row['타이어 (후)']),
            clean_value(row['휠 (전)']), clean_value(row['휠 (후)']), clean_value(row['주차보조']),
            clean_value(row['주행안전']), clean_value(row['보행자 안전']), clean_value(row['공회전 제한장치']),
            clean_value(row['에어백']), clean_value(row['도어포켓 라이트']), clean_value(row['엠비언트 라이트']),
            clean_value(row['룸미러']), clean_value(row['헤드램프']), clean_value(row['헤드램프 부가기능']),
            clean_value(row['주간 주행등']), clean_value(row['리어 램프']), clean_value(row['전방 안개등']),
            clean_value(row['아웃 사이드미러']), clean_value(row['주요기능']), clean_value(row['승차정원']),
            clean_value(row['시트배열']), clean_value(row['시트재질']), clean_value(row['동승석']),
            clean_value(row['운전석']), clean_value(row['뒷좌석 송풍구']), clean_value(row['뒷좌석 측면커튼']),
            clean_value(row['뒷좌석 후면커튼']), clean_value(row['계기판']), clean_value(row['스티어링 휠']),
            clean_value(row['화면크기']), clean_value(row['사운드시스템']), clean_value(row['스피커']),
            clean_value(row['적재량']), clean_value(row['적재함 길이']), clean_value(row['적재함 너비']),
            clean_value(row['적재함 높이']), clean_value(row['트렁크']), clean_value(row['트렁크 (전) 용량']),
            clean_value(row['트렁크 (후) 용량']), clean_value(row['에어컨']), clean_value(row['엔진시동']),
            clean_value(row['와이퍼']), clean_value(row['파워 아웃렛']), clean_value(row['온도조절 범위']),
            clean_value(row['루프']), clean_value(row['주차 브레이크']), clean_value(row['부가기능'])
        ))

# 커밋하고 연결 닫기
connection.commit()
cursor.close()
connection.close()