from django.test import TestCase
from catalog.models import Product
from datetime import date

class ProductModelTest(TestCase):
    def setUp(self):
        """Inisialisasi beberapa produk Nike sebagai data awal"""
        self.products = [
            {
                "image": "https://static.nike.com/a/images/t_PDP_936_v1/f_auto,q_auto:eco/8d2ce6b7-7fce-4c9a-8fbf-b8505665c21f/NIKE+X+LEGO+COLLECTION+JERSEY.png",
                "name": "Nike x LEGO® Collection Older Kids' Dri-FIT Jersey",
                "brand": "Nike",
                "description": """Welcome to the Nike x LEGO® World! Take your game to out-of-this-world levels of play in this roomy, sweat-wicking knit jersey.

Colour Shown: Brave Blue/Cobalt Blaze/Cobalt Blaze
Style: HV6734-477
Country/Region of Origin: Laos, Thailand""",
                "price": 549000,
                "category": "Jersey",
                "stock": 111,
                "release_date": date(2025, 10, 23),
                "is_available": True,
            },
            {
                "image": "https://static.nike.com/a/images/t_PDP_936_v1/f_auto,q_auto:eco/23ad9950-6732-4fd1-aea2-88221492b2b4/AS+KB+M+NK+DF+TEE+M90+SIG.png",
                "name": "Kobe Men's Dri-FIT Basketball T-Shirt",
                "brand": "Nike",
                "description": """The Kobe signature tee goes beyond the basics with sweat-wicking Dri-FIT technology and a roomy fit to help you stay dry and comfortable.

Colour Shown: Court Purple
Style: IM0321-504
Country/Region of Origin: China""",
                "price": 549000,
                "category": "Jersey",
                "stock": 169,
                "release_date": date(2025, 10, 23),
                "is_available": True,
            },
            {
                "image": "https://static.nike.com/a/images/t_PDP_936_v1/f_auto,q_auto:eco/d1e47a87-aea4-4fe2-a341-72320bbc5820/W+NK+DF+CROSSOVER+5%22+SHORT.png",
                "name": "Nike Crossover Women's Dri-FIT 12.5cm (approx.) Basketball Shorts",
                "brand": "Nike",
                "description": """Wider through the legs and hips, these lightweight, sweat-wicking Crossover Shorts help you move freely up and down the court. An updated drawcord can be tied inside or outside for comfort and style.

Colour Shown: White/Black/Black
Style: FV8505-100
Country/Region of Origin: Vietnam""",
                "price": 569000,
                "category": "Pants",
                "stock": 119,
                "release_date": date(2025, 10, 23),
                "is_available": True,
            },
            {
                "image": "https://static.nike.com/a/images/t_PDP_936_v1/f_auto,q_auto:eco/7c9b7a92-4acc-4da5-b1be-92bc7b32853f/AS+LJ+M+NK+8IN+SHORT.png",
                "name": "LeBron Men's 20cm (approx.) Basketball Shorts",
                "brand": "Nike",
                "description": """Celebrate LeBron's reign with these 20cm (approx.) basketball shorts. Two layers of structured mesh bring a premium feel, while a "Forever King" label pays tribute to his long-standing dominance of the court.

Colour Shown: Sail/Dark Team Red
Style: HV3395-133
Country/Region of Origin: China""",
                "price": 999000,
                "category": "Pants",
                "stock": 130,
                "release_date": date(2025, 10, 23),
                "is_available": True,
            },
        ]

        # Buat semua produk ke database
        for p in self.products:
            Product.objects.create(**p)

    def test_product_count(self):
        """Pastikan semua produk berhasil disimpan"""
        self.assertEqual(Product.objects.count(), 4)

    def test_product_fields_content(self):
        """Pastikan data pertama sesuai dengan yang diinput"""
        product = Product.objects.first()
        self.assertEqual(product.brand, "Nike")
        self.assertIn("LEGO", product.name)
        self.assertTrue(product.is_available)
        self.assertGreater(product.price, 0)

    def test_str_representation(self):
        """Pastikan __str__ di model menampilkan nama produk"""
        product = Product.objects.first()
        self.assertEqual(str(product), product.name)

    def test_category_filter(self):
        """Pastikan filter kategori berfungsi"""
        Jersey = Product.objects.filter(category="Jersey")
        Pants = Product.objects.filter(category="Pants")
        self.assertEqual(Jersey.count(), 2)
        self.assertEqual(Pants.count(), 2)
