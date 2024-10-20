import os
import pandas as pd

# 각 CSV 파일의 첫 번째 열을 칼럼 이름으로 처리하는 함수
def get_csv_columns_from_first_column(file_path):
    try:
        df = pd.read_csv(file_path, header=None)  # 헤더 없이 파일을 읽음
        first_column_as_columns = df.iloc[:, 0].tolist()  # 첫 번째 열을 칼럼으로 추출
        data = df.iloc[:, 1:].T  # 나머지 데이터를 가져옴
        data.columns = first_column_as_columns  # 첫 번째 열을 칼럼으로 설정
        return data
    except Exception as e:
        print(f"파일 {file_path} 에서 오류 발생: {e}")
        return pd.DataFrame()  # 오류가 발생할 경우 빈 DataFrame 반환

# 모든 CSV 파일을 하나의 DataFrame으로 합치는 함수
def merge_csv_files_into_one(directory_path):
    combined_df = pd.DataFrame()  # 결과를 저장할 빈 DataFrame
    all_columns = set()  # 모든 칼럼의 합집합을 저장할 집합

    # 디렉토리 내 모든 파일에 대해 반복
    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)

        # 파일의 데이터를 가져옴
        current_df = get_csv_columns_from_first_column(file_path)
        if not current_df.empty:
            all_columns.update(current_df.columns)  # 칼럼 합집합 업데이트
            combined_df = pd.concat([combined_df, current_df], axis=0, ignore_index=True)

    # 모든 칼럼의 합집합에 따라 DataFrame을 재구성 (존재하지 않는 칼럼은 빈 값으로 채움)
    combined_df = combined_df.reindex(columns=sorted(all_columns))

    # 요청한 순서로 칼럼을 재배치
    column_order = [
        # 기본 정보
        '브랜드', '모델명', '세부모델명', '차종', '트림명', '가격',
        # 차량 크기 및 외관
        '전장', '전폭', '전고', '축거', '윤거 (전)', '윤거 (후)', '오버행 (전)', '오버행 (후)', '차음 유리', '자외선 차단유리',
        # 엔진 및 성능
        '엔진형식', '배기량', '최고출력', '최대토크', '최고속도', '제로백', '친환경',
        # 연료 및 배터리
        '연료', '연료탱크', 'CO₂ 배출', '배터리 용량', '배터리 전압', '배터리 제조사', '배터리 종류',
        '충전방식 (급속)', '충전방식 (완속)', '충전시간 (급속)', '충전시간 (완속)', '에너지소비효율',
        # 주행 및 연비
        '복합연비', '고속연비', '도심연비', '복합 주행거리', '고속 주행거리', '도심 주행거리', '정속주행',
        # 변속기 및 구동 방식
        '변속기', '굴림방식',
        # 브레이크 및 서스펜션
        '브레이크 (전)', '브레이크 (후)', '서스펜션 (전)', '서스펜션 (후)',
        # 타이어 및 휠
        '타이어 (전)', '타이어 (후)', '휠 (전)', '휠 (후)',
        # 안전 및 주행 보조
        '주차보조', '주행안전', '보행자 안전', '공회전 제한장치', '에어백',
        # 내외부 장비 및 편의 기능
        '도어포켓 라이트', '엠비언트 라이트', '룸미러', '헤드램프', '헤드램프 부가기능', '주간 주행등',
        '리어 램프', '전방 안개등', '아웃 사이드미러', '주요기능',
        # 내부 공간 및 좌석
        '승차정원', '시트배열', '시트재질', '동승석', '운전석', '뒷좌석 송풍구', '뒷좌석 측면커튼', '뒷좌석 후면커튼',
        # 계기판 및 디지털 기능
        '계기판', '스티어링 휠', '화면크기',
        # 엔터테인먼트 및 오디오
        '사운드시스템', '스피커',
        # 트렁크 및 적재 용량
        '적재량', '적재함 길이', '적재함 너비', '적재함 높이', '트렁크', '트렁크 (전) 용량', '트렁크 (후) 용량',
        # 기타 부가기능 및 편의장치
        '에어컨', '엔진시동', '와이퍼', '파워 아웃렛', '온도조절 범위', '루프', '주차 브레이크', '부가기능',
        '고속전비', '복합전비', '도심전비'
    ]

    # 지정된 순서로 칼럼을 재정렬, 없는 칼럼은 무시
    combined_df = combined_df.reindex(columns=[col for col in column_order if col in combined_df.columns])

    return combined_df

# CSV 파일들이 저장된 디렉토리 경로
directory_path = "C:/Users/user/Desktop/기업 프로젝트/csv/car"

# 모든 CSV 파일을 하나의 DataFrame으로 합치기
combined_df = merge_csv_files_into_one(directory_path)

# 결과를 UTF-8 with BOM으로 CSV 파일로 저장
combined_df.to_csv("combined_output.csv", index=False, encoding="utf-8-sig")
print("모든 CSV 파일이 combined_output.csv로 합쳐졌으며, 요청하신 순서대로 정렬되었습니다.")
