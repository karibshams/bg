from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from apps.tours.models import Destination, CorporateTour, CorporateItinerary
from apps.tours.admin import CorporateTourAdmin
from apps.tours.corporate_voucher import generate_corporate_voucher_pdf

class CorporateToursTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser('admin_corp', 'admin@example.com', 'pass1234')
        self.client.force_login(self.admin_user)

        self.dest1 = Destination.objects.create(name="Bandarban", slug="bandarban", is_featured=True)
        self.dest2 = Destination.objects.create(name="Cox's Bazar", slug="coxs-bazar", is_featured=True)

        today = date.today()
        self.corp_tour = CorporateTour.objects.create(
            title="Grameenphone Annual Executive Retreat 2026",
            bangla_title="গ্রামীণফোন বার্ষিক করপোরেট ভ্রমণ ২০২৬",
            company_name="Grameenphone Ltd.",
            contact_person="Tanvir Ahmed",
            designation="Head of People & Culture",
            phone="01711998877",
            email="tanvir.corp@grameenphone.com",
            office_address="GPHouse, Bashundhara R/A, Dhaka",
            route_summary="Dhaka -> Bandarban -> Cox's Bazar -> Dhaka",
            start_date=today + timedelta(days=20),
            end_date=today + timedelta(days=24),
            duration_text="5 Days / 4 Nights",
            num_participants=80,
            bus_count=2,
            bus_type="Luxury Scania AC Multi-Axle Coaches",
            accommodation_details="Sayeman Beach Resort (Executive Twin Sharing Suites)",
            catering_details="Full-board buffet catering + Gala BBQ dinner on Cox's Bazar beach",
            total_cost=850000.00,
            advance_paid=300000.00,
            payment_status="PARTIAL",
            special_requirements="Beachside seminar sound system, projector screen, customized branded corporate gifts",
            reminder_notes="Confirm 2 Scania buses from operator by day 15. Assign 2 senior tour managers.",
            status="CONFIRMED"
        )
        self.corp_tour.destinations.add(self.dest1, self.dest2)

        # Add custom day-by-day itineraries
        self.itin1 = CorporateItinerary.objects.create(
            corporate_tour=self.corp_tour,
            day_number=1,
            title="Departure from Dhaka & Arrival at Bandarban",
            description="Luxury AC coach departure at night. Check-in at Bandarban resort, breakfast, and executive team briefing.",
            stay_info="Bandarban Hill Resort"
        )
        self.itin2 = CorporateItinerary.objects.create(
            corporate_tour=self.corp_tour,
            day_number=2,
            title="Nilgiri & Chimbuk Sightseeing + Transfer to Cox's Bazar",
            description="Cloud exploration at Nilgiri, ethnic tribal lunch, and scenic sunset transfer to Cox's Bazar.",
            stay_info="Sayeman Beach Resort, Cox's Bazar"
        )

    def test_corporate_tour_creation_and_reference_code(self):
        self.assertTrue(self.corp_tour.reference_code.startswith("BG-CORP-"))
        self.assertEqual(self.corp_tour.destinations.count(), 2)
        dest_display = self.corp_tour.get_destinations_display()
        self.assertIn("Bandarban", dest_display)
        self.assertIn("Cox's Bazar", dest_display)

    def test_due_amount_calculation(self):
        # 850,000 - 300,000 = 550,000
        self.assertEqual(self.corp_tour.due_amount, 550000.00)

    def test_corporate_voucher_pdf_generation(self):
        pdf_bytes = generate_corporate_voucher_pdf(self.corp_tour)
        self.assertTrue(len(pdf_bytes) > 1000)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))

    def test_admin_custom_voucher_view(self):
        admin_voucher_url = reverse('admin:corporate_tour_voucher', args=[self.corp_tour.id])
        response = self.client.get(admin_voucher_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn(self.corp_tour.reference_code, response['Content-Disposition'])

    def test_public_corporate_voucher_view(self):
        voucher_url = reverse('tours:corporate_voucher', args=[self.corp_tour.reference_code])
        response = self.client.get(voucher_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn(self.corp_tour.reference_code, response['Content-Disposition'])

    def test_admin_list_display_and_badges(self):
        site = AdminSite()
        admin_obj = CorporateTourAdmin(CorporateTour, site)
        
        status_html = admin_obj.status_badge(self.corp_tour)
        self.assertIn("Confirmed", status_html)

        payment_html = admin_obj.payment_badge(self.corp_tour)
        self.assertIn("Partially Paid", payment_html)

        voucher_html = admin_obj.voucher_action(self.corp_tour)
        self.assertIn("PDF Voucher", voucher_html)
