# import pytest
#
# from app.infrastructure.server.routes import USER_PATH
#
# @pytest.mark.asyncio
# async def test_post_success(web_client, user_post):
#
#     # BASELINE
#     resp = await web_client.get(USER_PATH)
#     response_body = await resp.json()
#     baseline_size = len(response_body["data"])
#
#     # POST
#     resp = await web_client.post(PUBLIC_USER, json=user_post)
#     assert resp.status == 200
#     new_user = (await resp.json())["data"]
#     assert set(new_user) == key_set
#
#     # NEW USER INSERTED
#     resp = await web_client.get(PUBLIC_USER)
#     response_body = await resp.json()
#     assert len(response_body["data"]) == baseline_size + 1
