import requests
import xml.etree.ElementTree as ET
from django.core.management.base import BaseCommand
from evapp.models import Oil


class Command(BaseCommand):
    help = '유가 정보를 가져와서 저장합니다'

    def handle(self, *args, **kwargs):
        url = "http://www.opinet.co.kr/api/avgAllPrice.do?out=xml&code=F241005339"
        response = requests.get(url)

        if response.status_code == 200:
            root = ET.fromstring(response.content)

            # XML에서 휘발유와 경유 가격 추출
            gasoline_price = None
            diesel_price = None

            for oil in root.findall('.//OIL'):
                prodnm = oil.find('PRODNM').text
                price = float(oil.find('PRICE').text)

                if prodnm == '휘발유':
                    gasoline_price = price
                elif prodnm == '자동차용경유':
                    diesel_price = price

            if gasoline_price is not None and diesel_price is not None:
                # 유가 정보를 DB에 저장 또는 업데이트
                Oil.objects.create(휘발유=gasoline_price, 경유=diesel_price)
                self.stdout.write(self.style.SUCCESS('유가 정보를 성공적으로 저장했습니다.'))
            else:
                self.stdout.write(self.style.ERROR('유가 정보를 가져오지 못했습니다.'))
        else:
            self.stdout.write(self.style.ERROR(f'API 요청 실패: {response.status_code}'))
