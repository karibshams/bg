from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from apps.tours.models import Tour, TourCategory, Destination
from apps.bookings.models import Booking
from apps.payments.models import Payment
from decimal import Decimal

User = get_user_model()

class AdminBulkActionsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin_bulk_test',
            email='admin_bulk@bhromonghuri.com',
            password='testpassword123'
        )
        self.client.force_login(self.admin_user)

        self.category = TourCategory.objects.create(name='Adventure', slug='adventure')
        self.destination = Destination.objects.create(
            name='Sylhet Tea Gardens',
            slug='sylhet-tea-gardens',
            description='Beautiful tea gardens'
        )
        self.tour = Tour.objects.create(
            title='Sylhet Green Tour',
            slug='sylhet-green-tour',
            category=self.category,
            destination=self.destination,
            price=Decimal('5000.00'),
            duration_days=3
        )
        self.booking = Booking.objects.create(
            tour=self.tour,
            customer_name='Test Customer',
            customer_email='test@example.com',
            customer_phone='01711111111',
            unit_price=Decimal('5000.00'),
            total_amount=Decimal('5000.00'),
            num_travelers=1
        )
        self.payment = Payment.objects.create(
            booking=self.booking,
            amount=Decimal('5000.00'),
            transaction_id='TRX12345678',
            payment_method='bKash'
        )

    def test_admin_payments_changelist_has_bulk_delete_and_actions(self):
        """Verify payments changelist has the enhanced bulk action toolbar and direct delete button."""
        response = self.client.get('/admin/payments/payment/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        
        # Verify bulk action toolbar elements
        self.assertIn('Bulk Actions', content)
        self.assertIn('Delete Selected Items', content)
        self.assertIn('Apply Action', content)
        self.assertIn('admin-bulk-actions-toolbar', content)
        self.assertIn('btn-bulk-delete', content)
        self.assertIn('btn-execute-action', content)
        self.assertIn('action-counter', content)
        self.assertIn('value="delete_selected"', content)
        # Verify quick actions for payments
        self.assertIn('Quick Approve', content)
        self.assertIn('Quick Reject', content)

    def test_admin_bookings_changelist_has_bulk_delete(self):
        """Verify bookings changelist has the direct bulk delete option."""
        response = self.client.get('/admin/bookings/booking/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Delete Selected Items', content)
        self.assertIn('btn-bulk-delete', content)
        self.assertIn('Apply Action', content)
        self.assertIn('Quick Confirm', content)

    def test_admin_tours_changelist_has_bulk_delete(self):
        """Verify tours changelist has the bulk actions bar and delete button."""
        response = self.client.get('/admin/tours/tour/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Delete Selected Items', content)
        self.assertIn('btn-bulk-delete', content)
        self.assertIn('btn-execute-action', content)

    def test_admin_destinations_changelist_has_bulk_delete(self):
        """Verify destinations changelist has bulk actions."""
        response = self.client.get('/admin/tours/destination/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Delete Selected Items', content)
        self.assertIn('btn-bulk-delete', content)

    def test_bulk_delete_execution_flow(self):
        """Test that selecting items and executing bulk delete actually deletes them upon confirmation."""
        d1 = Destination.objects.create(name='Temp Dest 1', slug='temp-dest-1', description='Temp')
        d2 = Destination.objects.create(name='Temp Dest 2', slug='temp-dest-2', description='Temp')
        
        # 1. Initiate delete_selected action
        post_data = {
            'action': 'delete_selected',
            'select_across': '0',
            'index': '0',
            '_selected_action': [str(d1.id), str(d2.id)]
        }
        confirm_resp = self.client.post('/admin/tours/destination/', post_data)
        self.assertEqual(confirm_resp.status_code, 200)
        self.assertIn('Are you sure', confirm_resp.content.decode('utf-8'))
        
        # 2. Confirm deletion
        post_data['post'] = 'yes'
        exec_resp = self.client.post('/admin/tours/destination/', post_data, follow=True)
        self.assertEqual(exec_resp.status_code, 200)
        
        # Verify objects are removed from the database
        self.assertFalse(Destination.objects.filter(id=d1.id).exists())
        self.assertFalse(Destination.objects.filter(id=d2.id).exists())
