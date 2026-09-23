from django.db import models
from django.utils.text import slugify

class Destination(models.Model):
    """Tourist destination like Sajek, Bandarban, Cox's Bazar, Sundarbans."""
    name = models.CharField(max_length=150)
    bangla_name = models.CharField(max_length=150, blank=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    tagline = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    bangla_description = models.TextField(blank=True)
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
    bangla_short_description = models.TextField(blank=True, help_text="Bengali teaser for cards and search results")
    description = models.TextField(help_text="Full itinerary and overview")
    bangla_description = models.TextField(blank=True, help_text="Bengali full itinerary and overview")
    cover_image = models.ImageField(upload_to='tours/covers/', blank=True, null=True)
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo preview link")
    
    guide_security_info = models.CharField(max_length=200, default="Certified Guide & Safety Escort", blank=True, help_text="e.g. Certified Guide & Safety Escort")
    bangla_guide_security_info = models.CharField(max_length=200, blank=True, help_text="Bengali: Certified Guide & Safety Escort")
    
    included_items = models.TextField(blank=True, help_text="What is included (one item per line)")
    bangla_included_items = models.TextField(blank=True, help_text="Bengali: What is included (one item per line)")
    excluded_items = models.TextField(blank=True, help_text="What is not included (excluded) (one item per line)")
    bangla_excluded_items = models.TextField(blank=True, help_text="Bengali: What is not included (excluded) (one item per line)")
    
    badge_text = models.CharField(max_length=50, blank=True, default="Featured", help_text="e.g. Popular, Hot Deal")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.9)
    reviews_count = models.PositiveIntegerField(default=12)
    
    # Bus Seat Selection Controls
    has_bus_seat_selection = models.BooleanField(
        default=False,
        verbose_name="Enable Bus Seat Selection",
        help_text="Provide an option to enable or disable bus seat selection per tour package"
    )
    bus_layout_type = models.CharField(
        max_length=10,
        choices=[
            ('36', '36-Seater (4x9)'),
            ('40', '40-Seater (4x10)'),
            ('45', '45-Seater (5x9)'),
        ],
        default='40',
        verbose_name="Bus Seat Layout",
        help_text="Choose from three specific bus seat layouts: 36-seater, 40-seater, or 45-seater"
    )

    # NID / Birth Certificate Requirement
    requires_nid_or_birth_cert = models.BooleanField(
        default=True,
        verbose_name="Require NID or Birth Certificate",
        help_text="Require travelers to upload NID or Birth Certificate when booking this package (e.g. hill tracts / border checkpoints)"
    )

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
        """Returns unified list of included items from model field & inline objects, cleanly stripping bullet points."""
        items = []
        if self.included_items:
            for line in self.included_items.splitlines():
                clean = line.strip().lstrip('•-*+✓✔> ').strip()
                if clean and clean not in items:
                    items.append(clean)
        for inc in self.inclusions.filter(is_included=True):
            clean = inc.item.strip().lstrip('•-*+✓✔> ').strip()
            if clean and clean not in items:
                items.append(clean)
        return items

    def get_excluded_list(self):
        """Returns unified list of excluded items from model field & inline objects, cleanly stripping bullet points."""
        items = []
        if self.excluded_items:
            for line in self.excluded_items.splitlines():
                clean = line.strip().lstrip('•-*+✕✗xX- ').strip()
                if clean and clean not in items:
                    items.append(clean)
        for exc in self.inclusions.filter(is_included=False):
            clean = exc.item.strip().lstrip('•-*+✕✗xX- ').strip()
            if clean and clean not in items:
                items.append(clean)
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

    @property
    def booked_seats(self):
        return max(0, self.total_capacity - self.available_seats)

    @property
    def percent_booked(self):
        if not self.total_capacity:
            return 0
        return min(100, round((self.booked_seats / self.total_capacity) * 100))

    @property
    def percent_available(self):
        if not self.total_capacity:
            return 0
        return max(0, 100 - self.percent_booked)

    @property
    def seat_status(self):
        if self.available_seats <= 0:
            return 'SOLD_OUT'
        if self.available_seats <= 5:
            return 'ALMOST_FULL'
        if self.available_seats <= max(10, int(self.total_capacity * 0.4)):
            return 'FILLING_FAST'
        return 'AVAILABLE'

    @property
    def seat_status_badge(self):
        """Returns status metadata (color classes, English label, Bangla label)."""
        status = self.seat_status
        if status == 'SOLD_OUT':
            return {
                'status': 'SOLD_OUT',
                'en': 'Sold Out',
                'bn': 'আসন পূর্ণ',
                'badge_class': 'bg-slate-200 text-slate-700 border-slate-300',
                'bar_class': 'bg-slate-400',
                'color': 'slate',
            }
        elif status == 'ALMOST_FULL':
            return {
                'status': 'ALMOST_FULL',
                'en': f'Only {self.available_seats} seats left!',
                'bn': f'মাত্র {self.available_seats}টি আসন বাকি!',
                'badge_class': 'bg-rose-100 text-rose-800 border-rose-200 animate-pulse',
                'bar_class': 'bg-rose-500',
                'color': 'rose',
            }
        elif status == 'FILLING_FAST':
            return {
                'status': 'FILLING_FAST',
                'en': f'{self.available_seats} seats remaining (Filling Fast)',
                'bn': f'{self.available_seats}টি আসন বাকি (দ্রুত পূর্ণ হচ্ছে)',
                'badge_class': 'bg-amber-100 text-amber-800 border-amber-200',
                'bar_class': 'bg-amber-500',
                'color': 'amber',
            }
        else:
            return {
                'status': 'AVAILABLE',
                'en': f'{self.available_seats} / {self.total_capacity} seats available',
                'bn': f'{self.available_seats} / {self.total_capacity} আসন খালি আছে',
                'badge_class': 'bg-emerald-100 text-emerald-800 border-emerald-200',
                'bar_class': 'bg-emerald-500',
                'color': 'emerald',
            }

    def __init__(self, *args, **kwargs):
        self._capacity_passed = 'total_capacity' in kwargs
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.pk:
            if not getattr(self, '_capacity_passed', False) and self.total_capacity == 40 and self.available_seats != 40:
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
    bangla_title = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    bangla_description = models.TextField(blank=True)
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
    bangla_item = models.CharField(max_length=255, blank=True)
    is_included = models.BooleanField(default=True, help_text="Checked = Included (✓), Unchecked = Excluded (✕)")

    class Meta:
        verbose_name = "Inclusion / Exclusion"
        verbose_name_plural = "Inclusions & Exclusions"

    def __str__(self):
        status = "Included" if self.is_included else "Excluded"
        return f"[{status}] {self.item}"


class TourBus(models.Model):
    """
    Reserved bus for a tour package.
    Supports assigning multiple reserved buses per tour package.
    """
    LAYOUT_CHOICES = [
        ('36', '36-Seater (4x9)'),
        ('40', '40-Seater (4x10)'),
        ('45', '45-Seater (5x9)'),
    ]

    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='buses')
    tour_date = models.ForeignKey('TourDate', on_delete=models.SET_NULL, null=True, blank=True, related_name='buses')
    bus_name = models.CharField(max_length=100, default="Bus 1", help_text="e.g. Scania AC - Bus 1")
    bus_number = models.CharField(max_length=50, blank=True, help_text="e.g. Dhaka Metro-Ba 14-8890")
    layout_type = models.CharField(max_length=10, choices=LAYOUT_CHOICES, default='40')
    total_seats = models.PositiveIntegerField(default=40)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['tour', 'bus_name']
        verbose_name = "Tour Reserved Bus"
        verbose_name_plural = "Tour Reserved Buses"

    def save(self, *args, **kwargs):
        if self.layout_type == '36':
            self.total_seats = 36
        elif self.layout_type == '40':
            self.total_seats = 40
        elif self.layout_type == '45':
            self.total_seats = 45
        super().save(*args, **kwargs)

    def get_seat_layout_grid(self):
        """
        Returns structured grid rows for bus layout:
        36-seater: 9 rows (A-I), 4 seats per row (Left: 1, 2; Right: 3, 4)
        40-seater: 10 rows (A-J), 4 seats per row (Left: 1, 2; Right: 3, 4)
        45-seater: 9 rows (A-I), 5 seats per row (Left: 1, 2; Right: 3, 4, 5)
        """
        rows = []
        row_letters = "ABCDEFGHIJ"
        if self.layout_type == '36':
            for r in row_letters[:9]:
                rows.append({
                    'row': r,
                    'left': [f"{r}1", f"{r}2"],
                    'right': [f"{r}3", f"{r}4"]
                })
        elif self.layout_type == '40':
            for r in row_letters[:10]:
                rows.append({
                    'row': r,
                    'left': [f"{r}1", f"{r}2"],
                    'right': [f"{r}3", f"{r}4"]
                })
        elif self.layout_type == '45':
            for r in row_letters[:9]:
                rows.append({
                    'row': r,
                    'left': [f"{r}1", f"{r}2"],
                    'right': [f"{r}3", f"{r}4", f"{r}5"]
                })
        return rows

    def get_all_seat_numbers(self):
        seats = []
        for row in self.get_seat_layout_grid():
            seats.extend(row['left'])
            seats.extend(row['right'])
        return seats

    def __str__(self):
        return f"{self.bus_name} ({self.get_layout_type_display()}) — {self.tour.title}"

