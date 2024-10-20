// 비교 표의 변수 정리
const elements = {
    left: {
        modal: document.getElementById('left-modal'),
        btn: document.getElementById('left-btn'),
        close: document.querySelector('.left-close'),
        selectIds: ['brand', 'type', 'fuel', 'model', 'detail-model', 'trim'],
        oilSpecId: 'left-oil-spec',
        ageSelectId: 'left-age',
        mileageSelectId: 'left-km',
        taxSpecId: 'left-tax-spec',
        subsidyId: 'left-subsidy'
    },
    right: {
        modal: document.getElementById('right-modal'),
        btn: document.getElementById('right-btn'),
        close: document.querySelector('.right-close'),
        selectIds: ['brand', 'type', 'fuel', 'model', 'detail-model', 'trim'],
        oilSpecId: 'right-oil-spec',
        ageSelectId: 'right-age',
        mileageSelectId: 'right-km',
        taxSpecId: 'right-tax-spec',
        subsidyId: 'right-subsidy'
    }
};

/* ---------------------------------------------------------------------------------------------------------------------------*/
// 모달

// 모달 select 초기화 함수
function resetAllSelects(side) {
    elements[side].selectIds.forEach(selectId => {
        if (selectId === 'brand') {
            // 브랜드는 옵션을 유지하고 선택된 값만 초기화
            const selectBox = document.getElementById(`${side}-${selectId}`);
            selectBox.selectedIndex = 0; // "선택" 옵션으로 초기화
        } else {
            // 나머지 선택 상자는 전체 초기화
            resetSelectBox(`${side}-${selectId}`);
        }
    });
}

// 모달 표시 O/X 함수
function modalAction(modal, displayStyle, side) {
    modal.style.display = displayStyle;

    // 모달이 닫힐 때 모든 선택 박스 초기화 (브랜드는 옵션 유지)
    if (displayStyle === 'none') {
        resetAllSelects(side);
    }
}

// 모달 버튼 뜨고 닫기 설정
Object.keys(elements).forEach(side => {
    elements[side].btn.onclick = () => modalAction(elements[side].modal, 'block', side);
    elements[side].close.onclick = () => modalAction(elements[side].modal, 'none', side);
});

// 화면 밖 누르면 모달 닫기
window.onclick = function(event) {
    Object.keys(elements).forEach(side => {
        const { modal } = elements[side];
        if (event.target === modal) modalAction(modal, 'none', side);
    });
};



/* ---------------------------------------------------------------------------------------------------------------------------*/

// Select
// Select 태그 업데이트와 초기화 함수
function updateSelectBox(selectId, options) {
    const selectBox = document.getElementById(selectId);
    const defaultOption = selectBox.dataset.defaultOption || '선택';
    selectBox.innerHTML = `<option value="">${defaultOption}</option>`;
    options.forEach(option => {
        const opt = document.createElement('option');
        opt.value = option;
        opt.innerHTML = option;
        selectBox.appendChild(opt);
    });
}

function resetSelectBox(selectId) {
    const selectBox = document.getElementById(selectId);
    const defaultOption = selectBox.dataset.defaultOption || '선택';
    selectBox.innerHTML = `<option value="">${defaultOption}</option>`;
}

// 모든 하위 선택 박스를 초기화하는 함수
function resetSubSelectsFrom(selectId, side) {
    const allSelects = elements[side].selectIds;
    const startIndex = allSelects.indexOf(selectId) + 1;
    const subSelects = allSelects.slice(startIndex);
    subSelects.forEach(select => resetSelectBox(`${side}-${select}`));
}

/* ---------------------------------------------------------------------------------------------------------------------------*/

// API 요청 함수
async function fetchData(url) {
    try {
        const response = await fetch(url);
        return await response.json();
    } catch (error) {
        console.error(`Error fetching data from ${url}:`, error);
    }
}

// 기름값 초기 설정
let oilPrices = { gasoline: 0, diesel: 0 };

// 페이지 로드 시 기름값, 브랜드 및 도시 가져오기
document.addEventListener('DOMContentLoaded', async () => {
    const oilData = await fetchData('/api/oil/');
    if (oilData) {
        oilPrices = {
            gasoline: oilData.gasoline || 0,
            diesel: oilData.diesel || 0
        };
    }

    const carData = await fetchData('/api/car/');
    if (carData?.brands) {
        updateSelectBox('left-brand', carData.brands);
        updateSelectBox('right-brand', carData.brands);
    }

    const cityData = await fetchData('/api/city/');
    if (cityData?.provinces_and_cities) {
        const provinces = [...new Set(cityData.provinces_and_cities.map(item => item.도))];
        updateSelectBox('left-province-select', provinces);
        updateSelectBox('right-province-select', provinces);

        // 도 선택 시 시 데이터 업데이트
        ['left', 'right'].forEach(side => {
            document.getElementById(`${side}-province-select`).addEventListener('change', (event) => {
                const selectedProvince = event.target.value;
                const cities = cityData.provinces_and_cities
                    .filter(item => item.도 === selectedProvince)
                    .map(item => item.시);
                updateSelectBox(`${side}-city-select`, cities);
            });
        });
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

    resetSubsidyInfo(side);

    const ids = elements[side].selectIds;
    const [brand, car_type, fuel, model, detail_model, trim] = ids.map(id => document.getElementById(`${side}-${id}`).value);
    const age = document.getElementById(elements[side].ageSelectId).value;

    if (!brand || !car_type || !fuel || !model || !detail_model || !trim || !age) {
        alert('모든 값을 선택해주세요.');
        return;
    }

    const url = `/api/spec/?brand=${encodeURIComponent(brand)}&car_type=${encodeURIComponent(car_type)}&fuel=${encodeURIComponent(fuel)}&model=${encodeURIComponent(model)}&detail_model=${encodeURIComponent(detail_model)}&trim=${encodeURIComponent(trim)}`;
    const data = await fetchData(url);


    if (data?.specs) {
        displaySpecs(data.specs, side);
        calculateAndDisplayCosts(data.specs, side);

        // 모달 닫기
        modalAction(elements[side].modal, 'none', side);
    } else {
        alert('해당 차량의 정보를 찾을 수 없습니다.');
    }
}

// 보조금 정보를 초기화하는 함수
function resetSubsidyInfo(side) {
    // 각 side의 보조금 정보를 초기화
    document.getElementById(`${side}-national-subsidy`).innerText = '';
    document.getElementById(`${side}-local-subsidy`).innerText = '';
}


// 유류비 및 자동차세를 계산하고 표시하는 함수
function calculateAndDisplayCosts(specs, side) {
    const age = document.getElementById(elements[side].ageSelectId).value;
    const mileage = document.getElementById(elements[side].mileageSelectId).value;

    if (!specs || !specs.연료 || (specs.연료 !== '전기(배터리)' && !specs.배기량)) {
        document.getElementById(elements[side].taxSpecId).innerHTML = '';
        document.getElementById(elements[side].oilSpecId).innerHTML = '';
        return;
    }

    document.getElementById(elements[side].taxSpecId).innerHTML = specs.연료 === '전기(배터리)' ? calculateElectricTax(age) : calculateTax(specs, age);
    document.getElementById(elements[side].oilSpecId).innerHTML = calculateOilCost(specs, mileage, age);
}

// 전기차에 대한 자동차세 계산 함수
function calculateElectricTax(age) {
    const baseTax = 130000; // 전기차 기본 자동차세
    let totalTax = 0;
    for (let year = 1; year <= age; year++) {
        const reductionRate = getReductionRate(year);
        totalTax += baseTax * (1 - reductionRate);
    }
    return Math.round(totalTax).toLocaleString() + ' 원';
}

// 차령 및 주행 거리 선택 변경 시 이벤트 리스너 추가 함수
function addAgeAndMileageChangeListener(side) {
    document.getElementById(elements[side].ageSelectId).addEventListener('change', () => {
        const specs = getSpecsFromDOM(side);
        calculateAndDisplayCosts(specs, side);
    });
    document.getElementById(elements[side].mileageSelectId).addEventListener('change', () => {
        const specs = getSpecsFromDOM(side);
        calculateAndDisplayCosts(specs, side);
    });
}

// DOM에서 현재 선택된 차량 스펙 가져오기
function getSpecsFromDOM(side) {
    return {
        연료: document.getElementById(`${side}-fuel-spec`).innerHTML,
        배기량: document.getElementById(`${side}-displacement-spec`).innerHTML,
        복합연비: document.getElementById(`${side}-combined-fuel-efficiency-spec`).innerHTML
    };
}

// 자동차세 계산 함수
function calculateTax(specs, age) {
    const displacement = parseFloat(specs.배기량) || 0;
    let baseTax;

    if (displacement === 0) {
        baseTax = 130000;
    } else if (displacement <= 1000) {
        baseTax = 104 * displacement;
    } else if (displacement <= 1600) {
        baseTax = 182 * displacement;
    } else {
        baseTax = 260 * displacement;
    }

    let totalTax = 0;
    for (let year = 1; year <= age; year++) {
        const reductionRate = getReductionRate(year);
        totalTax += baseTax * (1 - reductionRate);
    }

    return Math.round(totalTax).toLocaleString() + ' 원';
}

// 차령에 따른 경감율을 반환하는 함수
function getReductionRate(age) {
    const rates = [0, 0, 0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50];
    return rates[Math.min(age, 12)];
}

// 유류비 계산 함수
function calculateOilCost(specs, mileage, age) {
    const fuelType = specs.연료;
    let fuelEfficiency = parseFloat(specs.복합연비 || specs.복합전비);

    if (isNaN(fuelEfficiency) || fuelEfficiency <= 0) {
        console.log('유효하지 않은 연비 값:', fuelEfficiency);
        return '연비 정보 없음';
    }

    let costPerUnit;
    if (fuelType === '전기(배터리)') {
        costPerUnit = 347.2; // kWh당 비용
    } else if (fuelType === '가솔린' || fuelType === '가솔린+전기') {
        costPerUnit = oilPrices.gasoline; // 휘발유 가격
    } else if (fuelType === '디젤' || fuelType === '디젤+전기') {
        costPerUnit = oilPrices.diesel; // 경유 가격
    } else {
        console.log('알 수 없는 연료 타입:', fuelType);
        return '연료 정보 없음';
    }

    mileage = parseFloat(mileage);
    if (isNaN(mileage) || mileage <= 0) {
        console.log('유효하지 않은 주행 거리 값:', mileage);
        return '주행 거리 정보 없음';
    }

    const annualCost = (mileage / fuelEfficiency) * costPerUnit * age;
    console.log(`유류비 계산 - 연료 타입: ${fuelType}, 연비: ${fuelEfficiency}, 주행 거리: ${mileage}, 차령: ${age}, 유류비: ${annualCost}`);
    return Math.round(annualCost).toLocaleString() + ' 원';
}

// 차량 스펙 표시
function displaySpecs(specs, side) {
    const specIds = {
        'brand-spec': '브랜드',
        'model-spec': '모델명',
        'detail-model-spec': '세부모델명',
        'type-spec': '차종',
        'trim-spec': '트림명',
        'price-spec': '가격',
        'fuel-spec': '연료',
        'displacement-spec': '배기량',
        'subsidy': '보조금_id'
    };

    for (let [id, label] of Object.entries(specIds)) {
        const element = document.getElementById(`${side}-${id}`);
        if (element) {
            if (label === '가격' && specs[label]) {
                element.innerHTML = parseInt(specs[label]).toLocaleString() + ' 원';
            } else {
                element.innerHTML = specs[label] ?? '';
            }
        }
    }

    const subsidyId = specs['보조금_id'];
    const provinceSelect = document.getElementById(`${side}-province-select`);
    const citySelect = document.getElementById(`${side}-city-select`);

    if (!subsidyId) {
        // 보조금 정보가 없으면 해당 select 태그에 hidden 클래스 추가
        provinceSelect.classList.add('hidden');
        citySelect.classList.add('hidden');
    } else {
        // 보조금 정보가 있으면 hidden 클래스 제거
        provinceSelect.classList.remove('hidden');
        citySelect.classList.remove('hidden');
    }

    const combinedFuel = specs.복합연비 || specs.복합전비;
    const highwayFuel = specs.고속연비 || specs.고속전비;
    const cityFuel = specs.도심연비 || specs.도심전비;

    document.getElementById(`${side}-combined-fuel-efficiency-spec`).innerHTML =
        combinedFuel ? `${formatNumberWithoutTrailingZero(parseFloat(combinedFuel))} ${specs.복합연비 ? 'km/L' : 'km/kWh'}` : '';
    document.getElementById(`${side}-highway-fuel-efficiency-spec`).innerHTML =
        highwayFuel ? `${formatNumberWithoutTrailingZero(parseFloat(highwayFuel))} ${specs.고속연비 ? 'km/L' : 'km/kWh'}` : '';
    document.getElementById(`${side}-city-fuel-efficiency-spec`).innerHTML =
        cityFuel ? `${formatNumberWithoutTrailingZero(parseFloat(cityFuel))} ${specs.도심연비 ? 'km/L' : 'km/kWh'}` : '';
}


// 소수점 없는 숫자를 처리하는 함수
function formatNumberWithoutTrailingZero(number) {
    return Number.isInteger(number) ? number : number.toFixed(1).replace(/\.0$/, '');
}

// 보조금 정보를 가져오는 함수
async function fetchSubsidyInfo(side) {
    const carId = document.getElementById(`${side}-subsidy`).innerText;
    const selectedProvince = document.getElementById(`${side}-province-select`).value;
    const selectedCity = document.getElementById(`${side}-city-select`).value;

    if (!carId || !selectedProvince || !selectedCity) {
        alert('차량을 선택해 주세요.');
        return;
    }

    const url = `/api/subsidy/?car_id=${carId}&do=${selectedProvince}&city=${selectedCity}`;
    try {
        const response = await fetch(url);
        const data = await response.json();

        if (response.ok) {
            // 만원 단위로 제공되는 값을 원 단위로 변환
            const nationalSubsidy = (data.국가보조금 * 10000).toLocaleString() + ' 원';
            const localSubsidy = (data.지자체보조금 * 10000).toLocaleString() + ' 원';

            document.getElementById(`${side}-national-subsidy`).innerText = nationalSubsidy;
            document.getElementById(`${side}-local-subsidy`).innerText = localSubsidy;
        } else {
            alert(data.error || '보조금 정보를 가져오는 데 문제가 발생했습니다.');
        }
    } catch (error) {
        console.error('Error fetching subsidy info:', error);
    }
}


// 이벤트 리스너 설정 함수
function setEventListeners(side) {
    const selects = elements[side].selectIds;

    document.getElementById(`${side}-brand`).addEventListener('change', async function() {
        resetSubSelectsFrom('brand', side);
        await fetchOptions(this.value, null, null, null, null, 'types', `${side}-type`);
    });

    document.getElementById(`${side}-type`).addEventListener('change', async function() {
        resetSubSelectsFrom('type', side);
        const brand = document.getElementById(`${side}-brand`).value;
        await fetchOptions(brand, this.value, null, null, null, 'fuels', `${side}-fuel`);
    });

    document.getElementById(`${side}-fuel`).addEventListener('change', async function() {
        resetSubSelectsFrom('fuel', side);
        const brand = document.getElementById(`${side}-brand`).value;
        const car_type = document.getElementById(`${side}-type`).value;
        await fetchOptions(brand, car_type, this.value, null, null, 'models', `${side}-model`);
    });

    document.getElementById(`${side}-model`).addEventListener('change', async function() {
        resetSubSelectsFrom('model', side);
        const brand = document.getElementById(`${side}-brand`).value;
        const car_type = document.getElementById(`${side}-type`).value;
        const fuel = document.getElementById(`${side}-fuel`).value;
        await fetchOptions(brand, car_type, fuel, this.value, null, 'detail_models', `${side}-detail-model`);
    });

    document.getElementById(`${side}-detail-model`).addEventListener('change', async function() {
        resetSubSelectsFrom('detail-model', side);
        const brand = document.getElementById(`${side}-brand`).value;
        const car_type = document.getElementById(`${side}-type`).value;
        const fuel = document.getElementById(`${side}-fuel`).value;
        const model = document.getElementById(`${side}-model`).value;
        await fetchOptions(brand, car_type, fuel, model, this.value, 'trims', `${side}-trim`);
    });

    document.getElementById(`${side}-confirm`).addEventListener('click', () => fetchCarSpecs(side));

    // 도와 시 선택 시 보조금 정보 가져오기
    document.getElementById(`${side}-city-select`).addEventListener('change', () => fetchSubsidyInfo(side));
}

// 총 금액을 계산하고 표시하는 함수
function calculateAndDisplayTotalCost(specs, side) {
    // 차량 가격을 정수로 변환
    const price = parseInt(specs.가격) || 0;

    // 보조금 값 가져오기
    const nationalSubsidy = parseInt(document.getElementById(`${side}-national-subsidy`).innerText.replace(/[^0-9]/g, '')) || 0;
    const localSubsidy = parseInt(document.getElementById(`${side}-local-subsidy`).innerText.replace(/[^0-9]/g, '')) || 0;
    const totalSubsidy = nationalSubsidy + localSubsidy;

    // 자동차세 값 가져오기
    const tax = parseInt(document.getElementById(elements[side].taxSpecId).innerText.replace(/[^0-9]/g, '')) || 0;

    // 총 금액 계산
    const totalCost = price - totalSubsidy + tax;

    // 총 금액 표시
    document.getElementById(`${side}-total-cost`).innerText = `${totalCost.toLocaleString()} 원`;
}

// 기존 calculateAndDisplayCosts 함수에 총 금액 계산 추가
function calculateAndDisplayCosts(specs, side) {
    const age = document.getElementById(elements[side].ageSelectId).value;
    const mileage = document.getElementById(elements[side].mileageSelectId).value;

    if (!specs || !specs.연료 || (specs.연료 !== '전기(배터리)' && !specs.배기량)) {
        document.getElementById(elements[side].taxSpecId).innerHTML = '';
        document.getElementById(elements[side].oilSpecId).innerHTML = '';
        document.getElementById(`${side}-total-cost`).innerHTML = ''; // 총 금액 초기화
        return;
    }

    document.getElementById(elements[side].taxSpecId).innerHTML = specs.연료 === '전기(배터리)' ? calculateElectricTax(age) : calculateTax(specs, age);
    document.getElementById(elements[side].oilSpecId).innerHTML = calculateOilCost(specs, mileage, age);

    // 총 금액 계산 및 표시
    calculateAndDisplayTotalCost(specs, side);
}


// 왼쪽, 오른쪽 이벤트 리스너 설정
setEventListeners('left');
setEventListeners('right');
addAgeAndMileageChangeListener('left');
addAgeAndMileageChangeListener('right');
