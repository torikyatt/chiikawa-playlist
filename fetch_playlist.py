#!/usr/bin/env python3
"""
めざましテレビ公式YouTubeチャンネルから、
タイトルに「ちいかわ」と「限定配信」を含む動画(=現在公開中の見逃し配信)を
すべて抽出し、新しい順に並べて playlist.json に書き出すスクリプト。

必要な環境変数:
  YOUTUBE_API_KEY  ... YouTube Data API v3 のAPIキー
"""

import json
import os
import sys
import urllib.request
import urllib.parse

CHANNEL_ID = "UCrrsHarrLoiLTqu1LHxDJpw"  # めざましテレビ 公式YouTube
UPLOADS_PLAYLIST_ID = "UU" + CHANNEL_ID[2:]  # UC... -> UU... がアップロード一覧プレイリストID
MAX_TOTAL_RESULTS = 100  # 直近何件をチェック対象にするか
PAGE_SIZE = 50  # YouTube APIの1回あたり上限
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "playlist.json")

TITLE_KEYWORDS = ["ちいかわ", "限定配信"]


def fetch_recent_uploads(api_key: str) -> list:
    items = []
    page_token = None

    while len(items) < MAX_TOTAL_RESULTS:
        params = {
            "part": "snippet",
            "playlistId": UPLOADS_PLAYLIST_ID,
            "maxResults": str(PAGE_SIZE),
            "key": api_key,
        }
        if page_token:
            params["pageToken"] = page_token

        url = "https://www.googleapis.com/youtube/v3/playlistItems?" + urllib.parse.urlencode(params)

        with urllib.request.urlopen(url) as res:
            data = json.load(res)

        items.extend(data.get("items", []))

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return items[:MAX_TOTAL_RESULTS]


def find_target_videos(items: list) -> list:
    """条件に一致する動画を全て抽出し、公開日時の新しい順に並べて返す"""
    results = []

    for item in items:
        snippet = item.get("snippet", {})
        title = snippet.get("title", "")

        if not all(keyword in title for keyword in TITLE_KEYWORDS):
            continue

        video_id = snippet.get("resourceId", {}).get("videoId")
        if not video_id:
            continue

        results.append({
            "title": title,
            "videoId": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "publishedAt": snippet.get("publishedAt", ""),
        })

    # 新しい順(publishedAtの降順)に並べる。空文字は最後に回す。
    results.sort(key=lambda v: v["publishedAt"], reverse=True)
    return results


def load_previous_items() -> list:
    if not os.path.exists(OUTPUT_PATH):
        return []
    try:
        with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("items", [])
    except (json.JSONDecodeError, OSError):
        return []


def main():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("YOUTUBE_API_KEY が設定されていません", file=sys.stderr)
        sys.exit(1)

    uploads = fetch_recent_uploads(api_key)
    items = find_target_videos(uploads)

    if not items:
        # 該当なし: 前回の結果をそのまま維持する(取得エラーなどで一時的に0件になった場合の保険)
        items = load_previous_items()

    result = {"items": items}

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
