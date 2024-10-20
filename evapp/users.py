from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from .forms import SignUp
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from .models import Users
from django.utils import timezone

def signup(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = SignUp(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # 저장을 미뤄서 해싱을 먼저 처리
            user.set_password(form.cleaned_data['password'])  # 비밀번호 해싱
            user.save()  # 사용자 저장
            login(request, user)  # 회원가입 후 자동 로그인
            messages.success(request, '회원가입 성공!')
            return redirect('/')  # 가입 후 이동할 페이지
    else:
        form = SignUp()

    return render(request, 'signup.html', {'form': form})

# 로그인 로직
def userLogin(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'GET':

        return render(request, 'login.html')

    elif request.method == 'POST':

        userid = request.POST.get('userid')
        password = request.POST.get('password')

        user = authenticate(request, userid=userid, password=password)

        if user is not None:
            if user.is_active:
                login(request, user=user)
                return redirect('home')
            else:
                messages.error(request, "비활성화된 계정입니다. 관리자에게 문의하세요.")
                return redirect('login')
        else:
            messages.error(request, "아이디 혹은 비밀번호가 틀렸습니다.")
            return redirect('login')

def userLogout(request):
    logout(request)  # 세션 종료 (로그아웃 처리)
    return redirect('/')  # 로그아웃 후 홈 페이지로 리다이렉트

@login_required(login_url='/login/')
def mypage(request):
    user = request.user
    return render(request, 'mypage.html', {'user': user})

@login_required(login_url='/login/')
def update_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if check_password(new_password, request.user.password):
            messages.error(request, '새 비밀번호가 기존 비밀번호와 같습니다. 다시 입력해주세요.')
        elif new_password and new_password == confirm_password:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, '비밀번호가 성공적으로 변경되었습니다.')
            logout(request)  # 로그아웃 처리
            messages.info(request, '다시 로그인 해주세요.')
            return redirect('login')  # 로그아웃 후 로그인 페이지로 리다이렉트
        else:
            messages.error(request, '비밀번호가 일치하지 않습니다.')

    return redirect('mypage')

@login_required(login_url='/login/')
def update_name(request):
    if request.method == 'POST':
        new_name = request.POST.get('new_name')
        if new_name == request.user.name:
            messages.error(request, '새 이름이 기존 이름과 같습니다.')
        elif new_name:
            request.user.name = new_name
            request.user.save()
            messages.success(request, '이름이 성공적으로 변경되었습니다.')

    return redirect('mypage')

@login_required(login_url='/login/')
def update_email(request):
    if request.method == 'POST':
        new_email = request.POST.get('new_email')
        if new_email == request.user.email:
            messages.error(request, '새 이메일이 기존 이메일과 같습니다.')
        elif new_email:
            request.user.email = new_email
            request.user.save()
            messages.success(request, '이메일이 성공적으로 변경되었습니다.')

    return redirect('mypage')

@login_required(login_url='/login/')
def update_address(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        address_detail = request.POST.get('address_detail')

        # 현재 로그인한 사용자의 주소 업데이트
        request.user.address = address
        request.user.address_detail = address_detail
        request.user.save()

        messages.success(request, '주소가 성공적으로 변경되었습니다.')
        return redirect('mypage')

@login_required(login_url='/login/')
def delete_user(request, user_id):
    user = get_object_or_404(Users, id=user_id)  # 유저가 존재하지 않으면 404 에러 발생

    if request.user == user:
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            # 비밀번호 일치 여부 확인
            if password != confirm_password:
                messages.error(request, '비밀번호가 일치하지 않습니다.')
                return redirect('mypage')  # 비밀번호가 일치하지 않으면 마이페이지로 리다이렉트

            # 현재 유저 비밀번호와 비교
            if check_password(password, user.password):
                # 비밀번호가 일치하면 계정 비활성화 처리
                user.is_active = False
                user.delete_at = timezone.now()  # 삭제 시간 기록 (필요 시)
                user.save()
                logout(request)  # 로그아웃 처리
                messages.success(request, '계정이 삭제되었습니다.')
                return redirect('home')  # 성공적으로 비활성화되면 홈 페이지로 리다이렉트
            else:
                messages.error(request, '비밀번호가 틀렸습니다.')
                return redirect('mypage')  # 비밀번호가 틀리면 마이페이지로 리다이렉트
    else:
        messages.error(request, '다른 사용자의 계정을 삭제할 수 없습니다.')
        return redirect('mypage')