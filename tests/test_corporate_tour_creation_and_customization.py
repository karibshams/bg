from datetime import date, timedelta
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.tours.models import CorporateTour, CorporateItinerary, Destination

User = get_user_model()


class CorporateTourCreationAndCustomizationTest(TestCase):
    """
    Comprehensive tests for Corporate Tour admin creation, large group capacity,
    fleet logistics, unrestricted destinations, and dedicated frontend presentation layout.
    """

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin_corporate_tester',
            email='admin_corp@test.com',
            password='testpassword123'
        )
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_admin_add_page_loads_with_http_200_no_type_error(self):
        """Verify that GET /admin/tours/corporatetour/add/ does not crash on due_amount."""
        response = self.client.get('/admin/tours/corporatetour/add/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add Corporate Tour &amp; Event')

    def test_admin_create_corporate_tour_with_custom_destination_and_large_group(self):
        """
        Verify that admin can successfully submit and save a bespoke corporate tour
        with unrestricted Bangladesh destination, large group headcount (200 pax),
        and fleet allocations without picking predefined catalog destinations.
        """
        post_data = {
            'company_name': 'Apex Footwear Ltd',
            'contact_person': 'Mahbubur Rahman',
            'designation': 'Senior Manager, People & Culture',
            'phone': '01712345678',
            'email': 'mahbub@apexfootwear.com',
            'office_address': 'Apex Centre, Gulshan-1, Dhaka',
            'title': 'Apex Annual Leadership Summit & Retreat 2026',
            'bangla_title': 'এপেক্স বার্ষিক লিডারশিপ রিট্রিট ২০২৬',
            'destination_name': 'Grand Sylhet Resort & Hotel, Sylhet',
            'route_summary': 'Dhaka -> Sreemangal -> Sylhet Sadar -> Dhaka',
            'start_date': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'end_date': (date.today() + timedelta(days=33)).strftime('%Y-%m-%d'),
            'duration_text': '4 Days / 3 Nights',
            'num_participants': '200',
            'bus_count': '5',
            'bus_type': 'Hyundai Universe 40-Seat Luxury AC Coaches',
            'vehicle_breakdown': '5x Hyundai Universe AC Buses + 2x Toyota HiAce Microbuses for VPs',
            'accommodation_details': 'Grand Sylhet 5-Star Resort, Deluxe Twin sharing + Executive Suites',
            'catering_details': 'Full board dining, opening night banquet, gala BBQ night by the pool',
            'total_cost': '2450000.00',
            'advance_paid': '800000.00',
            'payment_status': 'PARTIAL',
            'special_requirements': 'Convention Hall for 250 delegates, digital podium, dual projectors',
            'reminder_notes': 'Confirm police pilot support on Dhaka-Sylhet Highway',
            'status': 'CONFIRMED',
            'is_published': 'on',
            'itineraries-TOTAL_FORMS': '2',
            'itineraries-INITIAL_FORMS': '0',
            'itineraries-MIN_NUM_FORMS': '0',
            'itineraries-MAX_NUM_FORMS': '1000',
            'itineraries-0-day_number': '1',
            'itineraries-0-title': 'Executive Departure & Grand Sylhet Reception',
            'itineraries-0-description': 'Convoy departure from Apex HQ. Check-in and welcome dinner.',
            'itineraries-0-stay_info': 'Grand Sylhet Resort',
            'itineraries-1-day_number': '2',
            'itineraries-1-title': 'Leadership Keynote & Team Building Sessions',
            'itineraries-1-description': 'Morning conference followed by outdoor lawn team building games.',
            'itineraries-1-stay_info': 'Grand Sylhet Resort',
        }

        response = self.client.post('/admin/tours/corporatetour/add/', post_data)
        self.assertEqual(response.status_code, 302)

        # Verify created model in DB
        corp_tour = CorporateTour.objects.filter(company_name='Apex Footwear Ltd').first()
        self.assertIsNotNone(corp_tour)
        self.assertEqual(corp_tour.num_participants, 200)
        self.assertEqual(corp_tour.bus_count, 5)
        self.assertEqual(corp_tour.destination_name, 'Grand Sylhet Resort & Hotel, Sylhet')
        self.assertTrue(corp_tour.reference_code.startswith('BG-CORP-'))
        self.assertEqual(corp_tour.due_amount, 1650000.00)
        self.assertEqual(corp_tour.itineraries.count(), 2)

    def test_corporate_tour_due_amount_calculation(self):
        """Verify due_amount handles None safely and computes correct balance."""
        tour = CorporateTour(total_cost=None, advance_paid=None)
        self.assertEqual(tour.due_amount, 0.0)

        tour.total_cost = 500000.00
        tour.advance_paid = 200000.00
        self.assertEqual(tour.due_amount, 300000.00)

        tour.advance_paid = 600000.00
        self.assertEqual(tour.due_amount, 0.0)

    def test_get_destinations_display_unrestricted(self):
        """Verify get_destinations_display prioritizes custom destination name."""
        tour = CorporateTour(
            destination_name='Bhawal National Resort, Gazipur',
            route_summary='Dhaka -> Gazipur -> Dhaka'
        )
        self.assertEqual(tour.get_destinations_display(), 'Bhawal National Resort, Gazipur')

    def test_dedicated_corporate_frontend_detail_view(self):
        """Verify the dedicated corporate presentation page renders with rich executive layout."""
        tour = CorporateTour.objects.create(
            title='Beximco Annual Innovation Retreat 2026',
            bangla_title='বেক্সিমকো বার্ষিক রিট্রিট ২০২৬',
            company_name='Beximco Group',
            contact_person='Nazmul Hassan',
            designation='Director of Corporate Affairs',
            phone='01711122233',
            email='nazmul@beximco.net',
            office_address='Beximco Industrial Park, Sarabo, Kashimpur, Gazipur',
            destination_name='Bhawal Resort & Spa, Gazipur',
            route_summary='Dhaka -> Gazipur -> Dhaka',
            start_date=date.today() + timedelta(days=15),
            end_date=date.today() + timedelta(days=17),
            duration_text='3 Days / 2 Nights',
            num_participants=300,
            bus_count=7,
            bus_type='Scania Multi-Axle Luxury AC Coaches',
            vehicle_breakdown='7x Scania 45-Seat AC Buses + 3x Executive HiAce Microbuses',
            accommodation_details='Exclusive resort buyout, executive cottages & deluxe suites',
            catering_details='Full-board buffet dining, pool barbecue & live musical banquet',
            total_cost=3200000.00,
            advance_paid=1000000.00,
            payment_status='PARTIAL',
            special_requirements='Large outdoor amphitheatre setup, professional sound engineering',
            is_published=True
        )

        CorporateItinerary.objects.create(
            corporate_tour=tour,
            day_number=1,
            title='VIP Convoy Arrival & Welcome Reception',
            description='Arrival at Bhawal Resort, express check-in, and welcome drink banquet.',
            stay_info='Bhawal Resort Cottages'
        )

        public_client = Client()
        url = reverse('tours:corporate_detail', kwargs={'reference': tour.reference_code})
        response = public_client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Beximco Group')
        self.assertContains(response, 'Beximco Annual Innovation Retreat 2026')
        self.assertContains(response, '300')
        self.assertContains(response, 'Travelers')
        self.assertContains(response, '7 Coach(es)')
        self.assertContains(response, 'Bhawal Resort &amp; Spa, Gazipur')
        self.assertContains(response, 'VIP Convoy Arrival &amp; Welcome Reception')
        self.assertContains(response, tour.reference_code)
        # Verify link to PDF voucher is present
        voucher_url = reverse('tours:corporate_voucher', kwargs={'reference': tour.reference_code})
        self.assertContains(response, voucher_url)

    def test_corporate_voucher_pdf_download_endpoint(self):
        """Verify the PDF voucher generates successfully and returns application/pdf."""
        tour = CorporateTour.objects.create(
            title='Pran-RFL Executive Strategy Conference 2026',
            company_name='Pran-RFL Group',
            contact_person='Kamrul Islam',
            phone='01733344455',
            email='kamrul@prangroup.com',
            destination_name='Grand Sultan Tea Resort, Sreemangal',
            start_date=date.today() + timedelta(days=20),
            end_date=date.today() + timedelta(days=22),
            duration_text='3 Days / 2 Nights',
            num_participants=120,
            bus_count=3,
            bus_type='Hino 1J Luxury AC Coach',
            vehicle_breakdown='3x Hino 1J AC Coaches + 1x Executive Coaster',
            total_cost=1400000.00,
            advance_paid=500000.00,
            is_published=True
        )

        url = reverse('tours:corporate_voucher', kwargs={'reference': tour.reference_code})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(len(response.content) > 1000)

    def test_corporate_landing_page_and_reference_code_lookup(self):
        """Verify the corporate hub allows looking up proposals by reference code."""
        tour = CorporateTour.objects.create(
            title='Unilever Sales Summit 2026',
            company_name='Unilever Bangladesh',
            contact_person='Sabrina Karim',
            phone='01755566677',
            email='sabrina@unilever.com',
            destination_name='Radisson Blu Bay View, Chattogram',
            start_date=date.today() + timedelta(days=25),
            end_date=date.today() + timedelta(days=27),
            duration_text='3 Days / 2 Nights',
            num_participants=150,
            bus_count=4,
            bus_type='Hyundai Universe AC',
            total_cost=1900000.00,
            advance_paid=1900000.00,
            payment_status='PAID',
            is_published=True
        )

        landing_url = reverse('tours:corporate_landing')
        response = self.client.get(landing_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bespoke Corporate Retreats')

        # Test lookup with valid reference code -> redirects to detail view
        lookup_response = self.client.get(landing_url, {'ref': tour.reference_code})
        expected_url = reverse('tours:corporate_detail', kwargs={'reference': tour.reference_code})
        self.assertRedirects(lookup_response, expected_url)

        # Test lookup with invalid reference code -> renders error message
        invalid_response = self.client.get(landing_url, {'ref': 'INVALID-REF-CODE'})
        self.assertEqual(invalid_response.status_code, 200)
        self.assertContains(invalid_response, "No corporate package found for reference code")
