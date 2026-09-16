import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.core.models import SiteSetting, Testimonial, FAQ
from apps.tours.models import Destination, TourCategory, Tour, TourDate, TourItinerary, TourInclusion
from apps.stories.models import Story
from apps.gallery.models import GalleryItem

class Command(BaseCommand):
    help = "Seeds initial realistic travel data for Bhromonghuri (ভ্রমণঘুড়ি)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Bhromonghuri data..."))

        # 1. Superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@bhromonghuri.com', 'admin123')
            self.stdout.write(self.style.SUCCESS("[OK] Superuser created (admin / admin123)"))
        else:
            self.stdout.write(self.style.WARNING("Superuser 'admin' already exists"))

        # 2. Site Settings
        setting, _ = SiteSetting.objects.get_or_create(pk=1)
        setting.site_name = "ভ্রমণঘুড়ি (Bhromonghuri)"
        setting.site_tagline_bn = "নতুন জায়গা, নতুন গল্প, নতুন অনুভূতি"
        setting.site_tagline_en = "Explore • Experience • Discover"
        setting.hero_headline = "অদেখা বাংলাকে নতুন চোখে দেখা"
        setting.hero_subheadline = "ভ্রমণঘুড়ির সাথে আবিষ্কার করুন পাহাড়, মেঘের উপত্যকা, সুন্দরবনের ম্যানগ্রোভ আর সেন্টমার্টিনের প্রবাল দ্বীপ। প্রতিটি পদক্ষেপে নিরাপদ ও রোমাঞ্চকর ভ্রমণ।"
        setting.phone = "+880 1712-345678"
        setting.email = "explore@bhromonghuri.com"
        setting.address = "House 42, Road 11, Banani, Dhaka - 1213, Bangladesh"
        setting.facebook_url = "https://facebook.com/bhromonghuri"
        setting.instagram_url = "https://instagram.com/bhromonghuri"
        setting.youtube_url = "https://youtube.com/@bhromonghuri"
        setting.total_tours_count = "60+"
        setting.total_travelers_count = "2,400+"
        setting.average_rating = 4.9
        setting.destinations_count = "28+"
        setting.save()
        self.stdout.write(self.style.SUCCESS("[OK] Site settings updated"))

        # 3. Categories
        cat_mountain, _ = TourCategory.objects.get_or_create(
            slug='mountain-hills',
            defaults={'name': 'Mountain & Hills', 'bangla_name': 'পাহাড় ও মেঘের রাজ্য', 'icon': 'mountain'}
        )
        cat_haor, _ = TourCategory.objects.get_or_create(
            slug='waterways-haor',
            defaults={'name': 'Waterways & Haor', 'bangla_name': 'হাওর ও জলরাশি', 'icon': 'ship'}
        )
        cat_beach, _ = TourCategory.objects.get_or_create(
            slug='beach-islands',
            defaults={'name': 'Beach & Islands', 'bangla_name': 'সমুদ্র ও প্রবাল দ্বীপ', 'icon': 'umbrella'}
        )
        cat_forest, _ = TourCategory.objects.get_or_create(
            slug='forest-wildlife',
            defaults={'name': 'Forest & Wildlife', 'bangla_name': 'অরণ্য ও বন্যপ্রাণী', 'icon': 'trees'}
        )

        # 4. Destinations
        dest_sajek, _ = Destination.objects.get_or_create(
            slug='sajek-valley',
            defaults={
                'name': 'Sajek Valley',
                'bangla_name': 'সাজেক ভ্যালি',
                'tagline': 'মেঘের রাজ্য ও হেলিপ্যাডের সূর্যাস্ত',
                'description': 'রাঙ্গামাটির বাঘাইছড়ি উপজেলায় অবস্থিত মেঘে ঢাকা উপত্যকা। পাহাড়ি আঁকাবাঁকা পথ আর মেঘের সাথে মিতালীর এক অপূর্ব স্বর্গরাজ্য।',
                'is_featured': True,
                'order': 1
            }
        )
        dest_bandarban, _ = Destination.objects.get_or_create(
            slug='bandarban',
            defaults={
                'name': 'Bandarban',
                'bangla_name': 'বান্দরবান',
                'tagline': 'বাংলার ছাদ, নীলগিরি ও নাফাকুম',
                'description': 'পাহাড়ের চূড়া, রুমা বাজার, মেঘ ছোঁয়া নীলগিরি, বগালেক আর রোমাঞ্চকর ট্র্যাকিং ট্রেইল নিয়ে বাংলাদেশের অন্যতম সেরা ট্রাভেল স্পট।',
                'is_featured': True,
                'order': 2
            }
        )
        dest_tanguar, _ = Destination.objects.get_or_create(
            slug='tanguar-haor',
            defaults={
                'name': 'Tanguar Haor',
                'bangla_name': 'টাঙ্গুয়ার হাওর',
                'tagline': 'মেঘালয়ের পাদদেশের নীল জলরাশি',
                'description': 'সুনামগঞ্জের রামসার সাইট টাঙ্গুয়ার হাওর, যাদুকাটা নদী ও নীলাদ্রি লেকের শান্ত জলে প্রিমিয়াম হাউসবোটে ভেসে বেড়ানোর স্বর্গীয় অভিজ্ঞতা।',
                'is_featured': True,
                'order': 3
            }
        )
        dest_sreemangal, _ = Destination.objects.get_or_create(
            slug='sreemangal',
            defaults={
                'name': 'Sreemangal',
                'bangla_name': 'শ্রীমঙ্গল',
                'tagline': 'সবুজ চায়ের দেশ ও লাউয়াছড়া বনানী',
                'description': 'মাইলের পর মাইল বিস্তৃত চা বাগান, সাত রঙের চা, মাধবপুর লেক ও চিরসবুজ রেইনফরেস্ট লাউয়াছড়ার মায়াবী পরিবেশ।',
                'is_featured': True,
                'order': 4
            }
        )
        dest_sundarbans, _ = Destination.objects.get_or_create(
            slug='sundarbans',
            defaults={
                'name': 'Sundarbans',
                'bangla_name': 'সুন্দরবন',
                'tagline': 'ম্যানগ্রোভ অরণ্য ও রয়েল বেঙ্গল টাইগারের পদচিহ্ন',
                'description': 'বিশ্বের বৃহত্তম ম্যানগ্রোভ অরণ্য, চিত্রল হরিণ, কুমির আর বন্য জীববৈচিত্র্যের রোমাঞ্চকর নৌবিহার।',
                'is_featured': True,
                'order': 5
            }
        )
        dest_saintmartin, _ = Destination.objects.get_or_create(
            slug='saint-martin',
            defaults={
                'name': "Saint Martin's Island",
                'bangla_name': 'সেন্টমার্টিন দ্বীপ',
                'tagline': 'নীল জল, প্রবাল আর নারিকেল জিঞ্জিরা',
                'description': 'বঙ্গোপসাগরের বুকে একমাত্র প্রবাল দ্বীপ সেন্টমার্টিন ও ছেঁড়াদ্বীপ। সূর্যাস্ত, সাইক্লিং আর তাজা সামুদ্রিক মাছের স্বাদ।',
                'is_featured': True,
                'order': 6
            }
        )
        self.stdout.write(self.style.SUCCESS("[OK] Destinations created"))

        # 5. Tours
        tour_1, _ = Tour.objects.get_or_create(
            slug='sajek-cloud-kingdom-adventure',
            defaults={
                'title': 'Sajek Valley: Kingdom of Clouds Adventure',
                'bangla_title': 'সাজেক ভ্যালি: মেঘের রাজ্যে রোমাঞ্চকর অভিযান',
                'destination': dest_sajek,
                'category': cat_mountain,
                'duration': '3 Days / 2 Nights',
                'duration_days': 3,
                'price': 9500.00,
                'discount_price': 8500.00,
                'max_travelers': 22,
                'short_description': 'খাগড়াছড়ি থেকে চাঁন্দের গাড়িতে পাহাড়ি আঁকাবাঁকা পথ পাড়ি দিয়ে সাজেকের রুইলুই পাড়া, কংলাক পাহাড় ও হেলিপ্যাডের মেঘ দেখা।',
                'description': 'সাজেক ভ্যালি ভ্রমণ মানেই মেঘের উপর দিয়ে চলা। সকালে ঘুম ভেঙে জানালার বাইরে কেবল ভাসমান মেঘমালা। এই ট্যুরে থাকছে সাজেকের সেরা ইকো-রিসোর্টে থাকার সুযোগ, কংলাক পাহাড়ে ট্র্যাকিং, আলুটিলা গুহা ও তারেং এক্সপ্লোরেশন। সাথে অভিজ্ঞ ট্যুর ম্যানেজার ও ট্রাভেল কিট।',
                'badge_text': 'Popular Choice',
                'rating': 4.9,
                'reviews_count': 34,
                'is_featured': True,
                'is_published': True,
            }
        )

        tour_2, _ = Tour.objects.get_or_create(
            slug='bandarban-nilgiri-chimbuk-trail',
            defaults={
                'title': 'Bandarban: Nilgiri & Chimbuk Hill Odyssey',
                'bangla_title': 'বান্দরবান: নীলগিরি, চিম্বুক ও শৈলপ্রপাত অভিযান',
                'destination': dest_bandarban,
                'category': cat_mountain,
                'duration': '3 Days / 2 Nights',
                'duration_days': 3,
                'price': 10500.00,
                'discount_price': 9200.00,
                'max_travelers': 18,
                'short_description': 'পাহাড়ের চূড়া ছুঁয়ে যাওয়া মেঘ, নীলগিরি রিসোর্ট পয়েন্ট, শৈলপ্রপাত ঝর্ণা ও পাহাড়ি আদিবাসী পল্লীর জীবনযাত্রা।',
                'description': 'বাংলার অন্যতম উঁচু পাহাড় চূড়া নীলগিরিতে দাঁড়িয়ে মেঘের সাগরে অবগাহন। চিম্বুক পাহাড়ের নৈসর্গিক সৌন্দর্য, মিলনছড়ি ভিউ পয়েন্ট আর সাঙ্গু নদীর তীরে শান্ত সন্ধ্যা উপভোগ করার পূর্ণাঙ্গ ভ্রমণ পরিকল্পনা।',
                'badge_text': 'Best Seller',
                'rating': 4.8,
                'reviews_count': 28,
                'is_featured': True,
                'is_published': True,
            }
        )

        tour_3, _ = Tour.objects.get_or_create(
            slug='tanguar-haor-luxury-houseboat',
            defaults={
                'title': 'Tanguar Haor: Luxury Houseboat Voyage',
                'bangla_title': 'টাঙ্গুয়ার হাওর: প্রিমিয়াম হাউসবোটে জলকাব্য',
                'destination': dest_tanguar,
                'category': cat_haor,
                'duration': '2 Days / 2 Nights',
                'duration_days': 2,
                'price': 8500.00,
                'discount_price': 7500.00,
                'max_travelers': 16,
                'short_description': 'ঐতিহ্যবাহী কাঠের হাউসবোটে আধুনিক সব সুযোগ-সুবিধা নিয়ে টাঙ্গুয়ার হাওর, নীলাদ্রি লেক ও যাদুকাটা নদীতে ভেসে বেড়ানো।',
                'description': 'বৃষ্টির দিনে কিংবা শরতের নীল আকাশে মেঘালয়ের পাহাড়কে সামনে রেখে টাঙ্গুয়ার হাওরে ভাসার অনবদ্য অভিজ্ঞতা। ওয়াচ টাওয়ার, শিমুল বাগান, বারিক্কা টিলা এবং নীলাদ্রি লেকে ক্যাম্পিং ফিল। দেশি হাঁসের মাংস ও হাওরের তাজা মাছের লোভনীয় খাবার।',
                'badge_text': 'Hot Deal',
                'rating': 5.0,
                'reviews_count': 42,
                'is_featured': True,
                'is_published': True,
            }
        )

        tour_4, _ = Tour.objects.get_or_create(
            slug='sreemangal-rainforest-tea-escape',
            defaults={
                'title': 'Sreemangal: Tea Gardens & Rainforest Trail',
                'bangla_title': 'শ্রীমঙ্গল: সবুজ চায়ের বাগান ও রেইনফরেস্ট ক্যাম্প',
                'destination': dest_sreemangal,
                'category': cat_forest,
                'duration': '2 Days / 1 Night',
                'duration_days': 2,
                'price': 6500.00,
                'discount_price': 5800.00,
                'max_travelers': 20,
                'short_description': 'লাউয়াছড়া জাতীয় উদ্যানের ট্র্যাকিং, মাধবপুর লেকের পদ্মফুল এবং শত বছরের ঐতিহ্যবাহী চা বাগানের মনোরম সবুজ।',
                'description': 'শহরের কোলাহল থেকে দূরে নিবিড় প্রকৃতির কোলে দুই দিন। বিশেষ আকর্ষণ: উলুক বানর ও বিরল পাখির কলতান, পাহাড়ি আদিবাসী মণিপুরী পাড়ার তাঁতশিল্প এবং বিখ্যাত নীলকণ্ঠের সাত রঙের চা।',
                'badge_text': 'Weekend Special',
                'rating': 4.7,
                'reviews_count': 19,
                'is_featured': True,
                'is_published': True,
            }
        )

        tour_5, _ = Tour.objects.get_or_create(
            slug='sundarbans-mangrove-safari',
            defaults={
                'title': 'Sundarbans: Mystical Mangrove Cruise Safari',
                'bangla_title': 'সুন্দরবন: ম্যানগ্রোভ বন ও ক্রুজ সাফারি',
                'destination': dest_sundarbans,
                'category': cat_forest,
                'duration': '4 Days / 3 Nights',
                'duration_days': 4,
                'price': 16000.00,
                'discount_price': 14500.00,
                'max_travelers': 30,
                'short_description': 'মোংলা থেকে লাক্সারি ভেসেল ক্রুজে কটকা, কচিখালী, করমজল এবং হরিনটানা ক্যানেল ক্রুজিং সাফারি।',
                'description': 'ইউনেস্কো ওয়ার্ল্ড হেরিটেজ সুন্দরবনের গহীনে চার দিনের রোমাঞ্চকর জাহাজ যাত্রা। অভিজ্ঞ গানম্যান গাইড, ডলফিন ওয়াচিং, ওয়াচ টাওয়ার থেকে বাঘের পদচিহ্ন পর্যবেক্ষণ ও ম্যানগ্রোভ ফরেস্ট ট্র্যাকিং।',
                'badge_text': 'Wild Expedition',
                'rating': 4.9,
                'reviews_count': 22,
                'is_featured': True,
                'is_published': True,
            }
        )

        tour_6, _ = Tour.objects.get_or_create(
            slug='saint-martin-coral-paradise',
            defaults={
                'title': "Saint Martin: Blue Horizon & Coral Paradise",
                'bangla_title': 'সেন্টমার্টিন: প্রবাল দ্বীপ ও নীল সাগরের হাতছানি',
                'destination': dest_saintmartin,
                'category': cat_beach,
                'duration': '3 Days / 2 Nights',
                'duration_days': 3,
                'price': 12000.00,
                'discount_price': 10500.00,
                'max_travelers': 24,
                'short_description': 'জাহাজে নীল সাগরে যাত্রা, সেন্টমার্টিনের স্বচ্ছ পানি, ছেঁড়াদ্বীপে সাইক্লিং আর রূপচাঁদা মাছের ফ্রাই।',
                'description': 'কক্সবাজার বা টেকনাফ থেকে জাহাজে সরাসরি সেন্টমার্টিন। রাতের জোছনায় সাগরের গর্জন শোনা, স্থানীয় বারবিকিউ ডিনার, ছেঁড়াদ্বীপে ট্রলারে ভ্রমণ ও প্রবালের মাঝে স্নরকেলিং।',
                'badge_text': 'Island Vibes',
                'rating': 4.8,
                'reviews_count': 31,
                'is_featured': True,
                'is_published': True,
            }
        )
        self.stdout.write(self.style.SUCCESS("[OK] Tours created"))

        # 6. Tour Dates
        today = datetime.date.today()
        sample_tours = [tour_1, tour_2, tour_3, tour_4, tour_5, tour_6]
        for idx, tour in enumerate(sample_tours):
            TourDate.objects.get_or_create(
                tour=tour,
                start_date=today + datetime.timedelta(days=7 + idx * 3),
                defaults={
                    'end_date': today + datetime.timedelta(days=7 + idx * 3 + tour.duration_days),
                    'available_seats': 14,
                    'price_override': None,
                    'is_active': True,
                }
            )
            TourDate.objects.get_or_create(
                tour=tour,
                start_date=today + datetime.timedelta(days=21 + idx * 4),
                defaults={
                    'end_date': today + datetime.timedelta(days=21 + idx * 4 + tour.duration_days),
                    'available_seats': 18,
                    'price_override': None,
                    'is_active': True,
                }
            )

        # 7. Itineraries for Tour 1 (Sajek)
        TourItinerary.objects.get_or_create(
            tour=tour_1,
            day_number=1,
            defaults={
                'title': 'যাত্রা শুরু ও রুইলুই পাড়ায় পৌঁছানো',
                'description': 'ঢাকা থেকে রাতের বাসে খাগড়াছড়ি। সকালের নাস্তা সেরে চাঁন্দের গাড়িতে আর্মি এসকর্ট নিয়ে পাহাড়ের বাঁক পেরিয়ে সাজেকের পথে যাত্রা। দুপুরে রুইলুই পাড়ায় রিসোর্টে চেক-ইন ও দুপুরের পাহাড়ি রান্না উপভোগ। বিকেলে হেলিপ্যাডে সূর্যাস্ত দেখা।',
                'meals': 'সকালের নাস্তা, দুপুরের খাবার, রাতের বারবিকিউ',
                'stay_info': 'সাজেক ইকো কটেজ'
            }
        )
        TourItinerary.objects.get_or_create(
            tour=tour_1,
            day_number=2,
            defaults={
                'title': 'কংলাক পাহাড় চূড়া ও মেঘের সাগরে অবগাহন',
                'description': 'ভোরবেলায় সূর্যোদয় ও মেঘের খেলা দেখা। সকালের নাস্তা সেরে সাজেকের সর্বোচ্চ চূড়া কংলাক পাহাড়ে ট্র্যাকিং। স্থানীয় লুসাই পল্লী পরিদর্শন। বিকেলে সাজেক কফি হাউসে আড্ডা ও রুইলুই পাড়ার পাহাড়ি সংস্কৃতি দর্শন।',
                'meals': 'সকালের নাস্তা, দুপুরের পাহাড়ি খাবার, রাতের খাবার',
                'stay_info': 'সাজেক ইকো কটেজ'
            }
        )
        TourItinerary.objects.get_or_create(
            tour=tour_1,
            day_number=3,
            defaults={
                'title': 'আলুটিলা গুহা, তারেং ও ঢাকার উদ্দেশ্যে প্রত্যাবর্তন',
                'description': 'সকালে চাঁন্দের গাড়িতে খাগড়াছড়ির উদ্দেশ্যে রওয়ানা। রহস্যময় আলুটিলা গুহায় মশালের আলোতে অভিযান। তারেং ভিউ পয়েন্ট ও ঝুলন্ত ব্রিজ পরিদর্শন। রাতে বাসে ঢাকার উদ্দেশ্যে যাত্রা।',
                'meals': 'সকালের নাস্তা, দুপুরের ঐতিহ্যবাহী সিস্টেম খাবার',
                'stay_info': 'রাতের স্লিপার বাসে যাত্রা'
            }
        )

        # 8. Tour Inclusions
        inclusions_list = [
            ("ঢাকা - গন্তব্য - ঢাকা নন-এসি / এসি বাস পরিবহন", True),
            ("পাহাড়ি চাঁন্দের গাড়ি / প্রিমিয়াম হাউসবোট রিজার্ভ", True),
            ("নির্ধারিত রিসোর্ট / কটেজে ২ রাত শেয়ারিং রুম", True),
            ("প্রতিদিনের ৩ বেলা মানসম্মত খাবার ও নাস্তা", True),
            ("অভিজ্ঞ ভ্রমণঘুড়ি ট্যুর লিডার ও লোকাল গাইড", True),
            ("প্রবেশ ফি ও স্থানীয় পারমিট চার্জ", True),
            ("ব্যক্তিগত কেনাকাটা ও ঔষধের খরচ", False),
            ("যাত্রাপথের বিরতিতে নিজস্ব খাবার", False),
            ("প্যাকেজে অন্তর্ভুক্ত নয় এমন যেকোনো অতিরিক্ত রাইড", False),
        ]
        for t in sample_tours:
            for item, is_inc in inclusions_list:
                TourInclusion.objects.get_or_create(tour=t, item=item, defaults={'is_included': is_inc})

        # 9. Stories
        Story.objects.get_or_create(
            slug='sajek-valley-first-touch-of-clouds',
            defaults={
                'title': 'ভ্রমণের গল্প: সাজেকের মেঘের দেশে প্রথম পা রাখা',
                'bangla_title': 'সাজেকের মেঘের দেশে প্রথম পা রাখা',
                'destination': dest_sajek,
                'author_name': 'শামস তানভীর',
                'read_time': '4 min read',
                'excerpt': 'পাহাড়ের বুক চিরে চাঁন্দের গাড়ি যখন এগোচ্ছিল, মনে হচ্ছিল আমরা যেন পৃথিবীর শেষ প্রান্তে মেঘের দেশে পৌঁছে যাচ্ছি...',
                'content': '''পাহাড় সবসময়ই আমাকে টানে। তবে সাজেকের টান একেবারেই অন্যরকম। সকাল সাড়ে এগারোটায় যখন বাঘাইহাট থেকে আমাদের চাঁন্দের গাড়ির বহর সেনা এসকর্টে চলতে শুরু করল, তখন চারপাশের পাহাড়ি ঢাল আর শীতল হাওয়া এক অদ্ভুত শিহরণ সৃষ্টি করছিল।

কংলাক পাহাড়ের মাথায় দাঁড়িয়ে যখন নিচের উপত্যকা দেখলাম, মনে হলো যেন এক বিশাল সাদা মেঘের সমুদ্র আমাদের পায়ে আছড়ে পড়ছে। ভ্রমণের সার্থকতা এখানেই—প্রতিদিনের ব্যস্ত নাগরিক জীবন থেকে হারিয়ে গিয়ে প্রকৃতির খাঁটি রূপটাকে অনুভব করা।

ভ্রমণঘুড়ির সুন্দর ব্যবস্থাপনা আর সহযাত্রীদের বন্ধুত্বপূর্ণ পরিবেশ পুরো সফরটিকে অবিস্মরণীয় করে রেখেছিল।''',
                'is_featured': True,
            }
        )
        Story.objects.get_or_create(
            slug='tanguar-haor-moonlit-night-houseboat',
            defaults={
                'title': 'টাঙ্গুয়ার হাওরে জোছনা রাতের জলকাব্য',
                'bangla_title': 'টাঙ্গুয়ার হাওরে জোছনা রাতের জলকাব্য',
                'destination': dest_tanguar,
                'author_name': 'ফারহানা ইসলাম',
                'read_time': '5 min read',
                'excerpt': 'সুনামগঞ্জের নীল জলরাশি আর মেঘালয়ের পাহাড় যখন রূপালী চাঁদের আলোয় ভেসে উঠছিল, হাউসবোটের ডেকে বসে সে দৃশ্য ভোলার নয়...',
                'content': '''তাহিরপুর ঘাট থেকে যখন আমাদের বজরা নৌকা বা হাউসবোট চলতে শুরু করল, তখন চোখের সামনে শুধু জল আর জল। দূরে মেঘালয়ের গাঢ় নীল পাহাড়গুলো যেন সীমানা প্রাচীর তৈরি করে রেখেছে।

টাঙ্গুয়ার হাওরের স্বচ্ছ পানিতে স্নান, ওয়াচ টাওয়ারের চারপাশের পাখির ওড়াউড়ি, আর সন্ধ্যায় নীলাদ্রি লেকের পাড়ে বসে পাহাড়ি চা খাওয়ার মুহূর্তগুলো মনের ভেতর গেঁথে আছে। রাতে বোটের ডেকে বসে খোলা আকাশের নিচে তারার মেলা আর হালকা হাওরের বাতাস—এমন শান্তি শহরে কল্পনাও করা যায় না।

যদি আপনি জলের গান ভালোবাসেন, তবে ভ্রমণঘুড়ির সাথে একবার হাওরে ভেসে বেড়ানো আপনার তালিকায় থাকা উচিত।''',
                'is_featured': True,
            }
        )

        # 10. Testimonials
        Testimonial.objects.get_or_create(
            customer_name="তানভীর আহমেদ",
            tour_name="সাজেক ভ্যালি ট্যুর",
            defaults={
                'customer_designation': 'Software Engineer, Dhaka',
                'review': 'ভ্রমণঘুড়ির সাথে এটি আমার দ্বিতীয় ট্যুর। রিসোর্টের লোকেশন ছিল দুর্দান্ত, একদম মেঘের কোল ঘেঁষে। ট্যুর হোস্টের আন্তরিকতা আর সময়ানুবর্তিতা সত্যিই প্রশংসনীয়। পরবর্তী ট্রিপেও আপনাদের সাথেই যাচ্ছি!',
                'rating': 5,
                'is_featured': True,
            }
        )
        Testimonial.objects.get_or_create(
            customer_name="সাদিয়া আফরিন",
            tour_name="টাঙ্গুয়ার হাওর হাউসবোট",
            defaults={
                'customer_designation': 'Architect, Sylhet',
                'review': 'মেয়েদের জন্য এতো চমৎকার ও নিরাপদ পরিবেশ খুব কম ট্রাভেল গ্রুপে দেখা যায়। হাউসবোটের খাবার ছিল এক কথায় অসাধারণ! দেশি হাঁস আর হাওরের মাছের স্বাদ ভুলতে পারছি না।',
                'rating': 5,
                'is_featured': True,
            }
        )
        Testimonial.objects.get_or_create(
            customer_name="মাহমুদুল হাসান",
            tour_name="বান্দরবান নীলগিরি ট্রেইল",
            defaults={
                'customer_designation': 'University Faculty, Chittagong',
                'review': 'পাহাড়ি রুট ম্যানেজমেন্ট ছিল নিখুঁত। কোনো ধরনের হিডেন চার্জ নেই, যা কমিট করেছে তার চেয়েও বেশি সুবিধা পেয়েছি। হাইলি রিকমেন্ডেড!',
                'rating': 5,
                'is_featured': True,
            }
        )

        # 11. FAQs
        FAQ.objects.get_or_create(
            question="ভ্রমণঘুড়ির সাথে বুকিং করার নিয়ম কী?",
            defaults={
                'answer': 'আমাদের ওয়েবসাইটের ট্যুর পেজ থেকে পছন্দের ট্যুর এবং তারিখ সিলেক্ট করে "বুক করুন" বাটনে ক্লিক করুন। আপনার নাম, ফোন ও যাত্রীদের সংখ্যা দিয়ে বিকাশ, নগদ বা কার্ডের মাধ্যমে পেমেন্ট সম্পন্ন করলেই সাথে সাথে বুকিং কনফার্মেশন ও রেফারেন্স নম্বর পেয়ে যাবেন।',
                'order': 1,
                'is_published': True,
            }
        )
        FAQ.objects.get_or_create(
            question="ট্যুর বাতিল বা রিফান্ড পলিসি কেমন?",
            defaults={
                'answer': 'ভ্রমণ শুরুর ৭ দিন পূর্বে জানালে সম্পূর্ণ রিফান্ড অথবা পরবর্তী যেকোনো ট্যুরে আসন অ্যাডজাস্ট করা যাবে। যাত্রা শুরুর ৩ দিন পূর্বে জানালে ৫০% রিফান্ড প্রযোজ্য। বিস্তারিত তথ্যের জন্য আমাদের হেল্পলাইনে যোগাযোগ করতে পারেন।',
                'order': 2,
                'is_published': True,
            }
        )
        FAQ.objects.get_or_create(
            question="নারী বা পরিবারের সদস্যদের জন্য পরিবেশ কতটা নিরাপদ?",
            defaults={
                'answer': 'আমাদের প্রতিটি ট্যুরই ফ্যামিলি ও ফিমেল ফ্রেন্ডলি। দলগত ভ্রমণের ক্ষেত্রে নারী ও পরিবারের সুরক্ষাকে আমরা সর্বোচ্চ অগ্রাধিকার দিই। প্রতিটি টিমে অভিজ্ঞ ট্যুর ম্যানেজার সার্বক্ষণিক উপস্থিত থাকেন।',
                'order': 3,
                'is_published': True,
            }
        )
        FAQ.objects.get_or_create(
            question="পাহাড়ি ট্যুরে কী কী সঙ্গে নেওয়া জরুরি?",
            defaults={
                'answer': 'জাতীয় পরিচয়পত্র (NID) এর ফটোকপি (বাধ্যতামূলক), আরামদায়ক ট্র্যাকিং জুতো, পাওয়ার ব্যাংক, ব্যক্তিগত ঔষধ, হালকা চাদর বা উইন্ডব্রেকার এবং ওয়াটারপ্রুফ ব্যাগ সঙ্গে নেওয়া বাঞ্ছনীয়।',
                'order': 4,
                'is_published': True,
            }
        )

        # 12. Gallery Items
        GalleryItem.objects.get_or_create(
            title="সাজেকের হেলিপ্যাডে ভাসমান মেঘ",
            defaults={
                'destination': dest_sajek,
                'category': 'MOUNTAIN',
                'caption': 'সকালের প্রথম সূর্যরশ্মিতে আলোকিত মেঘমালা',
                'is_featured': True,
                'order': 1,
            }
        )
        GalleryItem.objects.get_or_create(
            title="নীলাদ্রি লেকের শান্ত নীল জল",
            defaults={
                'destination': dest_tanguar,
                'category': 'FOREST',
                'caption': 'মেঘালয়ের পাহাড় আর চুনাপাথরের নীলাদ্রি লেক',
                'is_featured': True,
                'order': 2,
            }
        )
        GalleryItem.objects.get_or_create(
            title="বান্দরবান নীলগিরির পাহাড়ি কুয়াশা",
            defaults={
                'destination': dest_bandarban,
                'category': 'MOUNTAIN',
                'caption': 'পাহাড়ের চূড়া থেকে দিগন্ত বিস্তৃত মেঘের ভেলা',
                'is_featured': True,
                'order': 3,
            }
        )
        GalleryItem.objects.get_or_create(
            title="সেন্টমার্টিনের স্বচ্ছ সাগরে সূর্যাস্ত",
            defaults={
                'destination': dest_saintmartin,
                'category': 'BEACH',
                'caption': 'প্রবাল দ্বীপের পশ্চিম সৈকতে গোধূলির লাল আভা',
                'is_featured': True,
                'order': 4,
            }
        )
        GalleryItem.objects.get_or_create(
            title="শ্রীমঙ্গলের সবুজ চায়ের গালিচা",
            defaults={
                'destination': dest_sreemangal,
                'category': 'FOREST',
                'caption': 'সকালে শিশির ভেজা সবুজ দুটি পাতা একটি কুঁড়ি',
                'is_featured': True,
                'order': 5,
            }
        )
        GalleryItem.objects.get_or_create(
            title="টাঙ্গুয়ার হাওরে কাঠের বজরায় বন্ধুরা",
            defaults={
                'destination': dest_tanguar,
                'category': 'GROUP',
                'caption': 'জল তরঙ্গে আড্ডা ও গানের আনন্দঘন মুহূর্ত',
                'is_featured': True,
                'order': 6,
            }
        )

        self.stdout.write(self.style.SUCCESS("[OK] Realistic Bangladesh travel seed data created successfully!"))
