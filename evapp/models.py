from django.db import models
from django.contrib.auth.models import AbstractBaseUser
class Users(AbstractBaseUser):
    userid = models.CharField(max_length = 255, unique=True)
    name = models.CharField(max_length = 255)
    email = models.CharField(max_length = 255, unique=True)
    address = models.CharField(max_length = 255, blank=True, null=True)
    address_detail = models.CharField(max_length = 255, blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    delete_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'userid'
    REQUIRED_FIELDS = ['email', 'name']
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'users'

class Car(models.Model):
    # 기본 정보
    브랜드 = models.CharField(max_length=100, null=True, blank=True)
    모델명 = models.CharField(max_length=100, null=True, blank=True)
    세부모델명 = models.TextField(null=True, blank=True)
    차종 = models.CharField(max_length=50, null=True, blank=True)
    트림명 = models.TextField(null=True, blank=True)
    가격 = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)

    # 차량 크기 및 외관
    전장 = models.CharField(max_length=10, null=True, blank=True)
    전폭 = models.CharField(max_length=10, null=True, blank=True)
    전고 = models.CharField(max_length=10, null=True, blank=True)
    축거 = models.CharField(max_length=10, null=True, blank=True)
    윤거_전 = models.CharField(max_length=10, null=True, blank=True)
    윤거_후 = models.CharField(max_length=10, null=True, blank=True)
    오버행_전 = models.CharField(max_length=10, null=True, blank=True)
    오버행_후 = models.CharField(max_length=10, null=True, blank=True)
    차음_유리 = models.TextField(null=True, blank=True)
    자외선_차단유리 = models.TextField(null=True, blank=True)

    # 엔진 및 성능
    엔진형식 = models.CharField(max_length=100, null=True, blank=True)
    배기량 = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    최고출력 = models.CharField(max_length=50, null=True, blank=True)
    최대토크 = models.CharField(max_length=50, null=True, blank=True)
    최고속도 = models.CharField(max_length=50, null=True, blank=True)
    제로백 = models.CharField(max_length=50, null=True, blank=True)
    친환경 = models.TextField(null=True, blank=True)

    # 연료 및 배터리
    연료 = models.CharField(max_length=50, null=True, blank=True)
    연료탱크 = models.CharField(max_length=10, null=True, blank=True)
    CO2_배출 = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    배터리_용량 = models.CharField(max_length=10, null=True, blank=True)
    배터리_전압 = models.CharField(max_length=10, null=True, blank=True)
    배터리_제조사 = models.CharField(max_length=50, null=True, blank=True)
    배터리_종류 = models.CharField(max_length=50, null=True, blank=True)
    충전방식_급속 = models.CharField(max_length=50, null=True, blank=True)
    충전방식_완속 = models.CharField(max_length=50, null=True, blank=True)
    충전시간_급속 = models.CharField(max_length=10, null=True, blank=True)
    충전시간_완속 = models.CharField(max_length=10, null=True, blank=True)
    에너지소비효율 = models.CharField(max_length=50, null=True, blank=True)

    # 연비 및 전비
    복합연비 = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    고속연비 = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    도심연비 = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    복합전비 = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    고속전비 = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    도심전비 = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)

    # 주행 관련
    복합_주행거리 = models.CharField(max_length=50, null=True, blank=True)
    고속_주행거리 = models.CharField(max_length=50, null=True, blank=True)
    도심_주행거리 = models.CharField(max_length=50, null=True, blank=True)
    정속주행 = models.CharField(max_length=50, null=True, blank=True)

    # 구동 및 변속기
    변속기 = models.CharField(max_length=50, null=True, blank=True)
    굴림방식 = models.CharField(max_length=50, null=True, blank=True)

    # 브레이크 및 서스펜션
    브레이크_전 = models.CharField(max_length=50, null=True, blank=True)
    브레이크_후 = models.CharField(max_length=50, null=True, blank=True)
    서스펜션_전 = models.CharField(max_length=50, null=True, blank=True)
    서스펜션_후 = models.CharField(max_length=50, null=True, blank=True)

    # 타이어 및 휠
    타이어_전 = models.CharField(max_length=50, null=True, blank=True)
    타이어_후 = models.CharField(max_length=50, null=True, blank=True)
    휠_전 = models.CharField(max_length=50, null=True, blank=True)
    휠_후 = models.CharField(max_length=50, null=True, blank=True)

    # 안전 및 보조 기능
    주차보조 = models.TextField(null=True, blank=True)
    주행안전 = models.TextField(null=True, blank=True)
    보행자_안전 = models.TextField(null=True, blank=True)
    공회전_제한장치 = models.TextField(null=True, blank=True)
    에어백 = models.TextField(null=True, blank=True)

    # 외부 장비 및 기능
    도어포켓_라이트 = models.TextField(null=True, blank=True)
    엠비언트_라이트 = models.TextField(null=True, blank=True)
    룸미러 = models.TextField(null=True, blank=True)
    헤드램프 = models.TextField(null=True, blank=True)
    헤드램프_부가기능 = models.TextField(null=True, blank=True)
    주간_주행등 = models.TextField(null=True, blank=True)
    리어_램프 = models.TextField(null=True, blank=True)
    전방_안개등 = models.TextField(null=True, blank=True)
    아웃_사이드미러 = models.TextField(null=True, blank=True)

    # 내부 장비 및 기능
    주요기능 = models.TextField(null=True, blank=True)
    승차정원 = models.CharField(max_length=10, null=True, blank=True)
    시트배열 = models.CharField(max_length=50, null=True, blank=True)
    시트재질 = models.CharField(max_length=50, null=True, blank=True)
    동승석 = models.CharField(max_length=50, null=True, blank=True)
    운전석 = models.TextField(null=True, blank=True)
    뒷좌석_송풍구 = models.CharField(max_length=50, null=True, blank=True)
    뒷좌석_측면커튼 = models.CharField(max_length=50, null=True, blank=True)
    뒷좌석_후면커튼 = models.CharField(max_length=50, null=True, blank=True)

    # 디지털 기능 및 계기판
    계기판 = models.CharField(max_length=50, null=True, blank=True)
    스티어링_휠 = models.CharField(max_length=50, null=True, blank=True)
    화면크기 = models.CharField(max_length=50, null=True, blank=True)

    # 엔터테인먼트
    사운드시스템 = models.CharField(max_length=50, null=True, blank=True)
    스피커 = models.CharField(max_length=50, null=True, blank=True)

    # 트렁크 및 적재
    적재량 = models.CharField(max_length=50, null=True, blank=True)
    적재함_길이 = models.CharField(max_length=50, null=True, blank=True)
    적재함_너비 = models.CharField(max_length=50, null=True, blank=True)
    적재함_높이 = models.CharField(max_length=50, null=True, blank=True)
    트렁크 = models.CharField(max_length=50, null=True, blank=True)
    트렁크_전_용량 = models.CharField(max_length=50, null=True, blank=True)
    트렁크_후_용량 = models.CharField(max_length=50, null=True, blank=True)

    # 기타 장비 및 부가 기능
    에어컨 = models.TextField(null=True, blank=True)
    엔진시동 = models.CharField(max_length=50, null=True, blank=True)
    와이퍼 = models.CharField(max_length=50, null=True, blank=True)
    파워_아웃렛 = models.CharField(max_length=50, null=True, blank=True)
    온도조절_범위 = models.CharField(max_length=50, null=True, blank=True)
    루프 = models.CharField(max_length=50, null=True, blank=True)
    주차_브레이크 = models.CharField(max_length=50, null=True, blank=True)
    부가기능 = models.TextField(null=True, blank=True)
    보조금_id = models.BigIntegerField(null = True, blank=True)
    사진 = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'car'

class Oil(models.Model):
    휘발유 = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    경유 = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'oil'

class Subsidy(models.Model):
    도 = models.CharField(max_length=50)
    시 = models.CharField(max_length=50)
    차종 = models.CharField(max_length=50)
    제조사 = models.CharField(max_length=50)
    모델명 = models.CharField(max_length=100)
    국가보조금 = models.DecimalField(max_digits=5, decimal_places=1)
    지자체보조금 = models.DecimalField(max_digits=5, decimal_places=1)

    class Meta:
        db_table = 'subsidy'
        managed = False  # Django가 이 테이블을 관리하지 않도록 설정

class EVCar(models.Model):
    차종 = models.CharField(max_length=50)
    제조사 = models.CharField(max_length=50)
    모델명 = models.CharField(max_length=100)

    class Meta:
        managed = False  # Django가 이 테이블을 관리하지 않음
        db_table = 'ev_car'  # 데이터베이스 테이블 이름

class UsedCar(models.Model):
    차종 = models.CharField(max_length=255)
    모델명 = models.CharField(max_length=255)
    출고일 = models.CharField(max_length=7)
    주행거리 = models.IntegerField()
    가격 = models.DecimalField(max_digits=10, decimal_places=0)
    신차가격 = models.DecimalField(max_digits=10, decimal_places=0)

    class Meta:
        db_table = 'used_car'
        managed = False

class Apt(models.Model):
    id = models.IntegerField(primary_key=True)
    도로명주소 = models.CharField(max_length=255)
    전체대수 = models.IntegerField()
    전기차대수 = models.IntegerField()
    충전기대수_지상 = models.IntegerField()
    충전기대수_지하 = models.IntegerField()

    class Meta:
        db_table = 'apt'
        managed = False

class AptCharger(models.Model):
    id = models.AutoField(primary_key=True)
    apt_id = models.IntegerField()
    규격 = models.CharField(max_length=255)
    충전속도 = models.CharField(max_length=50)
    개수 = models.IntegerField(null=True, blank=True)
    사업자 = models.CharField(max_length=255)
    회원가 = models.DecimalField(max_digits=10, decimal_places=1)
    비회원가 = models.DecimalField(max_digits=10, decimal_places=1)

    class Meta:
        db_table = 'apt_charger'
        managed = False

class Charger(models.Model):
    id = models.AutoField(primary_key=True)
    주소 = models.CharField(max_length=255, null=True, blank=True)
    충전소명 = models.CharField(max_length=255, null=True, blank=True)
    충전량 = models.CharField(max_length=100, null=True, blank=True)
    운영기관 = models.CharField(max_length=255, null=True, blank=True)
    충전기타입 = models.CharField(max_length=100, null=True, blank=True)
    이용자제한 = models.CharField(max_length=100, null=True, blank=True)
    회원가 = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    비회원가 = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    위도 = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    경도 = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        db_table = 'charger'
        managed = False