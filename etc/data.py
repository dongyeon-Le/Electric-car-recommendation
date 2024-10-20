import os
import pandas as pd


# 첫 번째 열을 칼럼 이름으로 처리하고 '차종' 데이터를 추출하는 함수
def get_csv_car_type_from_first_column(file_path):
    try:
        df = pd.read_csv(file_path, header=None)  # 헤더 없이 파일을 읽음
        df = df.T  # 파일을 전치하여 첫 번째 열을 칼럼 이름으로 변환
        df.columns = df.iloc[0]  # 첫 번째 행을 칼럼 이름으로 설정
        df = df[1:]  # 나머지 데이터를 남김
        if '차종' in df.columns:  # '차종' 칼럼이 있는지 확인
            car_type_data = df['차종'].unique()[0]  # '차종' 칼럼의 값을 추출
            return car_type_data
        else:
            print(f"파일 {file_path} 에서 '차종' 칼럼을 찾을 수 없습니다.")  # 디버깅용 메시지
            return None  # '차종' 칼럼이 없으면 None 반환
    except Exception as e:
        print(f"파일 {file_path} 에서 오류 발생: {e}")  # 오류 메시지 출력
        return None  # 오류 발생 시 None 반환


# 파일 경로와 '차종' 데이터를 기반으로 그룹화할 딕셔너리
car_type_grouping = {}

# 데이터 폴더 경로
car_folder_path = "C:/Users/user/Desktop/기업 프로젝트/csv/car"

# 디렉토리 내 모든 파일을 순회하며 '차종' 데이터를 기반으로 그룹화
for file_name in os.listdir(car_folder_path):
    file_path = os.path.join(car_folder_path, file_name)
    car_type_data = get_csv_car_type_from_first_column(file_path)

    if car_type_data:  # '차종' 데이터가 있는 경우에만 처리
        if car_type_data in car_type_grouping:
            car_type_grouping[car_type_data].append(file_name)
        else:
            car_type_grouping[car_type_data] = [file_name]

# 결과를 텍스트 파일로 저장
output_file = "output.txt"
with open(output_file, "w", encoding="utf-8") as f:
    for car_type, files in car_type_grouping.items():
        f.write(f"'차종': {car_type}\n")
        f.write(f"파일 목록: {files}\n\n")

print(f"결과가 {output_file} 파일에 저장되었습니다.")
