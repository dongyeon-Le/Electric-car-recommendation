from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Car, Oil, EVCar, Subsidy, Apt, AptCharger, Charger
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

client_id = '4i2qbbvpg9'
client_secret = 'Nuqjv69noZ2UzMHQVa41mIFToQb8mV8uqxjKuory'

def homepage(request):
    return render(request, 'homepage.html')

def mapTest(request):
    return render(request, 'map_test.html')

allow = {
    'type': ['경차', '세단', 'SUV', 'MPV', 'none'],
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
                            # -------동연,다음단계------------
                            'send_type': type,
                            'send_brand': brand,
                            'send_price': price,
                            'send_years': years,
                            'send_km': km,
                            # --------------------------------
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

    # ----------------------------------------동연-------------------------------------


from django.db.models import Min, Max, Case, When, Value, IntegerField, OuterRef, Subquery, FloatField, F
from django.db.models.functions import Replace, Cast, Coalesce


def filterPage(request):
    send_type = request.GET.get('send_type', None)
    send_brand = request.GET.get('send_brand', None)
    send_price = request.GET.get('send_price', None)
    send_years = request.GET.get('send_years', None)
    send_km = request.GET.get('send_km', None)
    send_distance = request.GET.get('distance', None)
    print('타입=', send_type, '브랜드=', send_brand, '가격대=', send_price, '년도=', send_years, '키로수=', send_km, '거리=',
          send_distance)
    imsi = None
    cartype = send_type  # 원하는 차종
    carbrand = send_brand  # 원하는 브랜드
    carprice = int(send_price) * 1000  # 원하는 가격

    money = imsi
    distance = imsi

    price_ranges = {
        1000: (10000000, 20000000),  # 천만 이상, 이천만 미만
        2000: (20000000, 30000000),  # 이천만 이상, 삼천만 미만
        3000: (30000000, 40000000),  # 삼천만 이상, 사천만 미만
        4000: (40000000, 50000000),  # 사천만 이상, 오천만 미만
        5000: (50000000, 60000000),  # 오천만 이상, 육천만 미만
        6000: (60000000, 99999999999),  # 육천 이상
    }

    price_upranges = {
        1000: (20000000, 30000000),  # 이천만 이상, 삼천만 미만
        2000: (30000000, 40000000),  # 삼천만 이상, 사천만 미만
        3000: (40000000, 50000000),  # 사천만 이상, 오천만 미만
        4000: (50000000, 60000000),  # 오천만 이상, 육천만 미만
        5000: (60000000, 99999999999),  # 육천 이상
    }

    # 기본 쿼리셋(전기차만)
    queryset = Car.objects.all().filter(연료='전기(배터리)')
    querysetprice = Car.objects.all().filter(연료='전기(배터리)')

    # # cartype이 None이 아닐 때 필터 추가
    # if cartype:
    #     queryset = queryset.filter(차종=cartype)
    #     querysetprice = querysetprice.filter(차종=cartype)

    classifications = {
        '경차': ['경차', '소형'],  # 경차에 해당하는 모델명
        '세단': ['준중형', '중형', '준대형'],  # 세단에 해당하는 모델명
        'SUV': ['소형SUV', '중형SUV', '대형SUV'],  # SUV에 해당하는 모델명
        'MPV': ['픽업/밴', '소형버스', '소형트럭', '경트럭'],  # MPV에 해당하는 모델명
    }

    # 차종 분류
    if cartype:
        queryset = queryset.filter(차종__in=classifications[cartype])
        querysetprice = querysetprice.filter(차종__in=classifications[cartype])

    # 한국 브랜드 리스트
    korean_brands = ['기아', '제네시스', '쎄보모빌리티', '제이스모빌리티', '현대', '마이브',
                     '마스타전기차', '대창모터스', '디피코', '에스에스라이트', '이비온',
                     '모빌리티네트웍스', 'KGM', 'EVKMC']

    # carbrand가 None이 아닐 때 필터 추가
    if carbrand:
        queryset = queryset.filter(브랜드__in=korean_brands)
        querysetprice = querysetprice.filter(브랜드__in=korean_brands)

    # carprice가 None이 아닐 때 필터 추가
    if carprice:
        price_range = price_ranges.get(carprice)
        price_uprange = price_upranges.get(carprice)
        if price_range:  # 유효한 price_range가 있을 경우
            queryset = queryset.filter(가격__gte=price_range[0], 가격__lt=price_range[1])
        if price_uprange:  # 유효한 price_uprange가 있을 경우
            querysetprice = querysetprice.filter(가격__gte=price_uprange[0], 가격__lt=price_uprange[1])

    # 필터링된 모델명 가져오기
    model_names = queryset.values_list('모델명', flat=True).distinct()

    # ------------------------숫자변환로직--------------------------------------------

    # 배터리 용량을 kWh를 제거하고 FloatField로 변환하는 로직 - 가격대
    queryset = queryset.annotate(
        배터리_용량_숫자=Coalesce(
            Cast(
                Replace(F('배터리_용량'), Value(' kWh'), Value('')),  # ' kWh' 제거
                output_field=FloatField()  # FloatField로 변환
            ),
            0.0  # Null 값을 0.0으로 대체
        )
    )

    # 배터리 용량을 kWh를 제거하고 FloatField로 변환하는 로직 - 상위가격대
    querysetprice = querysetprice.annotate(
        배터리_용량_숫자=Coalesce(
            Cast(
                Replace(F('배터리_용량'), Value(' kWh'), Value('')),  # ' kWh' 제거
                output_field=FloatField()  # FloatField로 변환
            ),
            0.0  # Null 값을 0.0으로 대체
        )
    )

    # 층전시간급속 분을 제거하고 FloatField로 변환하는 로직 - 가격대
    queryset = queryset.annotate(
        충전시간_급속_숫자=Coalesce(
            Cast(
                Replace(F('충전시간_급속'), Value(' 분'), Value('')),  # ' kWh' 제거
                output_field=FloatField()  # FloatField로 변환
            ),
            0.0  # Null 값을 0.0으로 대체
        )
    )

    # 층전시간급속 분을 제거하고 FloatField로 변환하는 로직 - 상위가격대
    querysetprice = querysetprice.annotate(
        충전시간_급속_숫자=Coalesce(
            Cast(
                Replace(F('충전시간_급속'), Value(' 분'), Value('')),  # ' kWh' 제거
                output_field=FloatField()  # FloatField로 변환
            ),
            0.0  # Null 값을 0.0으로 대체
        )
    )

    # 층전시간완속 시간을 제거하고 FloatField로 변환하는 로직 - 가격대
    queryset = queryset.annotate(
        충전시간_완속_숫자=Coalesce(
            Cast(
                Replace(F('충전시간_완속'), Value(' 시간'), Value('')),  # ' kWh' 제거
                output_field=FloatField()  # FloatField로 변환
            ),
            0.0  # Null 값을 0.0으로 대체
        )
    )

    # 층전시간완속 시간을 제거하고 FloatField로 변환하는 로직 - 상위가격대
    querysetprice = querysetprice.annotate(
        충전시간_완속_숫자=Coalesce(
            Cast(
                Replace(F('충전시간_완속'), Value(' 시간'), Value('')),  # ' kWh' 제거
                output_field=FloatField()  # FloatField로 변환
            ),
            0.0  # Null 값을 0.0으로 대체
        )
    )

    # 복합주행거리 km를 제거하고 FloatField로 변환하는 로직 - 가격대
    queryset = queryset.annotate(
        복합주행거리_숫자=Coalesce(
            Cast(
                Replace(F('복합_주행거리'), Value(' km'), Value('')),  # ' kWh' 제거
                output_field=FloatField()  # FloatField로 변환
            ),
            0.0  # Null 값을 0.0으로 대체
        )
    )

    # 복합주행거리 km를 제거하고 FloatField로 변환하는 로직 - 상위가격대
    querysetprice = querysetprice.annotate(
        복합주행거리_숫자=Coalesce(
            Cast(
                Replace(F('복합_주행거리'), Value(' km'), Value('')),  # ' kWh' 제거
                output_field=FloatField()  # FloatField로 변환
            ),
            0.0  # Null 값을 0.0으로 대체
        )
    )

    queryset = queryset.annotate(
        가격_퍼센트=Coalesce(
            (F('가격') / (carprice * 10000)) * 100.0,  # 가격을 기준 가격으로 나누고 100을 곱하여 퍼센트로 변환
            0.0,  # Null 값은 0.0으로 대체
            output_field=FloatField()  # 결과 필드 타입을 FloatField로 명시
        )
    )

    # ------------------------숫자변환로직--------------------------------------------

    # 총점수 - 가격대
    queryset = queryset.annotate(
        가격_점수=Case(
            When(가격_퍼센트__lte=120.0, then=Value(100)),  # 20 이하
            When(가격_퍼센트__gt=120.0, 가격_퍼센트__lte=140.0, then=Value(80)),  # 20 ~ 40
            When(가격_퍼센트__gt=140.0, 가격_퍼센트__lte=160.0, then=Value(60)),  # 40 ~ 60
            When(가격_퍼센트__gt=160.0, 가격_퍼센트__lte=180.0, then=Value(40)),  # 60 ~ 80
            When(가격_퍼센트__gt=180.0, 가격_퍼센트__lte=200.0, then=Value(20)),  # 80 ~ 100
            When(가격_퍼센트__gt=200.0, then=Value(0)),  # 100 초과
            default=Value(0),  # 기본값
            output_field=IntegerField(),
        ),
        배터리용량_점수=Case(
            When(배터리_용량_숫자__lte=30.0, then=Value(10)),  # 30 이하
            When(배터리_용량_숫자__gt=30.0, 배터리_용량_숫자__lte=50.0, then=Value(30)),  # 30 ~ 50
            When(배터리_용량_숫자__gt=50.0, 배터리_용량_숫자__lte=70.0, then=Value(50)),  # 50 ~ 70
            When(배터리_용량_숫자__gt=70.0, 배터리_용량_숫자__lte=90.0, then=Value(70)),  # 70 ~ 90
            When(배터리_용량_숫자__gt=90.0, 배터리_용량_숫자__lte=110.0, then=Value(90)),  # 90 ~ 110
            When(배터리_용량_숫자__gt=110.0, then=Value(100)),  # 110 이상
            default=Value(0),
            output_field=IntegerField(),
        ),
        충전시간_급속_점수=Case(
            When(충전시간_급속_숫자__lte=20.0, then=Value(10)),  # 20분 이하
            When(충전시간_급속_숫자__gt=20.0, 충전시간_급속_숫자__lte=30.0, then=Value(20)),  # 20 ~ 30분
            When(충전시간_급속_숫자__gt=30.0, 충전시간_급속_숫자__lte=40.0, then=Value(30)),  # 30 ~ 40분
            When(충전시간_급속_숫자__gt=40.0, 충전시간_급속_숫자__lte=50.0, then=Value(40)),  # 40 ~ 50분
            When(충전시간_급속_숫자__gt=50.0, 충전시간_급속_숫자__lte=60.0, then=Value(50)),  # 50 ~ 60분
            When(충전시간_급속_숫자__gt=60.0, 충전시간_급속_숫자__lte=70.0, then=Value(60)),  # 60 ~ 70분
            When(충전시간_급속_숫자__gt=70.0, then=Value(70)),  # 70분 이상
            default=Value(0),
            output_field=IntegerField(),
        ),
        충전시간_완속_점수=Case(
            When(충전시간_완속_숫자__lte=4.0, then=Value(20)),  # 0~4시간: 20점
            When(충전시간_완속_숫자__gt=4.0, 충전시간_완속_숫자__lte=6.0, then=Value(40)),  # 4~6시간: 40점
            When(충전시간_완속_숫자__gt=6.0, 충전시간_완속_숫자__lte=8.0, then=Value(60)),  # 6~8시간: 60점
            When(충전시간_완속_숫자__gt=8.0, 충전시간_완속_숫자__lte=10.0, then=Value(80)),  # 8~10시간: 80점
            When(충전시간_완속_숫자__gt=10.0, 충전시간_완속_숫자__lte=12.0, then=Value(90)),  # 10~12시간: 90점
            When(충전시간_완속_숫자__gt=12.0, then=Value(100)),  # 12시간 이상: 100점
            default=Value(0),
            output_field=IntegerField(),
        ),
        복합전비_점수=Case(
            When(복합전비__lte=2.6, then=Value(0)),  # 0~2.6시간: 0점
            When(복합전비__gt=2.6, 복합전비__lte=4.0, then=Value(20)),  # 2.6~4.0시간: 20점
            When(복합전비__gt=4.0, 복합전비__lte=5.0, then=Value(40)),  # 4.0~5.0시간: 40점
            When(복합전비__gt=5.0, 복합전비__lte=5.5, then=Value(60)),  # 5.0~5.5시간: 60점
            When(복합전비__gt=5.5, 복합전비__lte=6.0, then=Value(80)),  # 5.5~6.0시간: 80점
            When(복합전비__gt=6.0, 복합전비__lte=6.3, then=Value(90)),  # 6.0~6.3시간: 90점
            When(복합전비__gt=6.3, then=Value(100)),  # 6.3시간 이상: 100점
            default=Value(0),
            output_field=IntegerField(),
        ),
        복합주행거리_점수=Case(
            When(복합주행거리_숫자__lt=70.0, then=Value(0)),  # 0~69.9 km: 0점
            When(복합주행거리_숫자__gte=70.0, 복합주행거리_숫자__lt=150.0, then=Value(20)),  # 70.0~149.9 km: 20점
            When(복합주행거리_숫자__gte=150.0, 복합주행거리_숫자__lt=250.0, then=Value(40)),  # 150.0~249.9 km: 40점
            When(복합주행거리_숫자__gte=250.0, 복합주행거리_숫자__lt=350.0, then=Value(60)),  # 250.0~349.9 km: 60점
            When(복합주행거리_숫자__gte=350.0, 복합주행거리_숫자__lt=450.0, then=Value(80)),  # 350.0~449.9 km: 80점
            When(복합주행거리_숫자__gte=450.0, 복합주행거리_숫자__lt=500.0, then=Value(90)),  # 450.0~499.9 km: 90점
            When(복합주행거리_숫자__gte=500.0, then=Value(100)),  # 500.0 km 이상: 100점
            default=Value(0),
            output_field=IntegerField(),
        ),
    ).annotate(
        score=F('가격_점수') * Value(0.2) +
              F('배터리용량_점수') * Value(0.3) +
              F('충전시간_급속_점수') * Value(0.075) +
              F('충전시간_완속_점수') * Value(0.075) +
              F('복합전비_점수') * Value(0.1) +
              F('복합주행거리_점수') * Value(0.25)  # 배터리 점수와 충전 시간 점수 합산 # 배터리 점수와 충전 시간 점수 합산
    )

    # 총점수 - 가격대
    querysetprice = querysetprice.annotate(
        배터리용량_점수=Case(
            When(배터리_용량_숫자__lte=30.0, then=Value(10)),  # 30 이하
            When(배터리_용량_숫자__gt=30.0, 배터리_용량_숫자__lte=50.0, then=Value(30)),  # 30 ~ 50
            When(배터리_용량_숫자__gt=50.0, 배터리_용량_숫자__lte=70.0, then=Value(50)),  # 50 ~ 70
            When(배터리_용량_숫자__gt=70.0, 배터리_용량_숫자__lte=90.0, then=Value(70)),  # 70 ~ 90
            When(배터리_용량_숫자__gt=90.0, 배터리_용량_숫자__lte=110.0, then=Value(90)),  # 90 ~ 110
            When(배터리_용량_숫자__gt=110.0, then=Value(100)),  # 110 이상
            default=Value(0),
            output_field=IntegerField(),
        ),
        충전시간_급속_점수=Case(
            When(충전시간_급속_숫자__lte=20.0, then=Value(10)),  # 20분 이하
            When(충전시간_급속_숫자__gt=20.0, 충전시간_급속_숫자__lte=30.0, then=Value(20)),  # 20 ~ 30분
            When(충전시간_급속_숫자__gt=30.0, 충전시간_급속_숫자__lte=40.0, then=Value(30)),  # 30 ~ 40분
            When(충전시간_급속_숫자__gt=40.0, 충전시간_급속_숫자__lte=50.0, then=Value(40)),  # 40 ~ 50분
            When(충전시간_급속_숫자__gt=50.0, 충전시간_급속_숫자__lte=60.0, then=Value(50)),  # 50 ~ 60분
            When(충전시간_급속_숫자__gt=60.0, 충전시간_급속_숫자__lte=70.0, then=Value(60)),  # 60 ~ 70분
            When(충전시간_급속_숫자__gt=70.0, then=Value(70)),  # 70분 이상
            default=Value(0),
            output_field=IntegerField(),
        ),
        충전시간_완속_점수=Case(
            When(충전시간_완속_숫자__lte=4.0, then=Value(20)),  # 0~4시간: 20점
            When(충전시간_완속_숫자__gt=4.0, 충전시간_완속_숫자__lte=6.0, then=Value(40)),  # 4~6시간: 40점
            When(충전시간_완속_숫자__gt=6.0, 충전시간_완속_숫자__lte=8.0, then=Value(60)),  # 6~8시간: 60점
            When(충전시간_완속_숫자__gt=8.0, 충전시간_완속_숫자__lte=10.0, then=Value(80)),  # 8~10시간: 80점
            When(충전시간_완속_숫자__gt=10.0, 충전시간_완속_숫자__lte=12.0, then=Value(90)),  # 10~12시간: 90점
            When(충전시간_완속_숫자__gt=12.0, then=Value(100)),  # 12시간 이상: 100점
            default=Value(0),
            output_field=IntegerField(),
        ),
        복합전비_점수=Case(
            When(복합전비__lte=2.6, then=Value(0)),  # 0~2.6시간: 0점
            When(복합전비__gt=2.6, 복합전비__lte=4.0, then=Value(20)),  # 2.6~4.0시간: 20점
            When(복합전비__gt=4.0, 복합전비__lte=5.0, then=Value(40)),  # 4.0~5.0시간: 40점
            When(복합전비__gt=5.0, 복합전비__lte=5.5, then=Value(60)),  # 5.0~5.5시간: 60점
            When(복합전비__gt=5.5, 복합전비__lte=6.0, then=Value(80)),  # 5.5~6.0시간: 80점
            When(복합전비__gt=6.0, 복합전비__lte=6.3, then=Value(90)),  # 6.0~6.3시간: 90점
            When(복합전비__gt=6.3, then=Value(100)),  # 6.3시간 이상: 100점
            default=Value(0),
            output_field=IntegerField(),
        ),
        복합주행거리_점수=Case(
            When(복합주행거리_숫자__lt=70.0, then=Value(0)),  # 0~69.9 km: 0점
            When(복합주행거리_숫자__gte=70.0, 복합주행거리_숫자__lt=150.0, then=Value(20)),  # 70.0~149.9 km: 20점
            When(복합주행거리_숫자__gte=150.0, 복합주행거리_숫자__lt=250.0, then=Value(40)),  # 150.0~249.9 km: 40점
            When(복합주행거리_숫자__gte=250.0, 복합주행거리_숫자__lt=350.0, then=Value(60)),  # 250.0~349.9 km: 60점
            When(복합주행거리_숫자__gte=350.0, 복합주행거리_숫자__lt=450.0, then=Value(80)),  # 350.0~449.9 km: 80점
            When(복합주행거리_숫자__gte=450.0, 복합주행거리_숫자__lt=500.0, then=Value(90)),  # 450.0~499.9 km: 90점
            When(복합주행거리_숫자__gte=500.0, then=Value(100)),  # 500.0 km 이상: 100점
            default=Value(0),
            output_field=IntegerField(),
        ),
    ).annotate(
        score=
        F('배터리용량_점수') * Value(0.3) +  # 가격 점수 (20%)
        F('충전시간_급속_점수') * Value(0.075) +  # 배터리 용량 점수 (30%)
        F('충전시간_완속_점수') * Value(0.075) +  # 복합 주행 거리 점수 (25%)
        F('복합전비_점수') * Value(0.1) +  # 복합 전비 점수 (10%)
        F('복합주행거리_점수') * Value(0.25)  # 배터리 점수와 충전 시간 점수 합산 # 배터리 점수와 충전 시간 점수 합산
    )

    # 각 모델명에 대한 최소 가격 가져오기
    min_price_subquery = queryset.filter(모델명=OuterRef('모델명')).order_by('가격').values('가격')[:1]
    min_upprice_subquery = querysetprice.filter(모델명=OuterRef('모델명')).order_by('가격').values('가격')[:1]
    # 해당 최소 가격에 대한 점수 가져오기
    score_subquery = queryset.filter(모델명=OuterRef('모델명'), 가격=Subquery(min_price_subquery)).values('score')[:1]
    upscore_subquery = querysetprice.filter(모델명=OuterRef('모델명'), 가격=Subquery(min_upprice_subquery)).values('score')[:1]

    # # price_model: 각 모델명의 최소 가격과 해당 점수를 가져옴
    # price_model = queryset.annotate(
    #     min_price=Subquery(min_price_subquery),
    #     score=Subquery(score_subquery)
    # ).values('모델명', 'min_price', 'score','배터리_용량','충전시간_급속','충전시간_완속','복합전비','복합_주행거리').distinct().order_by('-score')

    # # upprice_model: 기존 모델명에 포함되지 않는 모델들 중 최소 가격 기준으로 가져옴
    # upprice_model = querysetprice.exclude(모델명__in=model_names).annotate(
    #     min_price=Min(min_upprice_subquery),
    #     score=Max(upscore_subquery)  # 또는 Subquery을 사용하여 min_price에 해당하는 score를 가져올 수 있습니다
    # ).values('모델명', 'min_price', 'score','배터리_용량','충전시간_급속','충전시간_완속','복합전비','복합_주행거리').distinct().order_by('-score')

    # price_model: 각 모델명의 최소 가격과 해당 점수를 가져옴

    price_model = queryset.annotate(
        min_price=Subquery(min_price_subquery),
        score=Subquery(score_subquery),
        가격_점수=F('가격_점수'),
        배터리용량_점수=F('배터리용량_점수'),
        충전시간_급속_점수=F('충전시간_급속_점수'),
        충전시간_완속_점수=F('충전시간_완속_점수'),
        복합전비_점수=F('복합전비_점수'),
        복합주행거리_점수=F('복합주행거리_점수'),
    ).values(
        '모델명', 'min_price', 'score',
        '가격_점수', '배터리용량_점수',
        '충전시간_급속_점수', '충전시간_완속_점수',
        '복합전비_점수', '복합주행거리_점수',
        '배터리_용량', '충전시간_급속', '충전시간_완속',
        '복합전비', '복합_주행거리', 'id'
    ).distinct()

    # upprice_model: 기존 모델명에 포함되지 않는 모델들 중 최소 가격 기준으로 가져옴
    upprice_model = querysetprice.exclude(모델명__in=model_names).annotate(
        min_price=Subquery(min_upprice_subquery),
        score=Subquery(upscore_subquery),
        가격_점수=Value(0),
        배터리용량_점수=F('배터리용량_점수'),
        충전시간_급속_점수=F('충전시간_급속_점수'),
        충전시간_완속_점수=F('충전시간_완속_점수'),
        복합전비_점수=F('복합전비_점수'),
        복합주행거리_점수=F('복합주행거리_점수'),
    ).values(
        '모델명', 'min_price', 'score',
        '가격_점수', '배터리용량_점수',
        '충전시간_급속_점수', '충전시간_완속_점수',
        '복합전비_점수', '복합주행거리_점수',
        '배터리_용량', '충전시간_급속', '충전시간_완속',
        '복합전비', '복합_주행거리', 'id'
    ).distinct()

    combined_models = list(price_model) + list(upprice_model)

    # 중복 제거를 위해 '모델명' 기준으로 최대값을 가져오기
    unique_models = {}
    for model in combined_models:
        model_name = model['모델명']
        if model_name not in unique_models:
            unique_models[model_name] = model
        else:
            # 중복된 모델의 값을 비교하여 더 높은 점수로 업데이트
            for key in ['배터리용량_점수', '충전시간_급속_점수', '충전시간_완속_점수', '복합전비_점수', '복합주행거리_점수']:
                unique_models[model_name][key] = max(unique_models[model_name][key], model[key])

    # 최종 결과
    # 점수 기준으로 정렬 후 상위 10개 모델 선택
    top_models = sorted(unique_models.values(), key=lambda x: x['score'], reverse=True)[:10]

    context = {
        'price_model': price_model,
        'upprice_model': upprice_model,
        'combined_models': top_models,
    }

    return render(request, 'filter/filter.html', context)