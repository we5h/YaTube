from http import HTTPStatus

from django.test import Client, TestCase


class StaticURLTests(TestCase):
    """Класс проверки URL's"""

    def setUp(self):
        self.guest_client = Client()

    def test_task_url_exists_at_desired_location(self):
        """Проверка доступа URL's для всех"""
        address_dict = {
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK
        }
        for address, code in address_dict.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_task_correct_template(self):
        """Тест соответсвия адреса шаблону"""
        address_temp = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for address, template in address_temp.items():
            with self.subTest(adress=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
