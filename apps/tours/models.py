import uuid
import re
from django.db import models
from django.utils.text import slugify
from django.utils import timezone


def parse_rich_text_items(text, strip_symbols='•-*+✓✔>✕✗xX '):
    """
    Parses items from either HTML (<ul><li>...</li></ul> or <p>...</p>) 
    or plain multi-line text, cleanly stripping bullet characters and outer tags.
    """
    if not text:
        return []
    items = []
    text_lower = text.lower()
    if '<li' in text_lower:
        found = re.findall(r'<li[^>]*>(.*?)</li>', text, re.IGNORECASE | re.DOTALL)
        for item in found:
            clean = re.sub(r'<[^>]+>', '', item).strip().lstrip(strip_symbols).strip()
            if clean and clean not in items:
                items.append(clean)
    elif '<p' in text_lower:
        found = re.findall(r'<p[^>]*>(.*?)</p>', text, re.IGNORECASE | re.DOTALL)
        for item in found:
            clean = re.sub(r'<[^>]+>', '', item).strip().lstrip(strip_symbols).strip()
            if clean and clean not in items:
                items.append(clean)
    else:
        for line in text.splitlines():
            clean = line.strip().lstrip(strip_symbols).strip()
            if clean and clean not in items:
                items.append(clean)
    return items

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

    # Geographic coordinates for Interactive Map
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Longitude")

    KNOWN_COORDINATES = {
        'sajek': (23.3820, 92.2938),
        'sajek-valley': (23.3820, 92.2938),
        'coxs-bazar': (21.4272, 91.9701),
        'cox-bazar': (21.4272, 91.9701),
        'bandarban': (22.1953, 92.2184),
        'saint-martin': (20.6272, 92.3225),
        'sreemangal': (24.3065, 91.7296),
        'sundarbans': (22.0864, 89.5160),
        'sundarban': (22.0864, 89.5160),
        'tanguar': (25.1328, 91.0772),
        'tanguar-haor': (25.1328, 91.0772),
        'chittagong': (22.3569, 91.7832),
        'chattogram': (22.3569, 91.7832),
        'rangamati': (22.6533, 92.1753),
        'sylhet': (24.8949, 91.8687),
        'kuakata': (21.8167, 90.1167),
        'dhaka': (23.8103, 90.4125),
    }

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Destination"
        verbose_name_plural = "Destinations"

    def get_coordinates(self):
        """Returns tuple of (lat, lng), falling back to known coordinates by slug or name."""
        if self.latitude is not None and self.longitude is not None:
            return (float(self.latitude), float(self.longitude))
        slug_clean = (self.slug or '').lower().replace('_', '-')
        name_clean = (self.name or '').lower()
        for key, coords in self.KNOWN_COORDINATES.items():
            if key in slug_clean or key in name_clean:
                return coords
        return (23.8103, 90.4125)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.latitude is None or self.longitude is None:
            coords = self.get_coordinates()
            if self.latitude is None:
                self.latitude = coords[0]
            if self.longitude is None:
                self.longitude = coords[1]
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
    
    DURATION_TYPE_CHOICES = [
        ('DAY_TOUR', 'Day Tour (Single Day / Day-Long)'),
        ('MULTI_DAY', 'Multi-Day Tour (e.g. 2 Nights / 3 Days)'),
    ]

    duration_type = models.CharField(
        max_length=20,
        choices=DURATION_TYPE_CHOICES,
        default='MULTI_DAY',
        verbose_name="Tour Duration Classification",
        help_text="Choose duration classification: Day Tour (Single Day / Day-Long) or Multi-Day Tour"
    )
    duration = models.CharField(max_length=80, default="3 Days / 2 Nights")
    duration_days = models.PositiveSmallIntegerField(default=3, help_text="Number of days for filtering")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in BDT (৳)")
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_travelers = models.PositiveIntegerField(default=20)
    
    short_description = models.TextField(help_text="Short teaser for cards and search results")
    bangla_short_description = models.TextField(blank=True, help_text="Bengali teaser for cards and search results")
    description = models.TextField(help_text="Full itinerary and overview")
    bangla_description = models.TextField(blank=True, help_text="Bengali full itinerary and overview")
    cover_image = models.ImageField(
        upload_to='tours/covers/', 
        blank=False, 
        null=True,
        verbose_name="Tour Cover Image (কভার ফটো)",
        help_text="Mandatory: Upload a distinct high-resolution landscape cover photo for this tour package card and hero banner."
    )
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
        """Returns unified list of included items from model field & inline objects, cleanly stripping bullet points and HTML tags."""
        items = parse_rich_text_items(self.included_items, strip_symbols='•-*+✓✔> ')
        for inc in self.inclusions.filter(is_included=True):
            clean = parse_rich_text_items(inc.item, strip_symbols='•-*+✓✔> ')
            for c in clean:
                if c and c not in items:
                    items.append(c)
        return items

    def get_excluded_list(self):
        """Returns unified list of excluded items from model field & inline objects, cleanly stripping bullet points and HTML tags."""
        items = parse_rich_text_items(self.excluded_items, strip_symbols='•-*+✕✗xX- ')
        for exc in self.inclusions.filter(is_included=False):
            clean = parse_rich_text_items(exc.item, strip_symbols='•-*+✕✗xX- ')
            for c in clean:
                if c and c not in items:
                    items.append(c)
        return items

    @property
    def is_day_tour(self):
        return self.duration_type == 'DAY_TOUR' or self.duration_days == 1

    @property
    def duration_type_badge(self):
        if self.is_day_tour:
            return {
                'code': 'DAY_TOUR',
                'en': 'Day Tour (Single Day)',
                'bn': 'ডে ট্যুর (১ দিন)',
                'short_en': 'Day Tour',
                'short_bn': 'ডে ট্যুর',
                'color': 'amber',
                'icon': 'sun'
            }
        return {
            'code': 'MULTI_DAY',
            'en': 'Multi-Day Tour',
            'bn': 'মাল্টি-ডে ট্যুর',
            'short_en': 'Multi-Day',
            'short_bn': 'মাল্টি-ডে',
            'color': 'sky',
            'icon': 'calendar'
        }

    @property
    def get_cover_image_url(self):
        """Returns the tour's custom cover image, falling back to destination cover image or default."""
        if self.cover_image:
            try:
                return self.cover_image.url
            except Exception:
                pass
        if self.destination and self.destination.cover_image:
            try:
                return self.destination.cover_image.url
            except Exception:
                pass
        return '/static/images/hero-sajek.jpg'

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


class CorporateTour(models.Model):
    """
    Dedicated module for bespoke corporate tour events with multi-destination support,
    cost/logistics breakdown, and customizable itineraries.
    """
    STATUS_CHOICES = [
        ('PROPOSAL', 'Proposal / Planning (পরিকল্পনা)'),
        ('CONFIRMED', 'Confirmed (নিশ্চিত)'),
        ('IN_PROGRESS', 'In Progress / Traveling (চলমান)'),
        ('COMPLETED', 'Completed (সম্পন্ন)'),
        ('CANCELLED', 'Cancelled (বাতিল)'),
    ]

    PAYMENT_CHOICES = [
        ('PENDING', 'Payment Pending (বকেয়া)'),
        ('PARTIAL', 'Partially Paid / Advance Received (আংশিক পরিশোধ)'),
        ('PAID', 'Fully Paid (পরিশোধিত)'),
    ]

    reference_code = models.CharField(max_length=40, unique=True, editable=False)
    
    # Event & Package Details
    title = models.CharField(max_length=255, verbose_name="Corporate Event / Tour Title")
    bangla_title = models.CharField(max_length=255, blank=True, verbose_name="Bangla Title (Optional)")
    
    # Client Organization Details
    company_name = models.CharField(max_length=200, verbose_name="Client Company / Organization")
    contact_person = models.CharField(max_length=150, verbose_name="Focal Person Name")
    designation = models.CharField(max_length=150, blank=True, verbose_name="Designation / Department")
    phone = models.CharField(max_length=50, verbose_name="Contact Phone")
    email = models.EmailField(verbose_name="Contact Email")
    office_address = models.CharField(max_length=255, blank=True, verbose_name="Company / Office Address")

    # Multi-Destination Support
    destinations = models.ManyToManyField(Destination, related_name='corporate_tours', verbose_name="Destinations Included")
    route_summary = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Custom Route Summary",
        help_text="e.g. Dhaka -> Bandarban + Cox's Bazar -> Dhaka"
    )

    # Schedule & Group Size
    start_date = models.DateField(verbose_name="Tour Start Date")
    end_date = models.DateField(verbose_name="Tour End Date")
    duration_text = models.CharField(max_length=100, default="3 Days / 2 Nights", verbose_name="Duration Description")
    num_participants = models.PositiveIntegerField(default=50, verbose_name="Total Participants / Employees")

    # Logistics Breakdown
    bus_count = models.PositiveIntegerField(default=1, verbose_name="Number of Buses Reserved")
    bus_type = models.CharField(max_length=150, default="Luxury AC Coach (Hino / Scania)", verbose_name="Bus Type / Operator")
    accommodation_details = models.TextField(blank=True, verbose_name="Resort / Hotel Logistics", help_text="e.g. 5-Star Resort, Twin sharing executive rooms")
    catering_details = models.TextField(blank=True, verbose_name="Food & Catering Logistics", help_text="e.g. Buffet breakfast, BBQ dinner, executive lunch sets")

    # Financial & Cost Breakdown
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total Package Budget (BDT)")
    advance_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Advance Paid Amount (BDT)")
    payment_status = models.CharField(max_length=30, choices=PAYMENT_CHOICES, default='PENDING', verbose_name="Payment Status")

    # Special Instructions & Admin Reminders
    special_requirements = models.TextField(blank=True, verbose_name="Client Special Requirements", help_text="Conference hall, sound system, team building, banner setup")
    reminder_notes = models.TextField(blank=True, verbose_name="Administrative Reminders & Logistics Notes", help_text="Internal notes for operations team, driver contacts, guide assignments")

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PROPOSAL', verbose_name="Event Status")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Corporate Tour & Event"
        verbose_name_plural = "Corporate Tours & Events"

    @property
    def due_amount(self):
        return max(0, float(self.total_cost) - float(self.advance_paid))

    def get_destinations_display(self):
        dests = list(self.destinations.all())
        if dests:
            return " + ".join(d.name for d in dests)
        return self.route_summary or "Multi-Destination Tour"

    def save(self, *args, **kwargs):
        if not self.reference_code:
            year = timezone.now().year
            while True:
                rand_code = uuid.uuid4().hex[:6].upper()
                candidate = f"BG-CORP-{year}-{rand_code}"
                if not CorporateTour.objects.filter(reference_code=candidate).exists():
                    self.reference_code = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference_code} — {self.company_name} ({self.title})"


class CorporateItinerary(models.Model):
    """Day-by-day customized schedule for corporate tour events."""
    corporate_tour = models.ForeignKey(CorporateTour, on_delete=models.CASCADE, related_name='itineraries')
    day_number = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=200, verbose_name="Day Heading / Activity")
    description = models.TextField(verbose_name="Activity / Schedule Details")
    stay_info = models.CharField(max_length=200, blank=True, verbose_name="Night Stay / Location")

    class Meta:
        ordering = ['day_number']
        verbose_name = "Corporate Itinerary Day"
        verbose_name_plural = "Corporate Itinerary Days"

    def __str__(self):
        return f"Day {self.day_number}: {self.title}"


