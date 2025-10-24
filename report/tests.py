from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from report.models import Report
from review.models import Review
from catalog.models import Product

class ReportViewsTest(TestCase):
    def setUp(self):
        # Create normal user and admin user
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.admin = User.objects.create_superuser(username="admin", password="password123", email="admin@example.com")

        # Create a sample product and review
        self.product = Product.objects.create(name="Test Product", price=10000)
        self.review = Review.objects.create(user=self.user, product=self.product, review="Nice product", rating=5)

        # Create a report by normal user
        self.report = Report.objects.create(
            reporter=self.user,
            title="Bad product",
            description="The product arrived broken",
            report_type="product",
            reported_product=self.product
        )

        self.client = Client()

    def test_show_report_authenticated_user(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse("report:show_report"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "report.html")
        self.assertIn(self.report, response.context["report_list"])

    def test_show_report_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("report:show_report"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/authentication/login/"))

    def test_create_report_ajax_success(self):
        self.client.login(username="testuser", password="password123")
        data = {
            "title": "Fake Review",
            "description": "This review is misleading",
            "report_type": "review",
            "object_id": self.review.id,
        }
        response = self.client.post(reverse("report:create_report"), data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})

    def test_create_report_ajax_invalid_form(self):
        self.client.login(username="testuser", password="password123")
        data = {"title": "", "description": ""}
        response = self.client.post(reverse("report:create_report"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", response.json())

    def test_edit_report_success(self):
        self.client.login(username="testuser", password="password123")
        url = reverse("report:edit_report", args=[self.report.id])
        data = {"title": "Updated title", "description": "Updated desc"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

        self.report.refresh_from_db()
        self.assertEqual(self.report.title, "Updated title")

    def test_edit_report_unauthorized_user(self):
        other_user = User.objects.create_user(username="other", password="password123")
        self.client.login(username="other", password="password123")
        url = reverse("report:edit_report", args=[self.report.id])
        response = self.client.post(url, {"title": "Hacked!"})
        self.assertEqual(response.status_code, 404)

    def test_delete_report_by_owner(self):
        self.client.login(username="testuser", password="password123")
        url = reverse("report:delete_report", args=[self.report.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertFalse(Report.objects.filter(id=self.report.id).exists())

    def test_delete_report_by_admin(self):
        self.client.login(username="admin", password="password123")
        report = Report.objects.create(
            reporter=self.user, title="To delete", description="desc", report_type="product", reported_product=self.product
        )
        url = reverse("report:delete_report", args=[report.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_delete_report_invalid_method(self):
        self.client.login(username="testuser", password="password123")
        url = reverse("report:delete_report", args=[self.report.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

    def test_report_detail_user_can_view_own(self):
        self.client.login(username="testuser", password="password123")
        url = reverse("report:report_detail", args=[self.report.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "report_detail.html")

    def test_report_detail_admin_can_view_any(self):
        self.client.login(username="admin", password="password123")
        url = reverse("report:report_detail", args=[self.report.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "report_detail.html")

    def test_admin_report_list_accessible_by_admin_only(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("report:admin_report_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_report_list.html")

    def test_admin_report_list_denied_for_normal_user(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse("report:admin_report_list"))
        self.assertEqual(response.status_code, 302)  # redirected due to user_passes_test

    def test_admin_report_detail_update_status(self):
        self.client.login(username="admin", password="password123")
        url = reverse("report:admin_report_detail", args=[self.report.id])
        data = {"status": "resolved"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # should redirect after update
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, "resolved")