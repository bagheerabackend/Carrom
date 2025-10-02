from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from Matches.models import Matches
from Player.models import Player
from Transactions.models import TransactionLog
from Games.models import Game
from Settings.models import AppSettings

User = get_user_model()

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password')
        return redirect('admin_login') 
    return render(request, 'login.html')

@login_required(login_url='admin_login')
def admin_logout(request):
    logout(request)
    return redirect("admin_login")

@login_required(login_url='admin_login')
def dashboard_view(request):
    total_players = Player.objects.count()
    total_matches_completed = Matches.objects.filter(status='completed').count()
    total_amount_won = Matches.objects.filter(status='completed').aggregate(total_amount=Sum('winning_amount'))['total_amount'] or 0
    context = {
        'total_players': total_players,
        'total_matches_completed': total_matches_completed,
        'total_amount_won': total_amount_won,
    }
    return render(request, 'dashboard.html', context)

@login_required(login_url='admin_login')
@require_http_methods(["GET"])
def dashboard_data(request):
    last_credit_transactions = TransactionLog.objects.filter(transaction_type="credit").values("user__name", "amount")[:3]
    last_debit_transactions = TransactionLog.objects.filter(transaction_type="debit").values("user__name", "amount")[:3]
    new_players = Player.objects.order_by("-id").values("name", "created_at")[:3]
    ongoing_matches = Matches.objects.filter(status="full").order_by("-id").values("player1__name", "player2__name")[:3]
    response_data = {
        'success': True,
        'credit_transactions': list(last_credit_transactions),
        'debit_transactions': list(last_debit_transactions),
        'new_players': list(new_players),
        'ongoing_matches': list(ongoing_matches)
    }
    return JsonResponse(response_data, safe=False)

@login_required(login_url='admin_login')
def player_view(request):
    context = {}
    return render(request, "players.html", context)

@login_required(login_url='admin_login')
@require_http_methods(["GET"])
def player_data(request):
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search_value = request.GET.get('search_value')
    sort_by = request.GET.get('sort_by', 'player_id')
    sort_order = '' if request.GET.get('sort_order') == 'asc' else '-'
    status = request.GET.get('status')
    q = Q()
    if status:
        q &= Q(is_blocked=True) if status == "blocked" else Q(is_blocked=False)
    if search_value:
        q &= (Q(name__icontains=search_value) | Q(phone__icontains=search_value) | Q(player_id__icontains=search_value))
    players = Player.objects.filter(q).order_by(f'{sort_order}{sort_by}')
    paginator = Paginator(players, per_page)
    page_obj = paginator.get_page(page)
    players_list = list(page_obj.object_list.values('id', 'player_id', 'name', 'email', 'phone', 'age', 'coin', 'withdrawable_coin', 'bonus', 'is_blocked', 'created_at'))
    response_data = {
        'total': paginator.count,
        'players': players_list,
        'current_page': page_obj.number,
        'per_page': per_page,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
    }
    return JsonResponse(response_data, safe=False)
    
@login_required(login_url='admin_login')
def block_player(request, player_id):
    if Player.objects.filter(id=player_id).exists():
        player = Player.objects.get(id=player_id)
        player.is_blocked = not player.is_blocked
        player.save()
        return JsonResponse("Success", safe=False)
    return JsonResponse({"message": "error"})

@login_required(login_url='admin_login')
def delete_player(request, player_id):
    if Player.objects.filter(id=player_id).exists():
        Player.objects.get(id=player_id).delete()
        return JsonResponse("Success", safe=False)
    return JsonResponse({"message": "error"})
    
@login_required(login_url='admin_login')
def matches_comp_view(request):
    context = {}
    return render(request, "matches_completed.html", context)

@login_required(login_url='admin_login')
@require_http_methods(["GET"])
def matches_comp_data(request):
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search_value = request.GET.get('search_value')
    sort_by = request.GET.get('sort_by', 'id')
    sort_order = '' if request.GET.get('sort_order') == 'asc' else '-'
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    q = Q(status='completed', game__type='cash')
    if search_value:
        q &= (Q(player1__name__icontains=search_value) | Q(player1__phone__icontains=search_value) | Q(player2__name__icontains=search_value) | Q(player2__phone__icontains=search_value))
    if from_date and to_date:
        to_date_str = datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1)
        q &= Q(created_at__range=[from_date, to_date_str])
    else:
        today = timezone.now().date()
        q &= Q(created_at__date=today)
    matches = Matches.objects.filter(q).order_by(f'{sort_order}{sort_by}')
    paginator = Paginator(matches, per_page)
    page_obj = paginator.get_page(page)
    match_list = list(page_obj.object_list.values('id', 'player1__name', 'player1__phone', 'player2__name', 'player2__phone', 'winner__name', 'winner__phone', 'winning_amount', 'game__name', 'commission_amount', 'created_at'))
    context = {
        'from_date': from_date,
        'to_date': to_date,
        'total': paginator.count,
        'matches': match_list,
        'current_page': page_obj.number,
        'per_page': per_page,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
    }
    return JsonResponse(context, safe=False)

@login_required(login_url='admin_login')
def matches_ong_view(request):
    context = {}
    return render(request, "matches_ongoing.html", context)

@login_required(login_url='admin_login')
@require_http_methods(["GET"])
def matches_ong_data(request):
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search_value = request.GET.get('search_value')
    sort_by = request.GET.get('sort_by', 'id')
    sort_order = '' if request.GET.get('sort_order') == 'asc' else '-'
    q = Q(status='full', game__type='cash')
    if search_value:
        q &= (Q(player1__name__icontains=search_value) | Q(player1__phone__icontains=search_value) | Q(player2__name__icontains=search_value) | Q(player2__phone__icontains=search_value))
    matches = Matches.objects.filter(q).order_by(f'{sort_order}{sort_by}')
    paginator = Paginator(matches, per_page)
    page_obj = paginator.get_page(page)
    match_list = list(page_obj.object_list.values('id', 'player1__name', 'player1__phone', 'player2__name', 'player2__phone', 'game__name', 'commission_amount', 'created_at'))
    context = {
        'total': paginator.count,
        'matches': match_list,
        'current_page': page_obj.number,
        'per_page': per_page,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
    }
    return JsonResponse(context, safe=False)
    
@login_required(login_url='admin_login')
def bonus_games_view(request):
    context={}
    return render(request, "bonus_matches.html", context)
    
@login_required(login_url='admin_login')
def bonus_games_data(request):
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search_value = request.GET.get('search_value')
    sort_by = request.GET.get('sort_by', 'id')
    sort_order = '' if request.GET.get('sort_order') == 'asc' else '-'
    q = Q(status__in=['completed', 'full'], game__type='bonus')
    if search_value:
        q &= (Q(player1__name__icontains=search_value) | Q(player1__phone__icontains=search_value) | Q(player2__name__icontains=search_value) | Q(player2__phone__icontains=search_value))
    matches = Matches.objects.filter(q).order_by(f'{sort_order}{sort_by}')
    paginator = Paginator(matches, per_page)
    page_obj = paginator.get_page(page)
    match_list = list(page_obj.object_list.values('id', 'player1__name', 'player1__phone', 'player2__name', 'player2__phone', 'winner__name', 'winner__phone', 'winning_amount', 'game__name', 'commission_amount', 'created_at', 'status'))
    context = {
        'total': paginator.count,
        'matches': match_list,
        'current_page': page_obj.number,
        'per_page': per_page,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
    }
    return JsonResponse(context, safe=False)
    
@login_required(login_url='admin_login')
def games_view(request):
    context = {}
    return render(request, "games.html", context)

@login_required(login_url='admin_login')
@require_http_methods(["GET"])
def games_data(request):
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search_value = request.GET.get('search_value')
    sort_by = request.GET.get('sort_by', 'id')
    type = request.GET.get('type')
    status = request.GET.get('status')
    sort_order = '' if request.GET.get('sort_order') == 'asc' else '-'
    q = Q()
    if search_value:
        q &= (Q(game__name__icontains=search_value))
    if type:
        q &= Q(type=type)
    if status:
        q &= Q(is_active=True) if status == "active" else Q(is_active=False)
    games = Game.objects.filter(q).order_by(f'{sort_order}{sort_by}')
    paginator = Paginator(games, per_page)
    page_obj = paginator.get_page(page)
    game_list = []
    for game in page_obj.object_list:
        game_list.append({
            'id': game.id,
            'name': game.name,
            'image': game.image.url if game.image else '',
            'fee': game.fee,
            'winning_amount': game.winning_amount,
            'is_active': game.is_active,
            'created_at': game.created_at,
            'type': game.type
        })
    context = {
        'total': paginator.count,
        'games': game_list,
        'current_page': page_obj.number,
        'per_page': per_page,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
    }
    return JsonResponse(context, safe=False)

@login_required(login_url='admin_login')
@require_http_methods(["POST"])
def add_game(request):
    name = request.POST.get('name')
    image = request.FILES.get('image')
    fee = request.POST.get('fee')
    winning_amount = request.POST.get('winning_amount')
    game = Game(name=name, image=image, fee=fee, winning_amount=winning_amount)
    game.save()
    return JsonResponse("Success", safe=False)

@login_required(login_url='admin_login')
@require_http_methods(["POST"])
def edit_game(request, id):
    if Game.objects.filter(id=id).exists():
        game = Game.objects.get(id=id)
        game.name = request.POST.get('name', game.name)
        game.image = request.FILES.get('image', game.image.url)
        game.fee = request.POST.get('fee', game.fee)
        game.winning_amount = request.POST.get('winning_amount', game.winning_amount)
        game.save()
        return JsonResponse("Success", safe=False)
    return JsonResponse({"message": "error"})

@login_required(login_url='admin_login')
def delete_game(request, id):
    if Game.objects.filter(id=id).exists():
        game = Game.objects.get(id=id)
        game.delete()
        return JsonResponse("Success", safe=False)
    return JsonResponse({"message": "error"})

@login_required(login_url='admin_login')
def block_game(request, id):
    if Game.objects.filter(id=id).exists():
        game = Game.objects.get(id=id)
        game.is_active = not game.is_active
        game.save()
        return JsonResponse("Success", safe=False)
    return JsonResponse({"message": "error"})

@login_required(login_url='admin_login')
def commission_view(request):
    context = {}
    return render(request, "commission.html", context)

@login_required(login_url='admin_login')
@require_http_methods(["GET"])
def commission_data(request):
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search_value = request.GET.get('search_value')
    sort_by = request.GET.get('sort_by', 'id')
    sort_order = '' if request.GET.get('sort_order') == 'asc' else '-'
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    today = timezone.now().date()
    q = Q(status='completed', game__type='cash')
    if search_value:
        q &= (Q(winner__name__icontains=search_value) | Q(winner__phone__icontains=search_value))
    if from_date and to_date:
        to_date_str = datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1)
        q &= Q(created_at__range=[from_date, to_date_str])
    else:
        q &= Q(created_at__date=today)
    commission = Matches.objects.filter(q).order_by(f'{sort_order}{sort_by}')
    paginator = Paginator(commission, per_page)
    page_obj = paginator.get_page(page)
    commission_list = list(page_obj.object_list.values('id', 'winner__name', 'winner__phone', 'winning_amount', 'game__name', 'commission_amount', 'created_at'))
    todays_total_commission = Matches.objects.filter(status='completed', game__type='cash', created_at__date=today).aggregate(total_commission=Sum('commission_amount'))
    start_of_month = today.replace(day=1)
    monthly_total_commission = Matches.objects.filter(status='completed', game__type='cash', created_at__date__gte=start_of_month, created_at__date__lte=today).aggregate(total_commission=Sum('commission_amount'))
    start_of_year = today.replace(month=1, day=1)
    yearly_total_commission = Matches.objects.filter(status='completed', game__type='cash', created_at__date__gte=start_of_year, created_at__date__lte=today).aggregate(total_commission=Sum('commission_amount'))
    context = {
        'from_date': from_date,
        'to_date': to_date,
        'total': paginator.count,
        'matches': commission_list,
        'current_page': page_obj.number,
        'per_page': per_page,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'todays_total_commission': todays_total_commission.get('total_commission') or 0,
        'monthly_total_commission': monthly_total_commission.get('total_commission') or 0,
        'yearly_total_commission': yearly_total_commission.get('total_commission') or 0,
    }
    return JsonResponse(context, safe=False)

@login_required(login_url='admin_login')
def credit_trans_view(request):
    context = {}
    return render(request, "credits.html", context)

@login_required(login_url='admin_login')
@require_http_methods(["GET"])
def credit_trans_data(request):
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search_value = request.GET.get('search_value')
    sort_by = request.GET.get('sort_by', 'id')
    sort_order = '' if request.GET.get('sort_order') == 'asc' else '-'
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    today = timezone.now().date()
    q = Q(transaction_type="credit")
    if search_value:
        q &= (Q(user__name__icontains=search_value) | Q(user__phone__icontains=search_value))
    if from_date and to_date:
        to_date_str = datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1)
        q &= Q(transaction_at__range=[from_date, to_date_str])
    else:
        q &= Q(transaction_at__date=today)
    credits = TransactionLog.objects.filter(q).order_by(f'{sort_order}{sort_by}')
    paginator = Paginator(credits, per_page)
    page_obj = paginator.get_page(page)
    credits_list = list(page_obj.object_list.values('id', 'user__name', 'user__phone', 'amount', 'gst_deduct', 'balance_after', 'transaction_at'))
    todays_total_credit = TransactionLog.objects.filter(transaction_type="credit", transaction_at__date=today).aggregate(total_credit=Sum('amount'), total_gst=Sum('gst_deduct'), total_balance_transferred=Sum('balance_after'))
    start_of_month = today.replace(day=1)
    monthly_total_credit = TransactionLog.objects.filter(transaction_type="credit", transaction_at__date__gte=start_of_month, transaction_at__date__lte=today).aggregate(total_credit=Sum('amount'), total_gst=Sum('gst_deduct'), total_balance_transferred=Sum('balance_after'))
    start_of_year = today.replace(month=1, day=1)
    yearly_total_credit = TransactionLog.objects.filter(transaction_type="credit", transaction_at__date__gte=start_of_year, transaction_at__date__lte=today).aggregate(total_credit=Sum('amount'), total_gst=Sum('gst_deduct'), total_balance_transferred=Sum('balance_after'))
    context = {
        'from_date': from_date,
        'to_date': to_date,
        'total': paginator.count,
        'credits': credits_list,
        'current_page': page_obj.number,
        'per_page': per_page,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'today_credits': todays_total_credit,
        'monthly_credits': monthly_total_credit,
        'yearly_credits': yearly_total_credit,
    }
    return JsonResponse(context, safe=False)

@login_required(login_url='admin_login')
def debit_trans_view(request):
    context = {}
    return render(request, "debits.html", context)

@login_required(login_url='admin_login')
@require_http_methods(["GET"])
def debit_trans_data(request):
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search_value = request.GET.get('search_value')
    sort_by = request.GET.get('sort_by', 'id')
    sort_order = '' if request.GET.get('sort_order') == 'asc' else '-'
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    today = timezone.now().date()
    q = Q(transaction_type="debit")
    if search_value:
        q &= (Q(user__name__icontains=search_value) | Q(user__phone__icontains=search_value))
    if from_date and to_date:
        to_date_str = datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1)
        q &= Q(transaction_at__range=[from_date, to_date_str])
    else:
        q &= Q(transaction_at__date=today)
    debits = TransactionLog.objects.filter(q).order_by(f'{sort_order}{sort_by}')
    paginator = Paginator(debits, per_page)
    page_obj = paginator.get_page(page)
    debits_list = list(page_obj.object_list.values('id', 'user__name', 'user__phone', 'amount', 'gst_deduct', 'balance_after', 'transaction_at'))
    todays_total_debit = TransactionLog.objects.filter(transaction_type="debit", transaction_at__date=today).aggregate(total_debit=Sum('amount'), total_gst=Sum('gst_deduct'), total_balance_transferred=Sum('balance_after'))
    start_of_month = today.replace(day=1)
    monthly_total_debit = TransactionLog.objects.filter(transaction_type="debit", transaction_at__date__gte=start_of_month, transaction_at__date__lte=today).aggregate(total_debit=Sum('amount'), total_gst=Sum('gst_deduct'), total_balance_transferred=Sum('balance_after'))
    start_of_year = today.replace(month=1, day=1)
    yearly_total_debit = TransactionLog.objects.filter(transaction_type="debit", transaction_at__date__gte=start_of_year, transaction_at__date__lte=today).aggregate(total_debit=Sum('amount'), total_gst=Sum('gst_deduct'), total_balance_transferred=Sum('balance_after'))
    context = {
        'from_date': from_date,
        'to_date': to_date,
        'total': paginator.count,
        'debits': debits_list,
        'current_page': page_obj.number,
        'per_page': per_page,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'today_debits': todays_total_debit,
        'monthly_debits': monthly_total_debit,
        'yearly_debits': yearly_total_debit,
    }
    return JsonResponse(context, safe=False)

@login_required(login_url='admin_login')
def app_settings_view(request):
    setting = AppSettings.objects.last()
    if setting:
        context = {
            'add': False,
            'version': setting.version,
            'maintenance_mode': 'In Maintenance' if setting.maintenance_mode else 'Not In Maintenance',
            'maintenance_message': setting.maintenance_message or 'N/A',
            'gst_percentage': setting.gst_percentage,
            'tds_percentage': setting.tds_percentage,
            'bonus_point': setting.bonus_point,
            'withdrawal_limit': setting.withdrawal_limit,
            'daily_withdraw_count': setting.daily_withdraw_count,
        }
    else:
        context = {
            'add': True,
        }
    return render(request, "app_settings.html", context)

@login_required(login_url='admin_login')
@require_http_methods(["POST"])
def add_setting(request):
    version = request.POST.get('version')
    maintenance_mode = True if request.POST.get('maintenance_mode') == 'true' else False
    maintenance_message = request.POST.get('maintenance_message')
    gst_percentage = request.POST.get('gst_percentage')
    tds_percentage = request.POST.get('tds_percentage')
    bonus_point = request.POST.get('bonus_point')
    withdrawal_limit = request.POST.get('withdrawal_limit')
    daily_withdraw_count = request.POST.get('daily_withdraw_count')
    setting = AppSettings(
        version = version,
        maintenance_mode = maintenance_mode,
        maintenance_message = maintenance_message,
        gst_percentage = gst_percentage,
        tds_percentage = tds_percentage,
        bonus_point = bonus_point,
        withdrawal_limit = withdrawal_limit,
        daily_withdraw_count = daily_withdraw_count,
    )
    setting.save()
    return JsonResponse("Success", safe=False)

@login_required(login_url='admin_login')
@require_http_methods(["POST"])
def edit_setting(request, id):
    if AppSettings.objects.filter(id=id).exists():
        setting = AppSettings.objects.get(id=id)
        setting.version = request.POST.get('version', setting.version)
        setting.maintenance_mode = request.POST.get('maintenance_mode', setting.maintenance_mode)
        setting.maintenance_message = request.POST.get('maintenance_message', setting.maintenance_message)
        setting.gst_percentage = request.POST.get('gst_percentage', setting.gst_percentage)
        setting.tds_percentage = request.POST.get('gst_percentage', setting.tds_percentage)
        setting.bonus_point = request.POST.get('bonus_point', setting.bonus_point)
        setting.withdrawal_limit = request.POST.get('withdrawal_limit', setting.withdrawal_limit)
        setting.daily_withdraw_count = request.POST.get('daily_withdraw_count', setting.daily_withdraw_count)
        setting.save()
        return JsonResponse("Success", safe=False)
    return JsonResponse({"message": "error"})