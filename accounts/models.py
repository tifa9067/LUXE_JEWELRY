from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    USER_TYPE_CHOICES = (
        ('customer', 'عميل'),
        ('admin', 'مدير'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, verbose_name='رقم الهاتف')
    address = models.TextField(blank=True, verbose_name='العنوان')
    city = models.CharField(max_length=100, blank=True, verbose_name='المدينة')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer', verbose_name='نوع المستخدم')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"
    
    class Meta:
        verbose_name = 'ملف شخصي'
        verbose_name_plural = 'الملفات الشخصية'

# إشارة لإنشاء Profile تلقائياً عند إنشاء User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()