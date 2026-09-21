from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Story, StoryImage


class StoryImageInline(admin.TabularInline):
    model = StoryImage
    extra = 1
    fields = ('image', 'caption', 'uploaded_at')
    readonly_fields = ('uploaded_at',)


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'destination', 
        'author_name', 
        'status_badge', 
        'photo_count', 
        'is_featured', 
        'published_at',
        'moderation_actions'
    )
    list_filter = ('status', 'is_featured', 'destination', 'created_at')
    search_fields = ('title', 'bangla_title', 'author_name', 'author_email', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_featured',)
    inlines = [StoryImageInline]
    actions = ['approve_selected_stories', 'reject_selected_stories']

    fieldsets = (
        ('গল্পের তথ্য (Story Information)', {
            'fields': ('title', 'bangla_title', 'slug', 'destination', 'content', 'excerpt', 'cover_image')
        }),
        ('লেখক ও অনুমোদন (Author & Moderation)', {
            'fields': ('author_name', 'author_email', 'status', 'is_featured', 'read_time', 'published_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        """Admins can write and publish their own stories directly without requiring approval."""
        if not change and not obj.status:
            obj.status = Story.STATUS_APPROVED
        super().save_model(request, obj, form, change)

    @admin.display(description='স্ট্যাটাস (Status)')
    def status_badge(self, obj):
        if obj.status == Story.STATUS_APPROVED:
            return format_html(
                '<span style="background:#10b981; color:#fff; padding:3px 8px; border-radius:12px; font-weight:bold; font-size:11px;">'
                '✓ অনুমোদিত (Approved)</span>'
            )
        elif obj.status == Story.STATUS_PENDING:
            return format_html(
                '<span style="background:#f59e0b; color:#fff; padding:3px 8px; border-radius:12px; font-weight:bold; font-size:11px;">'
                '⏳ অপেক্ষমাণ (Pending)</span>'
            )
        else:
            return format_html(
                '<span style="background:#ef4444; color:#fff; padding:3px 8px; border-radius:12px; font-weight:bold; font-size:11px;">'
                '✕ বাতিল (Rejected)</span>'
            )

    @admin.display(description='ছবি (Photos)')
    def photo_count(self, obj):
        count = obj.images.count()
        return f"{count}টি ছবি" if count > 0 else "—"

    @admin.display(description='অ্যাকশন (Actions)')
    def moderation_actions(self, obj):
        preview_url = reverse('stories:detail', kwargs={'slug': obj.slug}) if obj.slug else '#'
        approve_url = reverse('stories:moderate', kwargs={'story_id': obj.pk, 'action': 'approve'})
        reject_url = reverse('stories:moderate', kwargs={'story_id': obj.pk, 'action': 'reject'})

        buttons = [
            f'<a href="{preview_url}" target="_blank" style="margin-right:6px; text-decoration:none;" title="ওয়েবসাইটে দেখুন">👁️ প্রিভিউ</a>'
        ]
        if obj.status != Story.STATUS_APPROVED:
            buttons.append(
                f'<a href="{approve_url}" style="color:#059669; font-weight:bold; margin-right:6px; text-decoration:none;">✓ অনুমোদন</a>'
            )
        if obj.status != Story.STATUS_REJECTED:
            buttons.append(
                f'<a href="{reject_url}" style="color:#dc2626; font-weight:bold; text-decoration:none;">✕ বাতিল</a>'
            )

        return format_html(" ".join(buttons))

    @admin.action(description='নির্বাচিত গল্পগুলো অনুমোদন করুন (Approve Selected)')
    def approve_selected_stories(self, request, queryset):
        updated = queryset.update(status=Story.STATUS_APPROVED)
        self.message_user(request, f"{updated}টি ভ্রমণ গল্প অনুমোদিত হয়েছে এবং লাইভ ওয়েবসাইটে প্রকাশিত হয়েছে।")

    @admin.action(description='নির্বাচিত গল্পগুলো বাতিল করুন (Reject Selected)')
    def reject_selected_stories(self, request, queryset):
        updated = queryset.update(status=Story.STATUS_REJECTED)
        self.message_user(request, f"{updated}টি গল্প বাতিল করা হয়েছে।")

