import json
import os
import pathlib
import atexit

from urllib import request
from urllib.parse import urlparse

from mitmproxy import http
from mitmproxy import ctx

# Set up storage for previously swiped users
swiped_users = {"likes": set(), "passes": set()}

# Load previously swiped users from disk
swiped_users_file_path = "./data/swiped-users.json"
if os.path.exists(swiped_users_file_path):
    with open(swiped_users_file_path) as f:
        swiped_users_from_persist = json.load(f)

        swiped_users = {
            "likes": set(swiped_users_from_persist["likes"]),
            "passes": set(swiped_users_from_persist["passes"])
        }

# Save swiped user list to disk
# TODO: something about this doesn't seem to be working properly currently, doesn't seem to save the likes/passes
def save_swiped_users():
    with open(swiped_users_file_path, "w") as f:
        json.dump({
            "likes": list(swiped_users["likes"]),
            "passes": list(swiped_users["passes"])
        }, f, indent=2)

atexit.register(save_swiped_users)

def check_user_swiped(user_id):
    if user_id in swiped_users["likes"]:
        print(f"You have already swiped 'like' on {user_id}")

    if user_id in swiped_users["passes"]:
        print(f"You have already swiped 'pass' on {user_id}")

# Save user JSON to disk
def save_user(user):
    user_identifier = f"{user['user']['name']}-{user['user']['_id']}"
    user_file_path = f"./data/{user_identifier}.json"

    ctx.log.info(f"Saving user: {user_identifier}")

    data_path = pathlib.Path("./data")
    if not data_path.exists():
        data_path.mkdir()

    with open(user_file_path, "w") as f:
        json.dump(user, f, indent=2)

    # Check if user has photos
    if "photos" in user["user"] and user["user"]["photos"]:
        # TODO: can we make this part run async so that it doesn't block the request?
        # Create directory for user's photos
        photos_dir = pathlib.Path(user_file_path).parent / "photos" / user_identifier
        if not photos_dir.exists():
            photos_dir.mkdir()

        # Save user's photos to disk
        for photo in user["user"]["photos"]:
            # TODO: Check if we have saved the photo already, and if so, skip downloading it again
            photo_file_path = photos_dir / f"{photo['id']}.jpg"

            if not pathlib.Path(photo_file_path).exists():
                ctx.log.info(f"Saving photo: {photo_file_path}")
                with request.urlopen(photo["url"]) as response, open(photo_file_path, "wb") as f:
                    f.write(response.read())
            else:
                ctx.log.info(f"Photo already saved: {photo_file_path}, skipping.")

# def request(flow: http.HTTPFlow) -> None:
#     # Check if this is a request to the Tinder API
#     if flow.request.pretty_host.endswith("api.gotinder.com"):
#         # TODO: Modify the request as desired
#         # flow.request.headers["X-Custom-Header"] = "My custom value"

def response(flow: http.HTTPFlow) -> None:
    # Check if this is a response from the Tinder API
    if flow.request.pretty_host.endswith("api.gotinder.com"):
        # Capture the response data
        # ctx.log.info(flow.response.headers)
        # ctx.log.info(flow.response.content)

        pretty_path = urlparse(flow.request.path).path

        ctx.log.info(f"path_components: {flow.request.path_components} ({flow.request.path}) ({pretty_path})")

        # Pass
        if flow.request.path_components[0] == "pass":
            ctx.log.info(f"Swiped left! (pass) ({flow.request.path})")

            user_id = flow.request.path_components[1]
            check_user_swiped(user_id)
            swiped_users["passes"].add(user_id)

        # Like
        elif flow.request.path_components[0] == "like":
            ctx.log.info(f"Swiped right! (like) ({flow.request.path})")

            user_id = flow.request.path_components[1]
            check_user_swiped(user_id)
            swiped_users["likes"].add(user_id)

        # New user recommendations
        elif pretty_path == "/v2/recs/core":
            json_data = json.loads(flow.response.content)
            user_count = len(json_data["data"]["results"])

            ctx.log.info(f"Received a new batch of {user_count} users to swipe on!")

            for user in json_data["data"]["results"]:
                save_user(user)

        # elif flow.request.path == "/v2/meta":
        #     if flow.response.content is not None:
        #         # Parse the JSON string into a dictionary
        #         json_data = json.loads(flow.response.content)
        #
        #         ctx.log.info("Before modification:")
        #         ctx.log.info(json_data["data"]["fast_match"]["secret_admirer"])
        #
        #         # Modify the dictionary
        #         json_data["data"]["fast_match"]["secret_admirer"]["enabled"] = True
        #         json_data["data"]["fast_match"]["secret_admirer"]["fetch_secret_admirer_on_card"] = 1
        #         json_data["data"]["fast_match"]["secret_admirer"]["max_likes_count"] = 1
        #         json_data["data"]["fast_match"]["secret_admirer"]["min_likes_count"] = 1
        #         json_data["data"]["fast_match"]["secret_admirer"]["reveal_like_min_likes_count"] = 1
        #
        #         # "levers": {
        #         # "unlimited_likes.in_app_enabled": {
        #         #     "p_id": "",
        #         #     "value": false
        #         # },
        #         # "unlimited_likes.in_app_like_threshold": {
        #         #     "p_id": "",
        #         #     "value": 5
        #         # },
        #         # "unlimited_likes.in_app_time_period": {
        #         #     "p_id": "",
        #         #     "value": 86400
        #         # }
        #
        #         # json_data["data"]["levers"]["unlimited_likes.in_app_enabled"]["p_id"] = ""
        #         # json_data["data"]["levers"]["unlimited_likes.in_app_enabled"]["value"] = True
        #
        #         # json_data["data"]["levers"]["unlimited_likes.in_app_like_threshold"]["p_id"] = ""
        #         # json_data["data"]["levers"]["unlimited_likes.in_app_like_threshold"]["value"] = 5
        #
        #         # json_data["data"]["levers"]["unlimited_likes.in_app_like_threshold"]["p_id"] = ""
        #         # json_data["data"]["levers"]["unlimited_likes.in_app_like_threshold"]["value"] = 86400
        #
        #         ctx.log.info("After modification:")
        #         ctx.log.info(json_data["data"]["fast_match"]["secret_admirer"])
        #
        #         # Convert the dictionary back to a JSON string
        #         flow.response.content = json.dumps(json_data).encode()