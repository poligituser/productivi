from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class RegistrationTests(TestCase):
    def setUp(self):
        self.url = reverse("register")
        self.data = {
            "username": "test_user",
            "email": "user@example.invalid",
            "password1": "Registration-Test!739",
            "password2": "Registration-Test!739",
        }

    def test_registration_saves_user_with_hashed_password(self):
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, reverse("registered"))
        self.assertContains(response, "Аккаунт создан")
        user = User.objects.get()
        self.assertEqual(user.username, self.data["username"])
        self.assertEqual(user.email, self.data["email"])
        self.assertIsNotNone(user.date_joined)
        self.assertNotEqual(user.password, self.data["password1"])
        self.assertTrue(user.check_password(self.data["password1"]))

    def test_invalid_data_does_not_create_user(self):
        cases = [
            ({"username": ""}, "username"),
            ({"username": "bad name"}, "username"),
            ({"email": "invalid"}, "email"),
            ({"email": ""}, "email"),
            ({"password2": "Different!739"}, "password2"),
            ({"password1": "123", "password2": "123"}, "password2"),
        ]
        for changes, field in cases:
            with self.subTest(changes=changes):
                response = self.client.post(self.url, self.data | changes)
                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context["form"].errors)
                self.assertEqual(User.objects.count(), 0)

    def test_duplicate_username_is_rejected(self):
        User.objects.create_user(username=self.data["username"].upper())
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("username", response.context["form"].errors)
        self.assertEqual(User.objects.count(), 1)

    def test_csrf_protection(self):
        client = Client(enforce_csrf_checks=True)
        response = client.get(self.url)
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, 'name="password1"')
        self.assertContains(response, 'name="password2"')
        self.assertEqual(client.post(self.url, self.data).status_code, 403)
        self.assertEqual(User.objects.count(), 0)
        data = self.data | {"csrfmiddlewaretoken": client.cookies["csrftoken"].value}
        response = client.post(self.url, data, HTTP_ORIGIN="https://other.example.invalid")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(User.objects.count(), 0)
        self.assertRedirects(client.post(self.url, data), reverse("registered"))
        self.assertEqual(User.objects.count(), 1)
