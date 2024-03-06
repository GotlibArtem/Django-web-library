from celery.schedules import crontab
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from ...models import Store_Fiction_Book


@shared_task
def send_reminder_emails():
    """
    Функция для отправки напоминаний о возврате книг.
    """
    # Получаем все экземпляры книг.
    fiction_books = Store_Fiction_Book.objects.all()

    # Проверяем, просрочена ли дата возврата для каждой книги.
    today = timezone.now().date()
    for book in fiction_books:
        if not book.return_day and today >= book.planned_return_day:
        # Отправляем письмо на почту пользователя.
        send_mail(
            subject='Напоминание о возврате книги',
            message=f'Уважаемый(ая) {book.reader.first_name} {book.reader.last_name}!\n\n' +
                    f'Просим Вас вернуть книгу "{book.book.book_name}".\n\n' +
                    'Спасибо за сотрудничество!',
            from_email='ag@dpi4.com',
            recipient_list=[book.reader.email],
        )


# Запланируйте задачу на отправку писем в 10:00 каждый день.
beat_schedule = {
  'send-reminder-emails': {
    'task': 'send_reminder_emails',
    'schedule': crontab(minute=40, hour=13),
  },
}
