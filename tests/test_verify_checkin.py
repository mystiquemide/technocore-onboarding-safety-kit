import unittest

from scripts.verify_checkin import VerificationError, find_matching_message, verify_room_payload


class VerifyCheckinTests(unittest.TestCase):
    def setUp(self):
        self.did = "did:key:z6MkExamplePublicIdentity"
        self.message = {
            "seq": 42,
            "ts": "2026-08-24T21:54:31.805052Z",
            "from": self.did,
            "text": "A useful Technocore onboarding note",
            "nonce": 123456789,
        }
        self.payload = {
            "room": "technocore",
            "count": 1,
            "last_seq": 42,
            "messages": [self.message],
        }

    def test_finds_exact_public_message(self):
        result = find_matching_message(
            self.payload["messages"],
            did=self.did,
            text=self.message["text"],
            nonce=self.message["nonce"],
            sequence=self.message["seq"],
        )
        self.assertEqual(result, self.message)

    def test_rejects_wrong_nonce(self):
        result = find_matching_message(
            self.payload["messages"],
            did=self.did,
            text=self.message["text"],
            nonce=999,
            sequence=self.message["seq"],
        )
        self.assertIsNone(result)

    def test_validates_room_and_returns_match(self):
        result = verify_room_payload(
            self.payload,
            room="technocore",
            did=self.did,
            text=self.message["text"],
            nonce=self.message["nonce"],
            sequence=self.message["seq"],
        )
        self.assertEqual(result["seq"], 42)

    def test_rejects_wrong_room(self):
        with self.assertRaises(VerificationError):
            verify_room_payload(
                self.payload,
                room="lobby",
                did=self.did,
                text=self.message["text"],
                nonce=self.message["nonce"],
                sequence=self.message["seq"],
            )

    def test_rejects_missing_messages_list(self):
        with self.assertRaises(VerificationError):
            verify_room_payload(
                {"room": "technocore", "last_seq": 42},
                room="technocore",
                did=self.did,
                text=self.message["text"],
                nonce=self.message["nonce"],
                sequence=self.message["seq"],
            )


if __name__ == "__main__":
    unittest.main()
