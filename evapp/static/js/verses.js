// 모달 표시/숨기기 함수
function modalAction(modal, displayStyle) {
    modal.style.display = displayStyle;
}

const elements = {
    left: {
        modal: document.getElementById('left-modal'),
        btn: document.getElementById('left-btn'),
        close: document.querySelector('.left-close'),
        selectIds: ['brand', 'type', 'fuel', 'model', 'detail-model', 'trim']
    },
    right: {
        modal: document.getElementById('right-modal'),
        btn: document.getElementById('right-btn'),
        close: document.querySelector('.right-close'),
        selectIds: ['brand', 'type', 'fuel', 'model', 'detail-model', 'trim']
    }
};

// 모달 버튼과 닫기 버튼 이벤트 설정
Object.keys(elements).forEach(side => {
    elements[side].btn.onclick = () => modalAction(elements[side].modal, 'block');
    elements[side].close.onclick = () => modalAction(elements[side].modal, 'none');
});

// 화면 외부 클릭으로 모달 닫기
window.onclick = function(event) {
    Object.values(elements).forEach(({ modal }) => {
        if (event.target == modal) modalAction(modal, 'none');
    });
};

// 선택 박스 업데이트와 초기화 함수
function updateSelectBox(selectId, options) {
    const selectBox = document.getElementById(selectId);
    selectBox.innerHTML = '<option value="">선택</option>';
    options.forEach(option => {
        const opt = document.createElement('option');
        opt.value = option;
        opt.innerHTML = option;
        selectBox.appendChild(opt);
    });
}

function resetSelectBox(selectId) {
    document.getElementById(selectId).innerHTML = '<option value="">선택</option>';
}

// 모든 하위 선택 박스를 초기화하는 함수
function resetSubSelectsFrom(selectId, side) {
    const allSelects = elements[side].selectIds;
    const startIndex = allSelects.indexOf(selectId) + 1;
    const subSelects = allSelects.slice(startIndex);
    subSelects.forEach(select => resetSelectBox(`${side}-${select}`));
}

// API 요청 함수
async function fetchData(url) {
    try {
        const response = await fetch(url);
        return await response.json();
    } catch (error) {
        console.error(`Error fetching data from ${url}:`, error);
    }
}

// 페이지 로드 시 브랜드 목록 로드
document.addEventListener('DOMContentLoaded', async () => {
    const data = await fetchData('/api/car/');
    if (data?.brands) {
        updateSelectBox('left-brand', data.brands);
        updateSelectBox('right-brand', data.brands);
    }
});

// 데이터 기반 목록 갱신 함수
async function fetchOptions(brand, car_type, fuel, model, detail_model, endpoint, selectId) {
    const url = new URL(`/api/car/`, window.location.origin);
    if (brand) url.searchParams.append('brand', brand);
    if (car_type) url.searchParams.append('car_type', car_type);
    if (fuel) url.searchParams.append('fuel', fuel);
    if (model) url.searchParams.append('model', model);
    if (detail_model) url.searchParams.append('detail_model', detail_model);

    const data = await fetchData(url);
    if (data && data[endpoint]) {
        updateSelectBox(selectId, data[endpoint]);
    }
}

// 차량 스펙을 가져오는 함수
async function fetchCarSpecs(side) {
    const ids = elements[side].selectIds;
    const [brand, car_type, fuel, model, detail_model, trim] = ids.map(id => document.getElementById(`${side}-${id}`).value);

    // 모든 값이 채워져 있는지 확인
    if (!brand || !car_type || !fuel || !model || !detail_model || !trim) {
        alert('모든 값을 선택해주세요.');
        return;
    }

    const url = `/api/spec/?brand=${encodeURIComponent(brand)}&car_type=${encodeURIComponent(car_type)}&fuel=${encodeURIComponent(fuel)}&model=${encodeURIComponent(model)}&detail_model=${encodeURIComponent(detail_model)}&trim=${encodeURIComponent(trim)}`;
    const data = await fetchData(url);
    if (data?.specs) {
        console.log('Specs:', data.specs);
        displaySpecs(data.specs, side);

        // 모달 닫기
        modalAction(elements[side].modal, 'none');
    } else {
        alert('해당 차량의 정보를 찾을 수 없습니다.');
    }
}

// 차량 스펙 표시
function displaySpecs(specs, side) {
    const specIds = {
        brand: '브랜드', model: '모델명', 'detail-model': '세부모델명', type: '차종', trim: '트림명', price: '가격',
        length: '전장', width: '전폭', height: '전고', wheelbase: '축거', 'front-tread': '윤거_전', 'rear-tread': '윤거_후',
        'front-overhang': '오버행_전', 'rear-overhang': '오버행_후', engine: '엔진형식', displacement: '배기량',
        'max-power': '최고출력', 'max-torque': '최대토크', 'max-speed': '최고속도', acceleration: '제로백',
        fuel: '연료', 'fuel-tank': '연료탱크', 'co2-emission': 'CO2_배출', 'battery-capacity': '배터리_용량',
        transmission: '변속기', 'drive-type': '굴림방식', 'front-tire': '타이어_전', 'rear-tire': '타이어_후',
        'front-wheel': '휠_전', 'rear-wheel': '휠_후', 'parking-assist': '주차보조', 'driving-safety': '주행안전',
        'pedestrian-safety': '보행자_안전', airbag: '에어백', 'door-pocket-light': '도어포켓_라이트',
        'ambient-light': '엠비언트_라이트', 'room-mirror': '룸미러', 'seating-capacity': '승차정원',
        'seat-layout': '시트배열', 'seat-material': '시트재질', dashboard: '계기판', 'steering-wheel': '스티어링_휠',
        'sound-system': '사운드시스템', speaker: '스피커', 'cargo-capacity': '적재량', trunk: '트렁크',
        ac: '에어컨', 'engine-start': '엔진시동', image: '사진'
    };

    for (let [id, label] of Object.entries(specIds)) {
        const element = document.getElementById(`${side}-${id}-spec`);

        if (label === '가격' && specs[label]) {
            // 가격을 1,000,000 원 형식으로 표시
            const formattedPrice = parseInt(specs[label]).toLocaleString() + ' 원';
            element.innerHTML = formattedPrice;
        } else if ((label === '승차정원' || label === '스피커') && specs[label]) {
            // 승차정원과 스피커에서 소수점 없애기
            element.innerHTML = formatNumberWithoutTrailingZero(parseFloat(specs[label]));
        } else {
            element.innerHTML = specs[label] ?? '';
        }
    }

    // 연비와 전비 조건 수정: 각 값이 `null`, `undefined` 또는 빈 문자열이 아닌 경우
    const combinedFuel = specs.복합연비 || specs.복합전비;
    const highwayFuel = specs.고속연비 || specs.고속전비;
    const cityFuel = specs.도심연비 || specs.도심전비;

    document.getElementById(`${side}-combined-fuel-efficiency-spec`).innerHTML =
        combinedFuel ? `${formatNumberWithoutTrailingZero(parseFloat(combinedFuel))} ${specs.복합연비 ? 'km/L' : 'km/kWh'}` : '';

    document.getElementById(`${side}-highway-fuel-efficiency-spec`).innerHTML =
        highwayFuel ? `${formatNumberWithoutTrailingZero(parseFloat(highwayFuel))} ${specs.고속연비 ? 'km/L' : 'km/kWh'}` : '';

    document.getElementById(`${side}-city-fuel-efficiency-spec`).innerHTML =
        cityFuel ? `${formatNumberWithoutTrailingZero(parseFloat(cityFuel))} ${specs.도심연비 ? 'km/L' : 'km/kWh'}` : '';

    // 이미지를 설정할 때 staticUrl 변수를 사용
    const imageSpecElement = document.getElementById(`${side}-image-spec`);
    if (specs.사진) {
        const imagePath = `${staticUrl}${specs.사진}`;
        imageSpecElement.innerHTML = `<img src="${imagePath}" alt="${specs.모델명}" style="width: 300px; height: auto;">`;
    } else {
        imageSpecElement.innerHTML = '이미지가 없습니다.';
    }
}

// 이벤트 리스너 설정 함수
function setEventListeners(side) {
    const selects = elements[side].selectIds;

    document.getElementById(`${side}-brand`).addEventListener('change', async function() {
        resetSubSelectsFrom('brand', side);  // 모든 하위 선택 초기화
        await fetchOptions(this.value, null, null, null, null, 'types', `${side}-type`);
    });

    document.getElementById(`${side}-type`).addEventListener('change', async function() {
        resetSubSelectsFrom('type', side);  // 모든 하위 선택 초기화
        const brand = document.getElementById(`${side}-brand`).value;
        await fetchOptions(brand, this.value, null, null, null, 'fuels', `${side}-fuel`);
    });

    document.getElementById(`${side}-fuel`).addEventListener('change', async function() {
        resetSubSelectsFrom('fuel', side);  // 모든 하위 선택 초기화
        const brand = document.getElementById(`${side}-brand`).value;
        const car_type = document.getElementById(`${side}-type`).value;
        await fetchOptions(brand, car_type, this.value, null, null, 'models', `${side}-model`);
    });

    document.getElementById(`${side}-model`).addEventListener('change', async function() {
        resetSubSelectsFrom('model', side);  // 모든 하위 선택 초기화
        const brand = document.getElementById(`${side}-brand`).value;
        const car_type = document.getElementById(`${side}-type`).value;
        const fuel = document.getElementById(`${side}-fuel`).value;
        await fetchOptions(brand, car_type, fuel, this.value, null, 'detail_models', `${side}-detail-model`);
    });

    document.getElementById(`${side}-detail-model`).addEventListener('change', async function() {
        resetSubSelectsFrom('detail-model', side);  // 트림 초기화
        const brand = document.getElementById(`${side}-brand`).value;
        const car_type = document.getElementById(`${side}-type`).value;
        const fuel = document.getElementById(`${side}-fuel`).value;
        const model = document.getElementById(`${side}-model`).value;
        await fetchOptions(brand, car_type, fuel, model, this.value, 'trims', `${side}-trim`);
    });

    document.getElementById(`${side}-confirm`).addEventListener('click', () => fetchCarSpecs(side));
}

// 소수점 없는 숫자를 처리하는 함수
function formatNumberWithoutTrailingZero(number) {
    return Number.isInteger(number) ? number : number.toFixed(1).replace(/\.0$/, '');
}

// 왼쪽, 오른쪽 이벤트 리스너 설정
setEventListeners('left');
setEventListeners('right');