import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

TEST_SERVER = "http://20.244.56.144/test"

@api_view(['GET'])
def top_users(request):
    try:
        users_resp = requests.get(f"{TEST_SERVER}/users")
        if users_resp.status_code != 200:
            return Response({"error": "Failed to retrieve users"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        users = users_resp.json().get("users", {})
    except Exception:
        return Response({"error": "Error fetching users data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    user_post_counts = []
    for uid, name in users.items():
        try:
            posts_resp = requests.get(f"{TEST_SERVER}/users/{uid}/posts")
            if posts_resp.status_code == 200:
                posts = posts_resp.json().get("posts", [])
                count_posts = len(posts)
            else:
                count_posts = 0
        except Exception:
            count_posts = 0

        user_post_counts.append({
            "user_id": uid,
            "name": name,
            "post_count": count_posts
        })

    sorted_users = sorted(user_post_counts, key=lambda x: x["post_count"], reverse=True)
    top_five = sorted_users[:5]

    return Response({"top_users": top_five}, status=status.HTTP_200_OK)

@api_view(['GET'])
def top_posts(request):
    post_type = request.query_params.get("type")
    if post_type not in ["latest", "popular"]:
        return Response({"error": "Invalid type parameter. Accepted values: latest, popular"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        users_resp = requests.get(f"{TEST_SERVER}/users")
        if users_resp.status_code != 200:
            return Response({"error": "Failed to retrieve users"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        users = users_resp.json().get("users", {})
    except Exception:
        return Response({"error": "Error fetching users data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    all_posts = []
    for uid in users.keys():
        try:
            posts_resp = requests.get(f"{TEST_SERVER}/users/{uid}/posts")
            if posts_resp.status_code == 200:
                posts = posts_resp.json().get("posts", [])
                for post in posts:
                    all_posts.append(post)
        except Exception:
            continue

    if post_type == "latest":
        sorted_posts = sorted(all_posts, key=lambda x: x.get("id", 0), reverse=True)
        latest_posts = sorted_posts[:5]
        return Response({"latest_posts": latest_posts}, status=status.HTTP_200_OK)

    else:
        posts_with_comment_count = []
        for post in all_posts:
            pid = post.get("id")
            try:
                comments_resp = requests.get(f"{TEST_SERVER}/posts/{pid}/comments")
                if comments_resp.status_code == 200:
                    comments = comments_resp.json().get("comments", [])
                    post["comment_count"] = len(comments)
                else:
                    post["comment_count"] = 0
            except Exception:
                post["comment_count"] = 0
            posts_with_comment_count.append(post)

        if not posts_with_comment_count:
            return Response({"popular_posts": []}, status=status.HTTP_200_OK)

        max_comments = max(p.get("comment_count", 0) for p in posts_with_comment_count)
        popular_posts = [p for p in posts_with_comment_count if p.get("comment_count", 0) == max_comments]
        return Response({"popular_posts": popular_posts}, status=status.HTTP_200_OK)

