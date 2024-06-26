from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from pages.models import Page
from pages.admin import PageAdmin
from registration.models import UserProfile
from registration.admin import UserProfileAdmin


class MyUserAdmin(UserAdmin):
    # override the default sort column
    ordering = ('-date_joined', )
    # if you want the date they joined or other columns displayed in the list,
    # override list_display too
    list_display = ('username', 'email', 'date_joined', 'first_name', 'last_name', 'is_staff')


publisher_admin = AdminSite('pageadmin')
publisher_admin.register(Page, PageAdmin)
#publisher_admin.unregister(User)
publisher_admin.register(User, MyUserAdmin)
#publisher_admin.register(User, UserAdmin)
publisher_admin.register(UserProfile, UserProfileAdmin)
