import unittest

from app import app


class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_and_health(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/health").json, {"status": "ok"})

    def test_normal_subnet(self):
        response = self.client.post("/api/subnets", json={"cidr": "192.168.10.42/24"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["network"], "192.168.10.0/24")
        self.assertEqual(response.json["broadcast_address"], "192.168.10.255")
        self.assertEqual(response.json["usable_hosts"], 254)

    def test_point_to_point_and_single_host(self):
        pair = self.client.post("/api/subnets", json={"cidr": "10.0.0.0/31"}).json
        single = self.client.post("/api/subnets", json={"cidr": "10.0.0.1/32"}).json
        self.assertEqual((pair["first_usable"], pair["last_usable"], pair["usable_hosts"]),
                         ("10.0.0.0", "10.0.0.1", 2))
        self.assertEqual((single["first_usable"], single["last_usable"], single["usable_hosts"]),
                         ("10.0.0.1", "10.0.0.1", 1))

    def test_invalid_input(self):
        for payload in ({"cidr": "999.1.1.1/24"}, {"cidr": "192.168.1.1"}, {}, {"cidr": 5}):
            with self.subTest(payload=payload):
                response = self.client.post("/api/subnets", json=payload)
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
