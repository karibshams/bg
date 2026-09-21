from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from apps.tours.models import Destination
from .models import Story, StoryImage


def story_list_view(request):
    """Lists all approved travel stories on the public website."""
    stories = Story.objects.filter(status=Story.STATUS_APPROVED).select_related('destination')
    featured_story = stories.filter(is_featured=True).first() or stories.first()
    other_stories = stories.exclude(id=featured_story.id) if featured_story else stories

    return render(request, 'stories/list.html', {
        'featured_story': featured_story,
        'stories': other_stories,
    })


def story_submit_view(request):
    """
    Public 'Share Your Story' submission form.
    User submissions are saved with 'pending' status and remain hidden from
    the website until approved by an admin.
    Fields: Title, Destination Tag, Description, and photo uploads (max 10 photos).
    """
    destinations = Destination.objects.all().order_by('order', 'name')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        destination_id = request.POST.get('destination', '').strip()
        author_name = request.POST.get('author_name', '').strip() or 'Anonymous Traveler'
        author_email = request.POST.get('author_email', '').strip()
        content = request.POST.get('content', '').strip()
        photos = request.FILES.getlist('photos')

        # Form Validation
        errors = []
        if not title:
            errors.append("গল্পের একটি আকর্ষণীয় শিরোনাম দিন।")
        if not content:
            errors.append("আপনার ভ্রমণের রোমাঞ্চকর অভিজ্ঞতা বা বিবরণ লিখুন।")
        if len(photos) > 10:
            errors.append("সর্বোচ্চ ১০টি ছবি আপলোড করা যাবে (Maximum 10 photos allowed).")

        dest_obj = None
        if destination_id:
            try:
                dest_obj = Destination.objects.get(id=destination_id)
            except Destination.DoesNotExist:
                pass

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'stories/submit.html', {
                'destinations': destinations,
                'title': title,
                'author_name': author_name,
                'author_email': author_email,
                'content': content,
                'selected_dest': destination_id,
            })

        # Calculate approximate reading time
        words_count = len(content.split())
        calc_min = max(2, round(words_count / 140))
        read_time_str = f"{calc_min} min read"

        # Create story with PENDING status (hidden from public site)
        story = Story(
            title=title,
            destination=dest_obj,
            author_name=author_name,
            author_email=author_email,
            read_time=read_time_str,
            content=content,
            status=Story.STATUS_PENDING,
            is_featured=False,
        )

        if photos:
            story.cover_image = photos[0]

        story.save()

        # Save all attached photos (up to 10 photos)
        for photo in photos[:10]:
            StoryImage.objects.create(story=story, image=photo)

        messages.success(
            request, 
            "ধন্যবাদ! আপনার ভ্রমণ গল্পটি সফলভাবে জমা হয়েছে। অ্যাডমিন পর্যালোচনার পর এটি ওয়েবসাইটে প্রদর্শিত হবে।"
        )
        return render(request, 'stories/submit_success.html', {
            'story': story,
        })

    return render(request, 'stories/submit.html', {
        'destinations': destinations,
    })


def story_detail_view(request, slug):
    """Renders single travel article. Pending stories visible to staff only."""
    story = get_object_or_404(Story.objects.select_related('destination'), slug=slug)

    # Hidden from public if not approved, unless viewing by staff/admin
    if story.status != Story.STATUS_APPROVED and not request.user.is_staff:
        raise Http404("এই গল্পটি এখনও পর্যালোচনায় রয়েছে বা অনুমোদিত হয়নি।")

    related_stories = Story.objects.filter(status=Story.STATUS_APPROVED).exclude(id=story.id)[:3]
    photos = story.images.all()

    return render(request, 'stories/detail.html', {
        'story': story,
        'related_stories': related_stories,
        'photos': photos,
    })


@staff_member_required
def story_moderate_action(request, story_id, action):
    """Admin quick action to approve or reject a story."""
    story = get_object_or_404(Story, pk=story_id)
    if action == 'approve':
        story.status = Story.STATUS_APPROVED
        story.save()
        messages.success(request, f"গল্প '{story.title}' সফলভাবে অনুমোদিত হয়েছে এবং লাইভ ওয়েবসাইটে প্রকাশিত হয়েছে।")
    elif action == 'reject':
        story.status = Story.STATUS_REJECTED
        story.save()
        messages.warning(request, f"গল্প '{story.title}' বাতিল (Rejected) করা হয়েছে।")

    next_url = request.GET.get('next', '/admin/stories/story/')
    return redirect(next_url)
