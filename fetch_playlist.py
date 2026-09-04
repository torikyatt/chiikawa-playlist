#!/usr/bin/env python3
"""
めざましテレビ公式YouTubeチャンネルから、
タイトルに「ちいかわ」と「期間限定」を含む最新動画を1件抽出し、
playlist.json に書き出すスクリプト。

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
MAX_RESULTS = 20  # 直近何件をチェック対象にするか
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "playlist.json")

TITLE_KEYWORDS = ["ちいかわ", "期間限定"]


def fetch_recent_uploads(api_key: str) -> list:
    params = {
        "part": "snippet",
        "playlistId": UPLOADS_PLAYLIST_ID,
        "maxResults": str(MAX_RESULTS),
        "key": api_key,
    }
    url = "https://www.googleapis.com/youtube/v3/playlistItems?" + urllib.parse.urlencode(params)

    with urllib.request.urlopen(url) as res:
        data = json.load(res)

    return data.get("items", [])


def find_target_video(items: list):
    for item in items:
        snippet = item.get("snippet", {})
        title = snippet.get("title", "")

        if all(keyword in title for keyword in TITLE_KEYWORDS):
            video_id = snippet.get("resourceId", {}).get("videoId")
            if not video_id:
                continue
            return {
                "found": True,
                "title": title,
                "videoId": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "publishedAt": snippet.get("publishedAt", ""),
            }
    return None


def load_previous_result() -> dict:
    if not os.path.exists(OUTPUT_PATH):
        return {"found": False}
    try:
        with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"found": False}


def main():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("YOUTUBE_API_KEY が設定されていません", file=sys.stderr)
        sys.exit(1)

    items = fetch_recent_uploads(api_key)
    result = find_target_video(items)

    if result is None:
        # 該当なし: 前回の結果をそのまま維持する(期間限定配信がまだ続いている可能性があるため)
        result = load_previous_result()
        result["found"] = result.get("found", False)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
