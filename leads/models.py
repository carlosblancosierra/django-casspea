\
from django.db import models

class Lead(models.Model):
    NEWSLETTER = 'newsletter'
    CONTACT_FORM = 'contact_form'

    LEAD_TYPES = (
        (NEWSLETTER, 'Newsletter Subscriber'),
        (CONTACT_FORM, 'Contact Form'),
    )

    email = models.EmailField()

    lead_type = models.CharField(max_length=100, choices=LEAD_TYPES)
    unsubscribed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email}"
