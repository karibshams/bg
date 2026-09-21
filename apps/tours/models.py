from django.db import models
from django.utils.text import slugify

class Destination(models.Model):
    """Tourist destination like Sajek, Bandarban, Cox's Bazar, Sundarbans."""
    name = models.CharField(max_length=150)
    bangla_name = models.CharField(max_length=150, blank=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    tagline = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='destinations/covers/', blank=True, null=True)
    is_featured = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Destination"
        verbose_name_plural = "Destinations"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.bangla_name})" if self.bangla_name else self.name


class TourCategory(models.Model):
    """Tour category e.g. Mountain, Beach, Forest, Adventure, Heritage."""
    name = models.CharField(max_length=100)
    bangla_name = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    icon = models.CharField(max_length=50, blank=True, default="compass", help_text="Lucide/SVG icon name or emoji")

    class Meta:
        ordering = ['name']
        verbose_name = "Tour Category"
        verbose_name_plural = "Tour Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tour(models.Model):
    """Main travel package managed by admin."""
    title = models.CharField(max_length=255)
    bangla_title = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=260, unique=True, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='tours')
    category = models.ForeignKey(TourCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='tours')
    
    duration = models.CharField(max_length=80, default="3 Days / 2 Nights")
    duration_days = models.PositiveSmallIntegerField(default=3, help_text="Number of days for filtering")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in BDT (৳)")
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_travelers = models.PositiveIntegerField(default=20)
    
    short_description = models.TextField(help_text="Short teaser for cards and search results")
    description = models.TextField(help_text="Full itinerary and overview")
    cover_image = models.ImageField(upload_to='tours/covers/', blank=True, null=True)
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo preview link")
    
    included_items = models.TextField(blank=True, help_text="What is included (one item per line)")
    excluded_items = models.TextField(blank=True, help_text="What is not included (excluded) (one item per line)")
    
    badge_text = models.CharField(max_length=50, blank=True, default="Featured", help_text="e.g. Popular, Hot Deal")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.9)
    reviews_count = models.PositiveIntegerField(default=12)
    
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name = "Tour"
        verbose_name_plural = "Tours"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.price

    def get_included_list(self):
        """Returns unified list of included items from model field & inline objects."""
        items = []
        if self.included_items:
            items.extend([line.strip() for line in self.included_items.splitlines() if line.strip()])
        items.extend([i.item for i in self.inclusions.filter(is_included=True)])
        return items

    def get_excluded_list(self):
        """Returns unified list of excluded items from model field & inline objects."""
        items = []
        if self.excluded_items:
            items.extend([line.strip() for line in self.excluded_items.splitlines() if line.strip()])
        items.extend([i.item for i in self.inclusions.filter(is_included=False)])
        return items

    def __str__(self):
        return f"{self.title} (৳{self.current_price:,.0f})"


class TourDate(models.Model):
    """Available batch or departure dates for a tour."""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='dates')
    start_date = models.DateField()
    end_date = models.DateField()
    total_capacity = models.PositiveIntegerField(default=40, help_text="Total batch capacity (e.g., 40 seats)")
    available_seats = models.PositiveIntegerField(default=40, help_text="Remaining available seats")
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['start_date']
        verbose_name = "Tour Departure Date"
        verbose_name_plural = "Tour Departure Dates"

    @property
    def effective_price(self):
        if self.price_override:
            return self.price_override
        return self.tour.current_price

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.total_capacity == 40 and self.available_seats != 40:
                self.total_capacity = self.available_seats
            elif self.total_capacity != 40 and self.available_seats == 40:
                self.available_seats = self.total_capacity
        super().save(*args, **kwargs)

    def update_available_seats(self):
        """Recalculate real-time seat availability: Available = Total Capacity - Confirmed Bookings."""
        confirmed_seats = self.bookings.filter(status='CONFIRMED').aggregate(
            total=models.Sum('num_travelers')
        )['total'] or 0
        self.available_seats = max(0, self.total_capacity - confirmed_seats)
        self.save(update_fields=['available_seats'])
        return self.available_seats

    def __str__(self):
        return f"{self.tour.title} — {self.start_date.strftime('%d %b %Y')} ({self.available_seats}/{self.total_capacity} seats left)"


class TourItinerary(models.Model):
    """Day by day breakdown of the journey."""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='itineraries')
    day_number = models.PositiveSmallIntegerField(default=1)
    title = models.CharField(max_length=255)
    description = models.TextField()
    meals = models.CharField(max_length=150, blank=True, help_text="e.g. Breakfast, Lunch, Dinner")
    stay_info = models.CharField(max_length=150, blank=True, help_text="e.g. Eco Resort Sajek")

    class Meta:
        ordering = ['day_number']
        verbose_name = "Itinerary Day"
        verbose_name_plural = "Itinerary Days"

    def __str__(self):
        return f"Day {self.day_number}: {self.title}"


class TourImage(models.Model):
    """Gallery images for a tour."""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='tours/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Tour Gallery Image"
        verbose_name_plural = "Tour Gallery Images"

    def __str__(self):
        return f"{self.tour.title} Image {self.id}"


class TourInclusion(models.Model):
    """Included and Excluded items."""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='inclusions')
    item = models.CharField(max_length=255)
    is_included = models.BooleanField(default=True, help_text="Checked = Included (✓), Unchecked = Excluded (✕)")

    class Meta:
        verbose_name = "Inclusion / Exclusion"
        verbose_name_plural = "Inclusions & Exclusions"

    def __str__(self):
        status = "Included" if self.is_included else "Excluded"
        return f"[{status}] {self.item}"
