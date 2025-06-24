from django.contrib import admin
from .models import (
    Profile,
    Collection,
    Channel,
    Follow,
    Bookmark,
    Notification,
    Subscription,
    MutedUser,
)

class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'video', 'created_at')
    search_fields = (
        'user__username',
        'video__title',
        'title',
        'description',
        'tags__name',
    )

admin.site.register(Profile)
admin.site.register(Collection)
admin.site.register(Channel)
admin.site.register(Follow)
admin.site.register(Bookmark, BookmarkAdmin)
admin.site.register(Notification)
admin.site.register(Subscription)
admin.site.register(MutedUser)
