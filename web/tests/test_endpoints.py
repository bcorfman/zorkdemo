from unittest import mock

import hug

from web.app import api


class FakeAdventure:
    responses = {
        "look": "**Snowy Woods**\n Whose woods these are I _think_ I know.",
    }

    def __init__(self, *arg, **kwargs):
        pass

    def execute(self, data):
        return self.responses.get(data[0], f"I really don't know how to {data[0]}.")

    def admin_save(self) -> bytes:
        return b"42"

    def admin_load(self, save_data: bytes):
        return

    @property
    def current_room(self):
        class FakeLocation:
            @property
            def description(self):
                return FakeAdventure.responses["look"]

        return FakeLocation()


def test_health_check():
    result = hug.test.get(api, url="/HEALTH-CHECK")
    assert result.status == hug.status.HTTP_200


def test_index():
    with mock.patch("web.app.Adventure", FakeAdventure):
        result = hug.test.get(api, url="/")
        assert result.status == hug.status.HTTP_200


def test_api():
    with mock.patch("web.app.Adventure", FakeAdventure):
        result = hug.test.post(api, url="/api", params={"input_data": "dance"})
        assert result.status == hug.status.HTTP_200
        assert result.data == {
            "input": "dance",
            "output": "<p>I really don&rsquo;t know how to dance.</p>",  # smarty quotes
        }
        result = hug.test.post(api, url="/api", params={"input_data": "look"})
        assert result.status == hug.status.HTTP_200
        # tests for <br /> on \n now
        assert result.data == {
            "input": "look",
            "output": "<p><strong>Snowy Woods</strong><br />\n Whose woods these are I <em>think</em> I know.</p>",
        }
