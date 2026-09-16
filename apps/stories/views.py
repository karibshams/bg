from django.shortcuts import render, get_object_or_404
from .models import Story

def story_list_view(request):
    """Lists all published travel stories."""
    stories = Story.objects.select_related('destination').all()
    featured_story = stories.filter(is_featured=True).first() or stories.first()
    other_stories = stories.exclude(id=featured_story.id) if featured_story else stories

    return render(request, 'stories/list.html', {
        'featured_story': featured_story,
        'stories': other_stories,
    })


def story_detail_view(request, slug):
    """Renders single travel article with related reads."""
    story = get_object_or_404(Story.objects.select_related('destination'), slug=slug)
    related_stories = Story.objects.exclude(id=story.id)[:3]

    return render(request, 'stories/detail.html', {
        'story': story,
        'related_stories': related_stories,
    })
