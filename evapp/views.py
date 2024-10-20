from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Car, Oil, EVCar, Subsidy, Apt, AptCharger, Charger, UsedCar
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from difflib import get_close_matches
from math import radians, sin, cos, sqrt, atan2
import requests
import pandas as pd
from sqlalchemy import create_engine
from matplotlib.font_manager import FontProperties
import os
from django.conf import settings
from io import BytesIO
import base64
import matplotlib
import matplotlib.pyplot as plt
import re
from django.db import connection
import numpy as np
from decimal import Decimal
from datetime import datetime
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from django.db.models import Max, Min, Case, When, Value, CharField, Q, F
from django.db.models.functions import Concat
from collections import defaultdict


client_id = '4i2qbbvpg9'
client_secret = 'Nuqjv69noZ2UzMHQVa41mIFToQb8mV8uqxjKuory'

def homepage(request):
    return render(request, 'homepage.html')


def charger500(request):
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')

    if lat is None or lng is None:
        return JsonResponse({'error': 'Latitude and longitude are required.'}, status=400)

    try:
        lat, lng = float(lat), float(lng)
    except ValueError:
        return JsonResponse({'error': 'Invalid latitude or longitude format.'}, status=400)

    nearby_chargers = []

    for charger in Charger.objects.filter(이용자제한='이용가능'):
        distance = calculate_distance(lat, lng, charger.위도, charger.경도)

        if distance <= 500:
            charger_info = {
                'og_type': charger.충전량,
                'type': '완속' if charger.충전량 in ['AC3상', 'AC완속', '완속(30kW단독)'] else '급속',
                'address': charger.주소,
                'name': charger.충전소명,
                'company': charger.운영기관,
                'charger_type': charger.충전기타입,
                'member_price': float(charger.회원가) if charger.회원가 else 0.0,
                'non_member_price': float(charger.비회원가) if charger.비회원가 else 0.0,
                'latitude': float(charger.위도),
                'longitude': float(charger.경도)
            }
            nearby_chargers.append(charger_info)

    return JsonResponse({'chargers': nearby_chargers})

def mapTest(request):
    return render(request, 'map_test.html')

allow = {
    'type': ['경차', '세단', 'SUV', 'none'],
    'brand': ['k', 'none'],
    'price': ['1', '2', '3', '4', '5', '6'],
    'years': [str(x) for x in range(1, 16)],
    'km': [str(x) for x in range(5000, 50001, 5000)]
}

def calculate_distance(lat1, lng1, lat2, lng2):
    R = 6371000  # Earth radius in meters
    phi1 = radians(lat1)
    phi2 = radians(float(lat2))  # Convert Decimal to float
    delta_phi = radians(float(lat2) - lat1)  # Convert Decimal to float
    delta_lambda = radians(float(lng2) - lng1)  # Convert Decimal to float

    a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

city_mapping = {
    "광주": "광주광역시",
    "대구": "대구광역시",
    "대전": "대전광역시",
    "부산": "부산광역시",
    "서울": "서울특별시",
    "세종특별자치시": "세종특별자치시",
    "울산": "울산광역시",
    "인천": "인천광역시",
    "제주특별자치도": "제주특별자치도"
}

def word_filter(address):
    first_word = address.split()[0]

    if first_word in city_mapping:
        return city_mapping[first_word]

    parts = address.split()
    if len(parts) >= 2:
        return parts[1]  # 두 번째 단어 반환
    return None

font_path = os.path.join(settings.STATICFILES_DIRS[0], 'fonts', 'NanumGothic.ttf')
font_prop = FontProperties(fname=font_path)

conn = 'mysql+mysqlconnector://ash:Dkstlgud0208!@119.200.223.190/project'
engine = create_engine(conn)

matplotlib.use('Agg')

def ev_test(request):
    context = {}
    if 'type' in request.GET:
        type = request.GET.get('type')
        if type not in allow['type']:
            return redirect('ev_test')  # 잘못된 값이 들어오면 기본 페이지로 리디렉션
        context['type'] = type

        if 'brand' in request.GET:
            brand = request.GET.get('brand')
            if brand not in allow['brand']:
                return redirect('ev_test')
            context['brand'] = brand

            if 'price' in request.GET:
                price = request.GET.get('price')
                if price not in allow['price']:
                    return redirect('ev_test')
                context['price'] = price

                if 'years' in request.GET and 'km' in request.GET:
                    years = request.GET.get('years')
                    km = request.GET.get('km')
                    if years not in allow['years'] or km not in allow['km']:
                        return redirect('ev_test')
                    context['years'] = years
                    context['km'] = km

                    if 'home' in request.GET and 'work' in request.GET and 'homeLat' in request.GET and 'homeLng' in request.GET and 'workLat' in request.GET and 'workLng' in request.GET:
                        home = request.GET.get('home')
                        work = request.GET.get('work')
                        homeLat = float(request.GET.get('homeLat'))
                        homeLng = float(request.GET.get('homeLng'))
                        workLat = float(request.GET.get('workLat'))
                        workLng = float(request.GET.get('workLng'))

                        home_word = word_filter(home)

                        start = f"{homeLng},{homeLat}"
                        end = f"{workLng},{workLat}"
                        option = 'trafast'
                        headers = {
                            "X-NCP-APIGW-API-KEY-ID": client_id,
                            "X-NCP-APIGW-API-KEY": client_secret
                        }

                        url = f'https://naveropenapi.apigw.ntruss.com/map-direction-15/v1/driving?start={start}&goal={end}&option={option}'
                        response = requests.get(url, headers=headers)
                        route_data = response.json()

                        path = []
                        distance = 0

                        if 'route' in route_data and 'trafast' in route_data['route']:
                            path_data = route_data['route']['trafast'][0]
                            path = path_data.get('path', [])
                            distance = path_data['summary'].get('distance', 0)
                        else:
                            print("Error: Expected 'trafast' data not found in response.")

                        # Initialize counters for chargers
                        home_slow = 0
                        home_fast = 0
                        work_slow = 0
                        work_fast = 0

                        nearby_chargers = []
                        for charger in Charger.objects.filter(이용자제한='이용가능'):
                            home_distance = calculate_distance(homeLat, homeLng, charger.위도, charger.경도)
                            work_distance = calculate_distance(workLat, workLng, charger.위도, charger.경도)

                            # Check charger type and count based on distance
                            charger_type = '완속' if charger.충전량 in ['AC3상', 'AC완속', '완속(30kW단독)'] else '급속'

                            if home_distance <= 500:
                                if charger_type == '완속':
                                    home_slow += 1
                                else:
                                    home_fast += 1

                            if work_distance <= 500:
                                if charger_type == '완속':
                                    work_slow += 1
                                else:
                                    work_fast += 1

                            if home_distance <= 500 or work_distance <= 500:
                                nearby_chargers.append({
                                    'og_type': charger.충전량,
                                    'type': charger_type,
                                    'address': charger.주소,
                                    'name': charger.충전소명,
                                    'company': charger.운영기관,
                                    'charger_type': charger.충전기타입,
                                    'member_price': float(charger.회원가) if charger.회원가 else 0.0,
                                    'non_member_price': float(charger.비회원가) if charger.비회원가 else 0.0,
                                    'latitude': float(charger.위도),
                                    'longitude': float(charger.경도)
                                })

                        query = "SELECT 도, 시, 평균 FROM subsidy_avg ORDER BY 평균 DESC;"
                        data = pd.read_sql(query, engine)

                        data_sorted = data.sort_values(by='평균', ascending=False).reset_index(drop=True)
                        city_data = data_sorted[data_sorted['시'] == home_word]

                        overall_avg = data['평균'].mean()
                        city_rank = data_sorted[data_sorted['시'] == home_word].index[0] + 1
                        total_count = len(data_sorted)

                        city_avg = city_data['평균'].values[0]
                        percent_diff = ((city_avg - overall_avg) / overall_avg) * 100  # 퍼센트 차이 계산
                        percent_diff_text = f"{percent_diff:+.1f}%"

                        color = 'blue' if percent_diff > 0 else 'red'

                        # 그래프 생성 및 퍼센트 차이 표시
                        fig, ax = plt.subplots(figsize=(8, 5))
                        bars = ax.bar(['전체 평균', home_word], [overall_avg, city_avg], color=['#014fa2', '#00abc5'])
                        ax.set_xticks([0, 1])
                        ax.set_xticklabels(['전체 평균', home_word], fontproperties=font_prop, fontsize=16)
                        ax.set_ylabel('지역 평균 지자체 보조금', fontproperties=font_prop, fontsize=16)
                        ax.set_title(f'{home_word} 지자체 보조금', fontproperties=font_prop, fontsize=16)

                        # 퍼센트 차이를 오른쪽 막대 위에 표시
                        ax.text(1, city_avg + (city_avg * 0.02), f"{percent_diff_text}", ha='center',
                                fontproperties=font_prop, fontsize=14, color=color)

                        # 그래프를 이미지로 변환
                        buffer = BytesIO()
                        plt.savefig(buffer, format='png')
                        buffer.seek(0)
                        graph_img = base64.b64encode(buffer.read()).decode('utf-8')
                        buffer.close()
                        plt.close(fig)

                        home_score = home_slow * 10 + home_fast * 20
                        work_score = work_slow * 10 + work_fast * 20

                        charger_score = home_score + work_score

                        context = {
                            'homeLat': homeLat,
                            'homeLng': homeLng,
                            'workLat': workLat,
                            'workLng': workLng,
                            'nearby_chargers': nearby_chargers,
                            'path': path,
                            'distance': distance,
                            'home_slow': home_slow,
                            'home_fast': home_fast,
                            'work_slow': work_slow,
                            'work_fast': work_fast,
                            'home_word': home_word,
                            'city_rank': city_rank,
                            'total_count': total_count,
                            'graph_img': graph_img,
                            'charger_score': charger_score,

                            'type': type,
                            'brand': brand,
                            'price': price,
                            'years': years,
                            'km': km,
                        }

                        return render(request, 'ev_test.html', context)
                    return render(request, 'ev_test5.html', context)
                return render(request, 'ev_test4.html', context)
            return render(request, 'ev_test3.html', context)
        return render(request, 'ev_test2.html', context)
    return render(request, 'ev_test1.html')


def verses(request):
    return render(request, 'verses.html')

def getCar(request):
    brand = request.GET.get('brand', None)
    car_type = request.GET.get('car_type', None)
    fuel = request.GET.get('fuel', None)
    model = request.GET.get('model', None)
    detail_model = request.GET.get('detail_model', None)

    # 로깅을 통해 확인
    print(f"브랜드: {brand}, 차종: {car_type}, 연료: {fuel}, 모델: {model}, 세부모델: {detail_model}")

    # 브랜드 목록 반환
    if not brand and not car_type and not fuel and not model:
        brands = Car.objects.values_list('브랜드', flat=True).distinct()
        return JsonResponse({'brands': list(brands)})

    # 차종 목록 반환
    if brand and not car_type and not fuel and not model:
        types = Car.objects.filter(브랜드=brand).values_list('차종', flat=True).distinct()
        return JsonResponse({'types': list(types)})

    # 연료 목록 반환
    if brand and car_type and not fuel and not model:
        fuels = Car.objects.filter(브랜드=brand, 차종=car_type).values_list('연료', flat=True).distinct()
        return JsonResponse({'fuels': list(fuels)})

    # 모델 목록 반환
    if brand and car_type and fuel and not model:
        models = Car.objects.filter(브랜드=brand, 차종=car_type, 연료=fuel).values_list('모델명', flat=True).distinct()
        return JsonResponse({'models': list(models)})

    # 세부 모델 목록 반환
    if brand and car_type and fuel and model and not detail_model:
        detail_models = Car.objects.filter(브랜드=brand, 차종=car_type, 연료=fuel, 모델명=model).values_list('세부모델명', flat=True).distinct()
        return JsonResponse({'detail_models': list(detail_models)})

    # 트림명 목록 반환
    if brand and car_type and fuel and model and detail_model:
        trims = Car.objects.filter(브랜드=brand, 차종=car_type, 연료=fuel, 모델명=model, 세부모델명=detail_model).values_list('트림명', flat=True).distinct()
        return JsonResponse({'trims': list(trims)})

    return JsonResponse({'error': 'Invalid request'}, status=400)


def getSpec(request):
    brand = request.GET.get('brand', None)
    car_type = request.GET.get('car_type', None)
    fuel = request.GET.get('fuel', None)
    model = request.GET.get('model', None)
    detail_model = request.GET.get('detail_model', None)
    trim = request.GET.get('trim', None)  # 트림명 추가

    # 로깅으로 받은 값 확인 (디버깅용)
    print(f"브랜드: {brand}, 차종: {car_type}, 연료: {fuel}, 모델: {model}, 세부모델: {detail_model}, 트림: {trim}")

    if brand and car_type and fuel and model and detail_model and trim:
        try:
            # 브랜드, 차종, 연료, 모델명, 세부모델명, 트림명으로 차량 정보 가져오기
            car = Car.objects.get(
                브랜드=brand, 차종=car_type, 연료=fuel, 모델명=model, 세부모델명=detail_model, 트림명=trim
            )
            # 필요한 스펙을 포함하는 데이터 준비
            specs = {
                'id': car.id,
                '사진': car.사진,
                '보조금_id': car.보조금_id,
                '브랜드': car.브랜드,
                '모델명': car.모델명,
                '세부모델명': car.세부모델명,
                '차종': car.차종,
                '트림명': car.트림명,
                '가격': car.가격,

                # 차량 크기 및 외관
                '전장': car.전장,
                '전폭': car.전폭,
                '전고': car.전고,
                '축거': car.축거,
                '윤거_전': car.윤거_전,
                '윤거_후': car.윤거_후,
                '오버행_전': car.오버행_전,
                '오버행_후': car.오버행_후,
                '차음_유리': car.차음_유리,
                '자외선_차단유리': car.자외선_차단유리,

                # 엔진 및 성능
                '엔진형식': car.엔진형식,
                '배기량': car.배기량,
                '최고출력': car.최고출력,
                '최대토크': car.최대토크,
                '최고속도': car.최고속도,
                '제로백': car.제로백,
                '친환경': car.친환경,

                # 연료 및 배터리
                '연료': car.연료,
                '연료탱크': car.연료탱크,
                'CO2_배출': car.CO2_배출,
                '배터리_용량': car.배터리_용량,
                '배터리_전압': car.배터리_전압,
                '배터리_제조사': car.배터리_제조사,
                '배터리_종류': car.배터리_종류,
                '충전방식_급속': car.충전방식_급속,
                '충전방식_완속': car.충전방식_완속,
                '충전시간_급속': car.충전시간_급속,
                '충전시간_완속': car.충전시간_완속,
                '에너지소비효율': car.에너지소비효율,

                # 연비 및 전비
                '복합연비': car.복합연비,
                '고속연비': car.고속연비,
                '도심연비': car.도심연비,
                '복합전비': car.복합전비,
                '고속전비': car.고속전비,
                '도심전비': car.도심전비,

                # 주행 관련
                '복합_주행거리': car.복합_주행거리,
                '고속_주행거리': car.고속_주행거리,
                '도심_주행거리': car.도심_주행거리,
                '정속주행': car.정속주행,

                # 구동 및 변속기
                '변속기': car.변속기,
                '굴림방식': car.굴림방식,

                # 브레이크 및 서스펜션
                '브레이크_전': car.브레이크_전,
                '브레이크_후': car.브레이크_후,
                '서스펜션_전': car.서스펜션_전,
                '서스펜션_후': car.서스펜션_후,

                # 타이어 및 휠
                '타이어_전': car.타이어_전,
                '타이어_후': car.타이어_후,
                '휠_전': car.휠_전,
                '휠_후': car.휠_후,

                # 안전 및 보조 기능
                '주차보조': car.주차보조,
                '주행안전': car.주행안전,
                '보행자_안전': car.보행자_안전,
                '공회전_제한장치': car.공회전_제한장치,
                '에어백': car.에어백,

                # 외부 장비 및 기능
                '도어포켓_라이트': car.도어포켓_라이트,
                '엠비언트_라이트': car.엠비언트_라이트,
                '룸미러': car.룸미러,
                '헤드램프': car.헤드램프,
                '헤드램프_부가기능': car.헤드램프_부가기능,
                '주간_주행등': car.주간_주행등,
                '리어_램프': car.리어_램프,
                '전방_안개등': car.전방_안개등,
                '아웃_사이드미러': car.아웃_사이드미러,

                # 내부 장비 및 기능
                '주요기능': car.주요기능,
                '승차정원': car.승차정원,
                '시트배열': car.시트배열,
                '시트재질': car.시트재질,
                '동승석': car.동승석,
                '운전석': car.운전석,
                '뒷좌석_송풍구': car.뒷좌석_송풍구,
                '뒷좌석_측면커튼': car.뒷좌석_측면커튼,
                '뒷좌석_후면커튼': car.뒷좌석_후면커튼,

                # 디지털 기능 및 계기판
                '계기판': car.계기판,
                '스티어링_휠': car.스티어링_휠,
                '화면크기': car.화면크기,

                # 엔터테인먼트
                '사운드시스템': car.사운드시스템,
                '스피커': car.스피커,

                # 트렁크 및 적재
                '적재량': car.적재량,
                '적재함_길이': car.적재함_길이,
                '적재함_너비': car.적재함_너비,
                '적재함_높이': car.적재함_높이,
                '트렁크': car.트렁크,
                '트렁크_전_용량': car.트렁크_전_용량,
                '트렁크_후_용량': car.트렁크_후_용량,

                # 기타 장비 및 부가 기능
                '에어컨': car.에어컨,
                '엔진시동': car.엔진시동,
                '와이퍼': car.와이퍼,
                '파워_아웃렛': car.파워_아웃렛,
                '온도조절_범위': car.온도조절_범위,
                '루프': car.루프,
                '주차_브레이크': car.주차_브레이크,
                '부가기능': car.부가기능,
            }

            return JsonResponse({'specs': specs})

        except Car.DoesNotExist:
            return JsonResponse({'error': 'Car not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def price(request):
    return render(request, 'price.html')

from django.http import JsonResponse
from .models import Oil

def getOil(request):
    try:
        # 최신 데이터의 휘발유와 경유 값을 가져오기
        latest_oil = Oil.objects.latest('id')
        print(f"아이디: {latest_oil.id}")  # 디버깅: 최신 Oil ID 확인
        print(f"휘발유: {latest_oil.휘발유}")  # 디버깅: 휘발유 가격 확인
        print(f"경유: {latest_oil.경유}")

        oil_prices = {
            'gasoline': latest_oil.휘발유,
            'diesel': latest_oil.경유
        }
    except Oil.DoesNotExist:
        # Oil 테이블에 데이터가 없을 경우 기본값 0 반환
        oil_prices = {
            'gasoline': 0,
            'diesel': 0
        }

    return JsonResponse(oil_prices)

def getCity(request):
    provinces_and_cities = Subsidy.objects.values('도', '시').distinct()
    return JsonResponse({'provinces_and_cities': list(provinces_and_cities)})


def getSubsidy(request):
    보조금_id = request.GET.get('car_id')
    도 = request.GET.get('do')
    시 = request.GET.get('city')

    # 보조금 ID를 이용해 EVCar 정보를 찾습니다.
    ev_car = EVCar.objects.filter(id=보조금_id).first()

    if not ev_car:
        return JsonResponse({"error": "보조금 정보가 없습니다."}, status=404)

    # 도와 시에 따른 보조금 정보 조회
    subsidy = Subsidy.objects.filter(
        도=도, 시=시, 차종=ev_car.차종,
        제조사=ev_car.제조사, 모델명=ev_car.모델명
    ).values('국가보조금', '지자체보조금').first()

    if not subsidy:
        return JsonResponse({"error": "보조금 정보가 없습니다."}, status=404)

    return JsonResponse({
        "국가보조금": subsidy['국가보조금'],
        "지자체보조금": subsidy['지자체보조금']
    })

def checkEV(request):
    car_id = request.GET.get('car_id')
    car = Car.objects.filter(id=car_id, 보조금_id__isnull=False).first()

    if car:
        return JsonResponse({"is_electric": True})
    return JsonResponse({"is_electric": False})

def evFilter(type, brand, price, city, discount_price_min, discount_price_max):
    # 차종 조건 설정
    차종_조건 = {
        '경차': ['경차', '소형'],
        '세단': ['준중형', '중형', '대형', '준대형'],
        'SUV': ['소형SUV', '중형SUV', '대형SUV'],
        'none': []
    }
    차종_조건_리스트 = 차종_조건.get(type, [])

    # 브랜드 조건 설정
    국산_브랜드 = ['현대', '기아', '제네시스', '쉐보레', 'KGM', '르노코리아']
    브랜드_조건 = 국산_브랜드 if brand == 'k' else None

    # SQL 쿼리 생성
    query = """
        SELECT COUNT(*)
        FROM car
        LEFT JOIN ev_car ON car.보조금_id = ev_car.id
        LEFT JOIN subsidy ON ev_car.모델명 = subsidy.모델명 AND subsidy.시 = %s
        WHERE car.연료 = '전기(배터리)'
        AND car.차종 IN %s
    """

    if 차종_조건_리스트:  # 차종 조건이 있을 경우에만 추가
        query += " AND car.차종 IN %s"

    # 브랜드 조건 추가
    if 브랜드_조건:
        query += " AND car.브랜드 IN %s"

    # 할인된 가격 조건 추가
    query += " AND (car.가격 - COALESCE(subsidy.국가보조금, 0) * 10000 - COALESCE(subsidy.지자체보조금, 0) * 10000) BETWEEN %s AND %s"

    print(
        f"디버그 - 입력값: type={type}, brand={brand}, price={price}, city={city}, discount_price_min={discount_price_min}, discount_price_max={discount_price_max}")
    print(f"디버그 - 차종_조건_리스트: {차종_조건_리스트}")
    print(f"디버그 - 브랜드_조건: {브랜드_조건}")

    params = [city]
    if 차종_조건_리스트:
        params.append(tuple(차종_조건_리스트))
    if 브랜드_조건:
        params.append(tuple(브랜드_조건))
    params.extend([discount_price_min, discount_price_max])

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        result = cursor.fetchone()

    return result[0] > 0


def evFilter_check(request):
    type = request.GET.get('type')
    brand = request.GET.get('brand')
    price = request.GET.get('price')
    city = request.GET.get('city')

    # 가격 조건 설정
    가격_범위 = {
        '1': (0, 20000000),
        '2': (0, 30000000),
        '3': (0, 40000000),
        '4': (0, 50000000),
        '5': (0, 60000000),
        '6': (60000000, 1000000000)
    }

    최소_가격, 최대_가격 = 가격_범위.get(price, (0, float('inf')))

    # 디버깅: 가격 범위 출력
    print(f"디버그 - 선택된 가격 범위: 최소_가격={최소_가격}, 최대_가격={최대_가격}")

    # evFilter 함수 호출
    has_ev = evFilter(type, brand, price, city, 최소_가격, 최대_가격)

    return JsonResponse({'has_ev': has_ev})

def evPage(request):
    type = request.GET.get('type')
    brand = request.GET.get('brand')
    price = request.GET.get('price')
    years = request.GET.get('years')
    km = request.GET.get('km')
    distance = request.GET.get('distance')
    city = request.GET.get('city')

    차종_조건 = {
        '경차': ['경차', '소형'],
        '세단': ['준중형', '중형', '대형', '준대형'],
        'SUV': ['소형SUV', '중형SUV', '대형SUV'],
        'none': None
    }
    차종_조건_리스트 = 차종_조건.get(type, None)

    국산_브랜드 = ['현대', '기아', '제네시스', '쉐보레', 'KGM', '르노코리아', '대창모터스', '자일자동차', '제이스모빌리티', '디피코', '쎄보모빌리티', '마이브', 'EVKMC', 'SMART EV', '이비온', '모빌리티네트웍스']
    브랜드_조건 = 국산_브랜드 if brand == 'k' else None

    가격_범위 = {
        '1': (0, 20000000),
        '2': (0, 30000000),
        '3': (0, 40000000),
        '4': (0, 50000000),
        '5': (0, 60000000),
        '6': (60000000, 1000000000)
    }
    최소_가격, 최대_가격 = 가격_범위[price]
    print(f"선택된 가격 범위: 최소_가격={최소_가격}, 최대_가격={최대_가격}")

    query = """
        SELECT 
            car.브랜드,
            car.모델명,
            car.세부모델명,
            car.차종,
            car.가격,
            subsidy.국가보조금,
            subsidy.지자체보조금,
            car.배터리_용량,
            car.복합전비,
            car.복합_주행거리,
            car.배터리_제조사,
            car.사진,
            car.id
        FROM 
            car
        LEFT JOIN 
            ev_car ON car.보조금_id = ev_car.id
        LEFT JOIN 
            subsidy ON ev_car.모델명 = subsidy.모델명 AND subsidy.시 = %s
        WHERE 
            car.연료 = '전기(배터리)' 
    """

    params = [city]
    if 차종_조건_리스트:
        query += " AND car.차종 IN %s"
        params.append(tuple(차종_조건_리스트))

    if 브랜드_조건:
        query += " AND car.브랜드 IN %s"
        params.append(tuple(브랜드_조건))

    query += " AND (car.가격 - COALESCE(subsidy.국가보조금, 0) * 10000 - COALESCE(subsidy.지자체보조금, 0) * 10000) BETWEEN %s AND %s"
    params.extend([최소_가격, 최대_가격])

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    print(rows)

    results = []
    for row in rows:
        국가보조금 = float(row[5] * Decimal(10000)) if row[5] is not None else 0
        지자체보조금 = float(row[6] * Decimal(10000)) if row[6] is not None else 0
        할인된_가격 = float(row[4]) - (국가보조금 + 지자체보조금) if row[4] is not None else 0

        if 할인된_가격 and 최소_가격 <= 할인된_가격 < 최대_가격:
            주행거리_숫자 = re.findall(r'\d+', row[9])[0] if row[9] is not None else '0'
            주행거리 = int(주행거리_숫자)
            왕복거리 = int(distance) * 2 / 1000
            한달_평일_주행거리 = 왕복거리 * 20
            충전주기 = 한달_평일_주행거리 / 주행거리 if 주행거리 > 0 else 0
            충전주기_일 = 20 / 충전주기 if 충전주기 > 0 else None

            배터리용량 = float(re.findall(r'\d+\.?\d*', row[7])[0]) if row[7] is not None else 0
            복합전비 = float(row[8]) if row[8] is not None else 0

            scores = {
                '가격': max(0, 100 - (할인된_가격 / 1000000)),
                '보조금 총액': min(100, ((국가보조금 + 지자체보조금) / 15000000) * 100),
                '배터리용량': min(100, (배터리용량 / 100) * 100),
                '복합 전비': min(100, (복합전비 / 6) * 100),
                '주행거리': min(100, (int(주행거리) / 600) * 100),
                '충전주기': min(100, 100 / (충전주기 if 충전주기 else 1))
            }

            # 점수 정규화 및 차트 데이터 준비
            normalized_scores = {k: v / 100 for k, v in scores.items()}
            values = list(normalized_scores.values()) + [list(normalized_scores.values())[0]]
            angles = np.linspace(0, 2 * np.pi, len(scores), endpoint=False).tolist() + [0]

            # 점수 총합을 계산하여 평균 표시
            average_score = sum(scores.values()) / len(scores)

            # 레이더 차트 생성
            fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True), facecolor='white')

            ax.set_ylim(0, 100)

            ax.fill(angles, [v * 100 for v in values], color='#1f77b4', alpha=0.3)
            ax.plot(angles, [v * 100 for v in values], color='#1f77b4', linewidth=2, marker='o', markersize=5)
            for angle, value, score_key in zip(angles, values, scores.keys()):
                ax.annotate(f'{scores[score_key]:.1f}',
                            xy=(angle, value * 100),
                            xytext=(5, 7),  # 텍스트 위치 조정
                            textcoords='offset points',
                            fontsize=10,
                            ha='center',
                            va='center',
                            color='navy')
            ax.grid(color='gray', linestyle='--', linewidth=0.5)
            ax.spines['polar'].set_visible(False)

            ax.set_xticklabels(scores.keys(), fontproperties=font_prop, fontsize=10)
            ax.set_yticklabels(['20', '40', '60', '80', '100'], fontproperties=font_prop, fontsize=8, color='gray')
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(scores.keys(), fontsize=10, color='navy')

            ax.text(0.5, 0.5, f'{average_score:.1f}', transform=ax.transAxes,
                    ha='center', va='center', fontsize=15, color='navy', fontweight='bold')

            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight')
            buffer.seek(0)
            graph_img = base64.b64encode(buffer.read()).decode('utf-8')
            buffer.close()
            plt.close(fig)

            results.append({
                'id': row[12],
                '브랜드': row[0],
                '모델명': row[1],
                '세부모델명': row[2] if row[2] is not None else '',
                '차종': row[3],
                '가격': f"{int(row[4]):,}원" if row[4] is not None else '',
                '국가보조금': f"{int(국가보조금):,}원" if 국가보조금 != 0 else '',
                '지자체보조금': f"{int(지자체보조금):,}원" if 지자체보조금 != 0 else '',
                '할인된_가격': f"{int(할인된_가격):,}원" if 할인된_가격 != 0 else '',
                '배터리용량': 배터리용량,
                '복합전비': row[8] if row[8] is not None else '',
                '주행거리': row[9] if row[9] is not None else '',
                '배터리제조사': row[10] if row[10] is not None else '',
                '사진': row[11],
                '충전주기': f"{충전주기_일:.1f}일" if 충전주기_일 else '데이터 부족',
                'graph_img': graph_img,
                'score': f"{average_score:.2f}"
            })

    filtered_results = {}
    for result in results:
        model_name = result['모델명']
        if model_name not in filtered_results or float(result['score']) > float(filtered_results[model_name]['score']):
            filtered_results[model_name] = result

    # 가장 점수가 높은 모델만 리스트로 변환
    top_results = list(filtered_results.values())
    top_results_sorted = sorted(top_results, key=lambda x: float(x['score']), reverse=True)

    # 상위 5개 결과만 context에 포함
    top_5_results = top_results_sorted[:5]

    context = {
        'type': type,
        'brand': brand,
        'price': price,
        'years': years,
        'km': km,
        'distance': distance,
        'city': city,
        'results': top_5_results,
    }

    return render(request, 'result_ev.html', context)

def hybridPage(request):
    type = request.GET.get('type')
    brand = request.GET.get('brand')
    price = request.GET.get('price')

    차종_조건 = {
        '경차': ['경차', '소형'],
        '세단': ['준중형', '중형', '대형', '준대형'],
        'SUV': ['소형SUV', '중형SUV', '대형SUV']
    }
    차종_조건_리스트 = 차종_조건.get(type, [])

    국산_브랜드 = ['현대', '기아', '제네시스', '쉐보레', 'KGM', '르노코리아']
    브랜드_조건 = 국산_브랜드 if brand == 'k' else None

    가격_범위 = {
        '1': (0, 20000000),
        '2': (20000000, 30000000),
        '3': (30000000, 40000000),
        '4': (40000000, 50000000),
        '5': (50000000, 60000000),
        '6': (60000000, 1000000000)
    }
    최소_가격, 최대_가격 = 가격_범위.get(price, (0, float('inf')))

    query_hybrid = """
        SELECT 
            car.브랜드,
            car.모델명,
            car.세부모델명,
            car.차종,
            car.가격,
            car.복합연비,
            car.사진,
            car.id
        FROM 
            car
        WHERE 
            car.연료 = '가솔린+전기'
            AND car.차종 IN %s
            AND car.가격 BETWEEN %s AND %s
    """

    if 브랜드_조건:
        query_hybrid += " AND car.브랜드 IN %s"

    with connection.cursor() as cursor:
        if 브랜드_조건:
            cursor.execute(query_hybrid, [tuple(차종_조건_리스트), 최소_가격, 최대_가격, tuple(브랜드_조건)])
        else:
            cursor.execute(query_hybrid, [tuple(차종_조건_리스트), 최소_가격, 최대_가격])

        rows = cursor.fetchall()

    results = []
    for row in rows:
        가격 = int(row[4]) if row[4] is not None else 0
        복합연비 = float(row[5]) if row[5] is not None else 0

        score_가격 = max(0, 100 - (가격 / 1000000))
        score_복합연비 = min(100, (복합연비 / 20) * 100)
        total_score = (score_가격 + score_복합연비) / 2

        results.append({
            'id': row[7],
            '브랜드': row[0],
            '모델명': row[1],
            '세부모델명': row[2] if row[2] is not None else '',
            '차종': row[3],
            '가격': f"{가격:,}원" if 가격 else '',
            '복합연비': f"{복합연비:.2f} km/L" if 복합연비 != 0 else '',
            '사진': row[6],
            'score': f"{total_score:.2f}"
        })

    results_sorted = sorted(results, key=lambda x: float(x['score']), reverse=True)
    top_5_results = results_sorted[:5]

    context = {
        'type': type,
        'brand': brand,
        'price': price,
        'results': top_5_results,
    }

    return render(request, 'result_hybrid.html', context)

def getSub(id, city):
    car = get_object_or_404(Car, id=id)

    ev_car = get_object_or_404(EVCar, id=car.보조금_id)
    name = ev_car.모델명
    subsidy = get_object_or_404(Subsidy, 모델명=name, 시=city)
    nation_sub = subsidy.국가보조금 * 10000
    city_sub = subsidy.지자체보조금 * 10000

    return nation_sub, city_sub

def getCarSpec(id):
    car = get_object_or_404(Car, id=id)

    car_spec = {
        '브랜드': car.브랜드,
        '모델명': car.모델명,
        '세부모델명': car.세부모델명,
        '차종': car.차종,
        '트림명': car.트림명,
        '가격': car.가격,
        '전장': car.전장,
        '전폭': car.전폭,
        '전고': car.전고,
        '축거': car.축거,
        '윤거_전': car.윤거_전,
        '윤거_후': car.윤거_후,
        '오버행_전': car.오버행_전,
        '오버행_후': car.오버행_후,
        '차음_유리': car.차음_유리,
        '자외선_차단유리': car.자외선_차단유리,
        '엔진형식': car.엔진형식,
        '배기량': car.배기량,
        '최고출력': car.최고출력,
        '최대토크': car.최대토크,
        '최고속도': car.최고속도,
        '제로백': car.제로백,
        '친환경': car.친환경,
        '연료': car.연료,
        '연료탱크': car.연료탱크,
        'CO2_배출': car.CO2_배출,
        '배터리_용량': car.배터리_용량,
        '배터리_전압': car.배터리_전압,
        '배터리_제조사': car.배터리_제조사,
        '배터리_종류': car.배터리_종류,
        '충전방식_급속': car.충전방식_급속,
        '충전방식_완속': car.충전방식_완속,
        '충전시간_급속': car.충전시간_급속,
        '충전시간_완속': car.충전시간_완속,
        '에너지소비효율': car.에너지소비효율,
        '복합연비': car.복합연비,
        '고속연비': car.고속연비,
        '도심연비': car.도심연비,
        '복합전비': car.복합전비,
        '고속전비': car.고속전비,
        '도심전비': car.도심전비,
        '복합_주행거리': car.복합_주행거리,
        '고속_주행거리': car.고속_주행거리,
        '도심_주행거리': car.도심_주행거리,
        '정속주행': car.정속주행,
        '변속기': car.변속기,
        '굴림방식': car.굴림방식,
        '브레이크_전': car.브레이크_전,
        '브레이크_후': car.브레이크_후,
        '서스펜션_전': car.서스펜션_전,
        '서스펜션_후': car.서스펜션_후,
        '타이어_전': car.타이어_전,
        '타이어_후': car.타이어_후,
        '휠_전': car.휠_전,
        '휠_후': car.휠_후,
        '주차보조': car.주차보조,
        '주행안전': car.주행안전,
        '보행자_안전': car.보행자_안전,
        '공회전_제한장치': car.공회전_제한장치,
        '에어백': car.에어백,
        '도어포켓_라이트': car.도어포켓_라이트,
        '엠비언트_라이트': car.엠비언트_라이트,
        '룸미러': car.룸미러,
        '헤드램프': car.헤드램프,
        '헤드램프_부가기능': car.헤드램프_부가기능,
        '주간_주행등': car.주간_주행등,
        '리어_램프': car.리어_램프,
        '전방_안개등': car.전방_안개등,
        '아웃_사이드미러': car.아웃_사이드미러,
        '주요기능': car.주요기능,
        '승차정원': car.승차정원,
        '시트배열': car.시트배열,
        '시트재질': car.시트재질,
        '동승석': car.동승석,
        '운전석': car.운전석,
        '뒷좌석_송풍구': car.뒷좌석_송풍구,
        '뒷좌석_측면커튼': car.뒷좌석_측면커튼,
        '뒷좌석_후면커튼': car.뒷좌석_후면커튼,
        '계기판': car.계기판,
        '스티어링_휠': car.스티어링_휠,
        '화면크기': car.화면크기,
        '사운드시스템': car.사운드시스템,
        '스피커': car.스피커,
        '적재량': car.적재량,
        '적재함_길이': car.적재함_길이,
        '적재함_너비': car.적재함_너비,
        '적재함_높이': car.적재함_높이,
        '트렁크': car.트렁크,
        '트렁크_전_용량': car.트렁크_전_용량,
        '트렁크_후_용량': car.트렁크_후_용량,
        '에어컨': car.에어컨,
        '엔진시동': car.엔진시동,
        '와이퍼': car.와이퍼,
        '파워_아웃렛': car.파워_아웃렛,
        '온도조절_범위': car.온도조절_범위,
        '루프': car.루프,
        '주차_브레이크': car.주차_브레이크,
        '부가기능': car.부가기능,
        '사진': car.사진,
    }

    return car_spec

def ev_car_fee(years):
    discount_rates = [0, 0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
    years = int(years)
    car_fee_list = []

    for year in range(1, years + 1):
        # 12년 이상일 경우 최대 경감율 50% 적용
        discount = discount_rates[-1] if year >= 12 else discount_rates[year - 1]

        # 각 연도별 경감된 가격 계산
        car_fee = 130000 * (1 - discount)
        car_fee_list.append(car_fee)

    total_fee = sum(car_fee_list)

    return car_fee_list, total_fee


def car_fee(cc, years):
    # 배기량 기준별 요율 설정 (괄호 안 비영업용 금액 사용)
    rates = [
        (1000, 104),
        (1600, 182),
        (2000, 260),
        (2500, 260),
        (float('inf'), 260)
    ]

    # 경감율 설정 (연도별 할인율)
    discount_rates = [0, 0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
    years = int(years)
    cc = float(cc)

    # 해당 배기량에 맞는 요율 찾기
    rate = next(rate for limit, rate in rates if cc <= limit)

    car_fee_list = []

    for year in range(1, years + 1):
        # 연도별 경감율 적용
        discount_rate = discount_rates[min(year - 1, len(discount_rates) - 1)]
        annual_fee = round(rate * cc * (1 - discount_rate))
        car_fee_list.append(annual_fee)

    total_fee = sum(car_fee_list)

    return car_fee_list, total_fee

def getGid(ev_type):
    # 차종별 일반차 ID 매핑
    mappings = {
        '경차': [5171, 2320, 3026],
        '소형': [5171, 2320, 3026],
        '준중형': [4194, 5185, 3101],
        '중형': [4194, 5185, 3101],
        '준대형': [3874, 4884, 4977],
        '대형': [3234, 3748],
        '소형SUV': [4460, 2459, 2760],
        '중형SUV': [2899, 3782, 4707],
        '대형SUV': [2899, 3782, 4707]
    }

    # 해당 차종에 맞는 일반차 ID 리스트 반환
    return mappings.get(ev_type, [])

def getOilPrice(km, l):
    oil = Oil.objects.latest('id')

    gas = float(oil.휘발유)

    fee = round((float(km)/float(l))*gas)

    return fee


def ev_result(request):
    id = request.GET.get('id')
    years = request.GET.get('years')
    km = float(request.GET.get('km'))
    distance = request.GET.get('distance')
    city = request.GET.get('city')

    # 전기차 보조금
    nation_sub, city_sub = getSub(id, city)

    # 전기차 스펙
    ev_car_spec = getCarSpec(id)

    # 전기차 보조금 뺀 가격
    price = ev_car_spec['가격'] - (nation_sub + city_sub)

    # 전기차 충전 요금
    charging_fee = round((km/float(ev_car_spec['복합전비']))*347.2)

    # 전기차 자동차세
    car_fee_list, total_car_fee = ev_car_fee(years)

    ev_fee, total_ev_fee = ev_car_fee(10)

    ev_year_fee = []
    ev_total_fee = int(price)
    for year in range(1, 11):
        ev_total_fee += charging_fee
        ev_total_fee += int(ev_fee[year-1])
        ev_year_fee.append(ev_total_fee)

    print(ev_year_fee)

    # 차종별 비교 차량 id 가져오기
    gid =  getGid(ev_car_spec['차종'])

    car1 = getCarSpec(gid[0])
    car1_fee_list, car1_total_fee = car_fee(car1['배기량'], years)
    car2 = getCarSpec(gid[1])
    car2_fee_list, car2_total_fee = car_fee(car2['배기량'], years)
    car3 = getCarSpec(gid[2])
    car3_fee_list, car3_total_fee = car_fee(car3['배기량'], years)

    car1_oil_fee = getOilPrice(km, car1['복합연비'])
    car2_oil_fee = getOilPrice(km, car2['복합연비'])
    car3_oil_fee = getOilPrice(km, car3['복합연비'])

    g1_fee, total_g1_fee = car_fee(car1['배기량'], 10)
    g2_fee, total_g2_fee = car_fee(car2['배기량'], 10)
    g3_fee, total_g3_fee = car_fee(car3['배기량'], 10)

    g1_year_fee = []
    g1_total_fee = int(car1['가격'])

    g2_year_fee = []
    g2_total_fee = int(car2['가격'])

    g3_year_fee = []
    g3_total_fee = int(car3['가격'])
    for year in range(1, 11):
        g1_total_fee += car1_oil_fee
        g1_total_fee += g1_fee[year-1]
        g2_total_fee += car2_oil_fee
        g2_total_fee += g2_fee[year-1]
        g3_total_fee += car3_oil_fee
        g3_total_fee += g3_fee[year-1]

        g1_year_fee.append(g1_total_fee)
        g2_year_fee.append(g2_total_fee)
        g3_year_fee.append(g3_total_fee)

    print(g1_year_fee)

    def generate_graph_image(ev_data, g_data, title):
        fig, ax = plt.subplots()
        ax.plot(range(1, 11), ev_data, label=f"{ev_car_spec['모델명']}", marker='o')
        ax.plot(range(1, 11), g_data, label="내연기관차", marker='o')
        ax.set_xlabel('연도', fontproperties=font_prop)
        ax.set_ylabel('총 가격 (만원)', fontproperties=font_prop)
        ax.set_title(title, fontproperties=font_prop)
        ax.legend(prop=font_prop)

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        graph_img = base64.b64encode(image_png).decode('utf-8')
        buffer.close()
        plt.close(fig)

        return graph_img

    # 그래프 생성 및 context에 추가
    ev_vs_g1_img = generate_graph_image(ev_year_fee, g1_year_fee, f"{ev_car_spec['브랜드']} {ev_car_spec['모델명']} vs {car1['브랜드']} {car1['모델명']}")
    ev_vs_g2_img = generate_graph_image(ev_year_fee, g2_year_fee, f"{ev_car_spec['브랜드']} {ev_car_spec['모델명']} vs {car2['브랜드']} {car2['모델명']}")
    ev_vs_g3_img = generate_graph_image(ev_year_fee, g3_year_fee, f"{ev_car_spec['브랜드']} {ev_car_spec['모델명']} vs {car3['브랜드']} {car3['모델명']}")

    # 예제 사용 (10년간 가격 하락 추이 예측)
    model = train_model()
    yearly_data = predict_yearly_depreciation(2, int(years)-1, int(km), int(ev_car_spec['가격']), model)  # 예시 입력 값
    used_img = generate_yearly_depreciation_graph(yearly_data, "연도별 차량 가격 하락 추이", int(ev_car_spec['가격']))


    context = {
        'id': id,
        'years': years,
        'km': km,
        'distance': distance,
        'city': city,
        '국가보조금': nation_sub,
        '지자체보조금': city_sub,
        'ev_car_spec': ev_car_spec,
        'car1': car1,
        'car1_fee_list': car1_fee_list,
        'car1_total_fee': car1_total_fee,
        'car1_oil_fee': car1_oil_fee,
        'car2': car2,
        'car2_fee_list': car2_fee_list,
        'car2_total_fee': car2_total_fee,
        'car2_oil_fee': car2_oil_fee,
        'car3': car3,
        'car3_fee_list': car3_fee_list,
        'car3_total_fee': car3_total_fee,
        'car3_oil_fee': car3_oil_fee,
        'price': price,
        'charging_fee': charging_fee,
        'car_fee_list': car_fee_list,
        'total_car_fee': total_car_fee,
        'ev_vs_g1_img': ev_vs_g1_img,
        'ev_vs_g2_img': ev_vs_g2_img,
        'ev_vs_g3_img': ev_vs_g3_img,
        'used_img': used_img,
    }

    return render(request, 'ev_verses.html', context)


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

    # 연간 주행거리 계산
    data['연간주행거리'] = data['주행거리'] / (data['운행일'] / 365)

    X = data[['운행일', '연간주행거리', '신차가격']]
    y = data['가격']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = GradientBoostingRegressor(random_state=42)
    model.fit(X_train, y_train)
    return model


# 연도별 가격 예측 (2년 차부터 예측 시작)
def predict_yearly_depreciation(start_year, total_years, annual_mileage, new_price, model):
    yearly_prices = []
    previous_price = new_price  # 신차 가격을 첫 번째 기준값으로 설정

    for year in range(start_year, start_year + total_years):
        운행일 = year * 365
        input_data = pd.DataFrame([[운행일, annual_mileage, new_price]], columns=['운행일', '연간주행거리', '신차가격'])
        predicted_price = model.predict(input_data)[0]

        # 다음 연도의 가격 예측
        next_year_input_data = pd.DataFrame([[운행일 + 365, annual_mileage, new_price]], columns=['운행일', '연간주행거리', '신차가격'])
        next_year_predicted_price = model.predict(next_year_input_data)[0]

        # 예측 가격이 전년도보다 높을 때, 전년도와 다음 연도 값의 중간으로 조정
        if predicted_price > previous_price:
            predicted_price = (previous_price + next_year_predicted_price) / 2

        yearly_prices.append(predicted_price)
        previous_price = predicted_price  # 현재 가격을 전년도 가격으로 업데이트

    return yearly_prices


def generate_yearly_depreciation_graph(yearly_data, title, new_price):
    fig, ax = plt.subplots(figsize=(6, 4.5))  # 그래프 크기 조정
    years = range(2, len(yearly_data) + 2)

    # 가격을 천만 원 단위로 변환
    yearly_data_million = [price / 10000 for price in yearly_data]

    ax.plot(years, yearly_data_million, marker='o', color='teal', linestyle='-', linewidth=2, markersize=6)

    # 축 레이블과 제목 설정
    ax.set_xlabel('연차', fontproperties=font_prop, fontsize=12, labelpad=15)
    ax.set_ylabel('예상 가격 (만 원)', fontproperties=font_prop, fontsize=12, labelpad=15)
    ax.set_title(title, fontproperties=font_prop, fontsize=16, pad=20)

    # 그리드 추가
    ax.grid(True, linestyle='--', alpha=0.7)

    # X축과 Y축 틱 포맷팅
    ax.tick_params(axis='x', rotation=0, labelsize=10)
    ax.tick_params(axis='y', labelsize=10)

    # Y축 레이블을 천 단위로 구분
    ax.get_yaxis().get_major_formatter().set_scientific(False)
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,.0f}".format(int(x))))  # 원 단위로 표시

    for year, price in zip(years, yearly_data):
        price_original = price / 10000  # 만 원 단위로 변환
        depreciation = ((new_price - price) / new_price) * 100  # 신차 대비 감소율 계산
        # price_original 값을 int로 변환하여 문자열 포맷으로 삽입
        ax.text(year, price_original, f"{int(price_original):,} (-{depreciation:.0f}%)",
                ha='center', va='bottom', fontsize=10, fontproperties=font_prop)

    # 그래프에 경계선을 추가
    for spine in ax.spines.values():
        spine.set_edgecolor('gray')
        spine.set_linewidth(0.5)

    # 레이아웃 조정
    plt.tight_layout()  # 라벨과 제목이 잘리지 않도록 자동으로 조정

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph_img = base64.b64encode(image_png).decode('utf-8')
    buffer.close()
    plt.close(fig)

    return graph_img

def format_price(price):
    # 가격이 원 단위로 저장되어 있다고 가정합니다.
    if price >= 100_000_000:  # 1억 원 이상인 경우
        eok = price // 100_000_000  # 억 단위
        remainder = (price % 100_000_000) // 10_000  # 만원 단위
        if remainder > 0:
            remainder_formatted = "{:,}".format(remainder)
            return f"{eok}억 {remainder_formatted}"
        else:
            return f"{eok}억"
    else:
        man = price // 10_000  # 만원 단위
        man_formatted = "{:,}".format(man)
        return man_formatted

def searchPage(request):
    query = request.GET.get('query', '')
    selected_car_types = request.GET.getlist('car_type')  # 선택된 차종 리스트
    selected_brands = request.GET.getlist('brand')        # 선택된 브랜드 리스트
    selected_fuels = request.GET.getlist('fuel')          # 선택된 연료 리스트

    cars_qs = Car.objects.all()

    if query:
        cars_qs = cars_qs.filter(
            Q(브랜드__icontains=query) |
            Q(모델명__icontains=query)
        )

    if selected_car_types:
        cars_qs = cars_qs.filter(차종__in=selected_car_types)

    if selected_brands:
        cars_qs = cars_qs.filter(브랜드__in=selected_brands)

    if selected_fuels:
        cars_qs = cars_qs.filter(연료__in=selected_fuels)

    cars = cars_qs.values(
        '브랜드', '모델명', '차종', '가격', '연료', '배기량', '복합연비',
        '배터리_용량', '복합전비', '복합_주행거리', '사진'
    ).order_by('모델명')

    car_dict = defaultdict(lambda: {
        '연료': set(),
        '최저가': float('inf'),
        '최고가': float('-inf'),
        '배기량': set(),
        '배터리_용량': set(),
        '복합연비': set(),
        '복합전비': set(),
        '복합_주행거리': set(),
        '사진': None
    })

    for car in cars:
        model_name = car['모델명']
        car_dict[model_name]['브랜드'] = car['브랜드']
        car_dict[model_name]['차종'] = car['차종']
        car_dict[model_name]['연료'].add(car['연료'])
        car_dict[model_name]['사진'] = car['사진']

        # 가격 범위 업데이트
        car_dict[model_name]['최저가'] = min(car_dict[model_name]['최저가'], car['가격'])
        car_dict[model_name]['최고가'] = max(car_dict[model_name]['최고가'], car['가격'])

        # 연료 유형에 따른 데이터 처리
        if car['연료'] == "전기(배터리)":
            if car['배터리_용량']:
                value = str(car['배터리_용량']).replace(' kWh', '').replace('kWh', '').strip()
                car_dict[model_name]['배터리_용량'].add(float(value))
            if car['복합전비']:
                value = str(car['복합전비']).replace(' km/kWh', '').replace('km/kWh', '').strip()
                car_dict[model_name]['복합전비'].add(float(value))
            if car['복합_주행거리']:
                value = str(car['복합_주행거리']).replace(' km', '').replace('km', '').strip()
                car_dict[model_name]['복합_주행거리'].add(float(value))
        else:
            if car['배기량']:
                value = str(car['배기량']).replace(' cc', '').replace('cc', '').strip()
                car_dict[model_name]['배기량'].add(int(value))
            if car['복합연비']:
                value = str(car['복합연비']).replace(' km/L', '').replace('km/L', '').strip()
                car_dict[model_name]['복합연비'].add(float(value))

    processed_cars = []
    for model, data in car_dict.items():
        lowest_price = int(data['최저가'])
        highest_price = int(data['최고가'])

        # 가격 범위 포맷팅
        if lowest_price == highest_price:
            price_formatted = format_price(lowest_price)
            price_range = f"{price_formatted}만원"
        else:
            lowest_price_formatted = format_price(lowest_price)
            highest_price_formatted = format_price(highest_price)
            price_range = f"{lowest_price_formatted} ~ {highest_price_formatted}만원"

        fuel_types = ", ".join(sorted(filter(None, data['연료'])))

        # 연료 유형에 따른 데이터 처리
        if "전기(배터리)" in data['연료']:
            battery_capacity = list(data['배터리_용량'])
            efficiency_range = list(data['복합전비'])
            driving_range = list(data['복합_주행거리'])

            # 배터리 용량 포맷팅
            if battery_capacity:
                min_battery_capacity = min(battery_capacity)
                max_battery_capacity = max(battery_capacity)
                if min_battery_capacity != max_battery_capacity:
                    battery_capacity_str = f"{min_battery_capacity} ~ {max_battery_capacity} kWh"
                else:
                    battery_capacity_str = f"{min_battery_capacity} kWh"
            else:
                battery_capacity_str = "정보 없음"

            # 주행 거리 포맷팅
            if driving_range:
                min_driving_range = min(driving_range)
                max_driving_range = max(driving_range)
                if min_driving_range != max_driving_range:
                    driving_range_str = f"{min_driving_range} ~ {max_driving_range} km"
                else:
                    driving_range_str = f"{min_driving_range} km"
            else:
                driving_range_str = "정보 없음"

            # 연비 범위 포맷팅
            if efficiency_range:
                min_efficiency = min(efficiency_range)
                max_efficiency = max(efficiency_range)
                if min_efficiency != max_efficiency:
                    efficiency_range_str = f"{min_efficiency} ~ {max_efficiency} km/kWh"
                else:
                    efficiency_range_str = f"{min_efficiency} km/kWh"
            else:
                efficiency_range_str = "정보 없음"

            # 전기차 데이터 구성
            car_data = {
                '브랜드': data['브랜드'],
                '모델명': model,
                '차종': data['차종'],
                '가격범위': price_range,
                '연료': fuel_types,
                '배터리용량': battery_capacity_str,
                '주행거리범위': driving_range_str,
                '연비범위': efficiency_range_str,
                '사진': data['사진']
            }
        else:
            engine_capacity = list(data['배기량'])
            efficiency_range = list(data['복합연비'])

            # 배기량 포맷팅
            if engine_capacity:
                min_engine_capacity = min(engine_capacity)
                max_engine_capacity = max(engine_capacity)
                if min_engine_capacity != max_engine_capacity:
                    engine_capacity_str = f"{min_engine_capacity} ~ {max_engine_capacity} cc"
                else:
                    engine_capacity_str = f"{min_engine_capacity} cc"
            else:
                engine_capacity_str = "정보 없음"

            # 연비 범위 포맷팅
            if efficiency_range:
                min_efficiency = min(efficiency_range)
                max_efficiency = max(efficiency_range)
                if min_efficiency != max_efficiency:
                    efficiency_range_str = f"{min_efficiency} ~ {max_efficiency} km/L"
                else:
                    efficiency_range_str = f"{min_efficiency} km/L"
            else:
                efficiency_range_str = "정보 없음"

            # 내연기관차 데이터 구성
            car_data = {
                '브랜드': data['브랜드'],
                '모델명': model,
                '차종': data['차종'],
                '가격범위': price_range,
                '연료': fuel_types,
                '배기량': engine_capacity_str,
                '연비범위': efficiency_range_str,
                '사진': data['사진']
            }

        processed_cars.append(car_data)

    # 모든 차종 목록 생성
    all_car_types = ['경차', '소형', '준중형', '중형', '준대형', '대형', '소형SUV', '중형SUV', '대형SUV', '스포츠카', '그외']
    # 브랜드 목록 생성
    all_brands = ['현대', '기아', '제네시스', 'KGM', '르노코리아', '쉐보레', 'BMW', '벤츠', '아우디', '테슬라', '폭스바겐', '볼보', '폴스타', '포르쉐', '포드']
    # 연료 종류 목록 생성
    all_fuels = ['LPG', 'LPG+가솔린', '가솔린', '가솔린+전기', '디젤', '전기(배터리)', '전기(수소연료전지)']

    return render(request, 'search.html', {
        'cars': processed_cars,
        'query': query,
        'car_types': all_car_types,
        'selected_car_types': selected_car_types,
        'brands': all_brands,
        'selected_brands': selected_brands,
        'fuels': all_fuels,
        'selected_fuels': selected_fuels
    })

def brandsearch(request):
    brand = request.GET.get('brand', None)

    # 차량 모델 쿼리
    car_modelname = Car.objects.filter(브랜드=brand).values(
        '모델명',
        '연료',
        '복합전비',  # 전기차의 복합전비
        '복합연비',  # 내연기관 차량의 복합연비
        '사진',
    ).annotate(
        최고가격=Max('가격'),
        최저가격=Min('가격'),
    )

    # 연료 부분 합치기
    result = {}
    for car in car_modelname:
        model_name = car['모델명']
        fuel_type = car['연료']
        photo = car['사진']  # 사진 정보 가져오기

        if model_name not in result:
            result[model_name] = {
                '연료': fuel_type,
                '최고가격': car['최고가격'],
                '최저가격': car['최저가격'],
                '사진': photo,  # 사진 추가
            }
        else:
            # 이미 등록된 연료 타입인지 확인 후 합치기
            if fuel_type not in result[model_name]['연료'].split(','):
                result[model_name]['연료'] += ',' + fuel_type

    # 최종 리스트로 변환
    car_modelname_final = []
    for model_name, info in result.items():
        info['모델명'] = model_name
        car_modelname_final.append(info)

    # 가격 변환
    for car in car_modelname_final:
        car['최고가격_변환'] = car['최고가격'] // 10000 if car['최고가격'] else None
        car['최저가격_변환'] = car['최저가격'] // 10000 if car['최저가격'] else None

    context = {
        'car_modelname': car_modelname_final
    }
    return render(request, 'filter/brandsearch.html', context)

def oilsearch(request):
    brand = request.GET.get('brand', None)

    # 차량 모델 쿼리 (연료 조건 수정) - 사진 필드 포함
    car_modelname = Car.objects.filter(
        Q(연료='LPG') | Q(연료='가솔린') | Q(연료='디젤')
    ).values(
        '모델명',
        '사진',  # 사진 필드 추가
    ).annotate(
        연료=Concat(
            Value(''),
            F('연료'),
        ),
        최고가격=Max('가격'),
        최저가격=Min('가격'),
    ).distinct()

    # 연료 부분 합치기
    result = {}
    for car in car_modelname:
        model_name = car['모델명']
        fuel_type = car['연료']
        photo = car['사진']  # 사진 정보 가져오기

        if model_name not in result:
            result[model_name] = {
                '연료': fuel_type,
                '최고가격': car['최고가격'],
                '최저가격': car['최저가격'],
                '사진': photo,  # 사진 추가
            }
        else:
            if fuel_type not in result[model_name]['연료']:
                result[model_name]['연료'] += ',' + fuel_type

    # 최종 리스트로 변환
    car_modelname_final = []
    for model_name, info in result.items():
        info['모델명'] = model_name
        car_modelname_final.append(info)

    for car in car_modelname_final:
        car['최고가격_변환'] = car['최고가격'] // 10000 if car['최고가격'] else None
        car['최저가격_변환'] = car['최저가격'] // 10000 if car['최저가격'] else None

    context = {
        'car_modelname': car_modelname_final
    }
    return render(request, 'filter/oilsearch.html', context)


def evsearch(request):
    brand = request.GET.get('brand', None)

    # 차량 모델 쿼리 - 사진 필드 포함
    car_modelname = Car.objects.filter(Q(연료='전기(배터리)') | Q(연료='전기(수소연료전지)')).values(
        '모델명',
        '연료',
        '사진',  # 사진 필드 추가
    ).annotate(
        최고가격=Max('가격'),
        최저가격=Min('가격'),
    )

    for car in car_modelname:
        car['최고가격_변환'] = car['최고가격'] // 10000 if car['최고가격'] else None
        car['최저가격_변환'] = car['최저가격'] // 10000 if car['최저가격'] else None

    context = {
        'car_modelname': car_modelname
    }
    return render(request, 'filter/evsearch.html', context)


def hybridsearch(request):
    brand = request.GET.get('brand', None)

    # 차량 모델 쿼리 - 사진 필드 포함
    car_modelname = Car.objects.filter(연료='가솔린+전기').values(
        '모델명',
        '연료',
        '사진',  # 사진 필드 추가
    ).annotate(
        최고가격=Max('가격'),
        최저가격=Min('가격'),
    )

    for car in car_modelname:
        car['최고가격_변환'] = car['최고가격'] // 10000 if car['최고가격'] else None
        car['최저가격_변환'] = car['최저가격'] // 10000 if car['최저가격'] else None

    context = {
        'car_modelname': car_modelname
    }
    return render(request, 'filter/hybridsearch.html', context)


def search_allcar(request):
    search_term = request.GET.get('search', '').strip()  # 검색어를 가져옵니다

    # 차량 모델 쿼리 - 사진 필드 포함
    car_modelname = Car.objects.filter(모델명__icontains=search_term).values(
        '모델명',
        '연료',
        '복합전비',  # 전기차의 복합전비
        '복합연비',  # 내연기관 차량의 복합연비
        '사진',  # 사진 필드 추가
    ).annotate(
        최고가격=Max('가격'),
        최저가격=Min('가격'),
    )

    # 연료 부분 합치기
    result = {}
    for car in car_modelname:
        model_name = car['모델명']
        fuel_type = car['연료']
        photo = car['사진']  # 사진 정보 가져오기

        if model_name not in result:
            result[model_name] = {
                '연료': fuel_type if fuel_type is not None else '',  # None일 경우 빈 문자열로 처리
                '최고가격': car['최고가격'],
                '최저가격': car['최저가격'],
                '사진': photo,  # 사진 추가
            }
        else:
            # 이미 등록된 연료 타입인지 확인 후 합치기
            if fuel_type and fuel_type not in result[model_name]['연료'].split(','):
                result[model_name]['연료'] += ',' + fuel_type  # fuel_type이 None이 아닐 때만 추가

    # 최종 리스트로 변환
    car_modelname_final = []
    for model_name, info in result.items():
        info['모델명'] = model_name
        car_modelname_final.append(info)

    # 가격 변환
    for car in car_modelname_final:
        car['최고가격_변환'] = car['최고가격'] // 10000 if car['최고가격'] else None
        car['최저가격_변환'] = car['최저가격'] // 10000 if car['최저가격'] else None

    context = {
        'car_modelname': car_modelname_final
    }
    return render(request, 'filter/search_allcar.html', context)