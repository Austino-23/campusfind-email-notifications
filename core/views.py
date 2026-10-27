from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.dateparse import parse_date
from .models import Item, Claim
from .services import find_matches_and_notify


def home(request):
    recent_items = Item.objects.filter(is_resolved=False)[:3]
    return render(request, 'core/index.html', {'recent_items': recent_items})


def accounts(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    mode = request.POST.get('mode', 'login')
    if request.method == 'POST':
        if mode == 'register':
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip().lower()
            username = email
            password = request.POST.get('password', '')
            confirm = request.POST.get('confirm_password', '')
            if not name or not email or not password:
                messages.error(request, 'Complete all required fields.')
            elif password != confirm:
                messages.error(request, 'The passwords do not match.')
            elif User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                messages.error(request, 'An account with this email already exists. Please log in.')
            else:
                try:
                    validate_password(password)
                except ValidationError as error:
                    for problem in error.messages:
                        messages.error(request, problem)
                else:
                    user = User.objects.create_user(username=username, email=email, password=password, first_name=name)
                    login(request, user)
                    messages.success(request, 'Your account has been created. Welcome to CampusFind!')
                    return redirect('dashboard')
        else:
            email = request.POST.get('email', '').strip().lower()
            password = request.POST.get('password', '')
            user_record = User.objects.filter(Q(username=email) | Q(email=email)).first()
            user = authenticate(request, username=user_record.username, password=password) if user_record else None
            if user:
                login(request, user)
                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}):
                    return redirect(next_url)
                return redirect('dashboard')
            messages.error(request, 'Email or password is incorrect.')
    return render(request, 'core/accounts.html', {'mode': mode, 'next': request.GET.get('next', '')})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been logged out.')
    return redirect('home')

@login_required
def report_item(request):
    if request.method == 'POST':
        name = request.POST.get('item_name', '').strip()
        report_type = request.POST.get('report_type', 'lost')
        category = request.POST.get('category', '')
        location = request.POST.get('location', '').strip()
        item_date = request.POST.get('item_date', '')
        description = request.POST.get('description', '').strip()
        contact_email = request.POST.get('contact_email', '').strip()
        photo = request.FILES.get('photo')
        parsed_date = parse_date(item_date)
        if not all([name, report_type in ('lost', 'found'), category in dict(Item.CATEGORIES), location, parsed_date, description]):
            messages.error(request, 'Please complete all required fields and choose a valid date and category.')
        elif photo and (photo.size > 5 * 1024 * 1024 or photo.content_type not in ('image/jpeg', 'image/png', 'image/webp')):
            messages.error(request, 'Photo must be JPG, PNG, or WEBP and no larger than 5 MB.')
        else:
            item = Item.objects.create(name=name, report_type=report_type, category=category, location=location,
                item_date=parsed_date, description=description, contact_email=contact_email, photo=photo, reported_by=request.user)
            if item.report_type == Item.FOUND:
                matched_notifications = find_matches_and_notify(item)
                sent_count = sum(1 for notification in matched_notifications if notification.email_sent)
                if sent_count:
                    messages.success(request, f'Your report for “{item.name}” has been saved. CampusFind emailed {sent_count} owner(s) about a possible match.')
                else:
                    messages.success(request, f'Your report for “{item.name}” has been saved. No confirmed automatic match was emailed yet.')
            else:
                messages.success(request, f'Your report for “{item.name}” has been saved.')
            return redirect('items')
    return render(request, 'core/report.html', {'categories': Item.CATEGORIES})


def items(request):
    queryset = Item.objects.filter(is_resolved=False)
    q = request.GET.get('q', '').strip()
    report_type = request.GET.get('type', '')
    category = request.GET.get('category', '')
    if q:
        queryset = queryset.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(location__icontains=q))
    if report_type in ('lost', 'found'):
        queryset = queryset.filter(report_type=report_type)
    if category and category in dict(Item.CATEGORIES):
        queryset = queryset.filter(category=category)
    return render(request, 'core/items.html', {'items': queryset, 'q': q, 'selected_type': report_type,
        'selected_category': category, 'categories': Item.CATEGORIES})

@login_required
def dashboard(request):
    if request.user.is_staff:
        my_items = Item.objects.all()[:10]
        claims = Claim.objects.select_related('item', 'claimant').all()[:20]
    else:
        my_items = Item.objects.filter(reported_by=request.user)
        claims = Claim.objects.filter(Q(claimant=request.user) | Q(item__reported_by=request.user)).select_related('item', 'claimant').distinct()
    return render(request, 'core/dashboard.html', {'my_items': my_items, 'claims': claims, 'is_admin': request.user.is_staff})

@login_required
def item_detail(request, item_id):
    """Show a report to staff or to the student who submitted it."""
    item = get_object_or_404(Item, pk=item_id)
    if not (request.user.is_staff or item.reported_by_id == request.user.id):
        messages.error(request, 'You are not allowed to view this report in detail.')
        return redirect('dashboard')
    claims = item.claims.select_related('claimant').all() if request.user.is_staff else item.claims.filter(claimant=request.user)
    return render(request, 'core/item_detail.html', {
        'item': item,
        'claims': claims,
        'is_admin': request.user.is_staff,
    })


@login_required
def claim_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id, is_resolved=False)
    if item.reported_by_id == request.user.id:
        messages.error(request, 'You cannot submit a claim on your own report.')
    elif request.method == 'POST':
        message = request.POST.get('message', '').strip()
        if len(message) < 10:
            messages.error(request, 'Please add at least 10 characters explaining why you believe this item is yours.')
        else:
            try:
                Claim.objects.create(item=item, claimant=request.user, message=message)
                messages.success(request, 'Your claim has been submitted to the person who reported the item.')
            except IntegrityError:
                messages.info(request, 'You have already submitted a claim for this item.')
    return redirect('items')

@login_required
def update_claim(request, claim_id):
    claim = get_object_or_404(Claim, pk=claim_id)
    if request.method == 'POST' and (request.user.is_staff or claim.item.reported_by_id == request.user.id):
        status = request.POST.get('status')
        if status in ('approved', 'rejected', 'pending'):
            claim.status = status
            claim.save(update_fields=['status'])
            messages.success(request, 'Claim status updated.')
    else:
        messages.error(request, 'You are not allowed to update this claim.')
    return redirect('dashboard')

@login_required
def resolve_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if request.method == 'POST' and (request.user.is_staff or item.reported_by_id == request.user.id):
        item.is_resolved = not item.is_resolved
        item.save(update_fields=['is_resolved'])
        messages.success(request, 'Item status updated.')
    else:
        messages.error(request, 'You are not allowed to change this item.')
    return redirect('dashboard')

@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if request.method == 'POST' and (request.user.is_staff or item.reported_by_id == request.user.id):
        item.delete()
        messages.success(request, 'Report deleted.')
    else:
        messages.error(request, 'You are not allowed to delete this report.')
    return redirect('dashboard')
