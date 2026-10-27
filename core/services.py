"""Automatic lost-and-found matching and email notifications."""
import re
from difflib import SequenceMatcher
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from .models import Item, MatchNotification

MATCH_THRESHOLD = 0.58

def _clean(value):
    return re.sub(r"[^a-z0-9\s]", " ", (value or "").lower()).strip()

def _similarity(first, second):
    a, b = _clean(first), _clean(second)
    if not a or not b:
        return 0.0
    sequence = SequenceMatcher(None, a, b).ratio()
    words_a, words_b = set(a.split()), set(b.split())
    overlap = len(words_a & words_b) / max(1, len(words_a | words_b))
    return max(sequence, overlap)

def score_match(lost_item, found_item):
    """Return a 0..1 score; category must match and name must be meaningfully similar."""
    if lost_item.category != found_item.category:
        return 0.0
    name_score = _similarity(lost_item.name, found_item.name)
    # Require a meaningful name match so generic descriptions do not trigger emails alone.
    if name_score < 0.38:
        return 0.0
    description_score = _similarity(lost_item.description, found_item.description)
    location_score = _similarity(lost_item.location, found_item.location)
    score = (0.55 * name_score) + (0.25 * description_score) + (0.20 * location_score)
    return round(score, 3)

def _owner_email(item):
    # Prefer the contact email supplied with the lost report, then the account email.
    return (item.contact_email or item.reported_by.email or '').strip()

def find_matches_and_notify(found_item):
    """Match a newly reported found item to open lost reports and email likely owners."""
    if found_item.report_type != Item.FOUND or found_item.is_resolved:
        return []

    notifications = []
    candidates = Item.objects.filter(
        report_type=Item.LOST, is_resolved=False, category=found_item.category
    ).exclude(reported_by_id=found_item.reported_by_id).select_related('reported_by')

    for lost_item in candidates:
        score = score_match(lost_item, found_item)
        if score < MATCH_THRESHOLD:
            continue
        recipient = _owner_email(lost_item)
        if not recipient:
            continue

        record, _created = MatchNotification.objects.get_or_create(
            lost_item=lost_item, found_item=found_item,
            defaults={'recipient_email': recipient, 'match_score': score},
        )
        # If delivery failed previously, a later matching run can retry.
        if record.email_sent:
            notifications.append(record)
            continue
        record.recipient_email = recipient
        record.match_score = score
        subject = f'CampusFind: your lost item may have been found - {lost_item.name}'
        message = (
            f"Hello {lost_item.reported_by.first_name or lost_item.reported_by.username},\n\n"
            f"Someone has reported a found item that may match your lost-item report.\n\n"
            f"Your lost item: {lost_item.name}\n"
            f"Category: {lost_item.get_category_display()}\n"
            f"Your reported location: {lost_item.location}\n\n"
            f"Found item description: {found_item.description}\n"
            f"Reported found near: {found_item.location}\n"
            f"Date reported found: {found_item.item_date}\n\n"
            "Please sign in to CampusFind to review the report and contact the finder. "
            "This is a possible match, not confirmation of ownership.\n\n"
            "CampusFind - Helping you find what's lost."
        )
        try:
            sent = send_mail(
                subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                [recipient], fail_silently=False,
            )
            if sent:
                record.email_sent = True
                record.email_sent_at = timezone.now()
                record.save(update_fields=['recipient_email', 'match_score', 'email_sent', 'email_sent_at'])
            else:
                record.save(update_fields=['recipient_email', 'match_score'])
        except Exception:
            # Do not block the user's report submission if email delivery is unavailable.
            record.save(update_fields=['recipient_email', 'match_score'])
        notifications.append(record)
    return notifications
