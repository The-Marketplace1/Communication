import unittest
from src.errors.exceptions import ValidationError
from src.privacy.masking import mask_phone_number
from src.validation.validators import phone_number
class ValidationTests(unittest.TestCase):
    def test_accepts_e164_phone_number(self) -> None:
        self.assertEqual(phone_number("+2348012345678"), "+2348012345678")
    def test_rejects_unstructured_phone_number(self) -> None:
        with self.assertRaises(ValidationError):
            phone_number("08012345678")
    def test_masks_all_but_last_two_digits(self) -> None:
        self.assertEqual(mask_phone_number("+2348012345678"), "+***********78")
if __name__ == "__main__":
    unittest.main()

