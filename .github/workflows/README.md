# chiikawa-playlist

めざましテレビ公式YouTubeチャンネルから、タイトルに「ちいかわ」と「期間限定」を含む
最新動画を自動検出し、`playlist.json` に書き出すリポジトリ。

VRChatワールド側は `https://raw.githubusercontent.com/<user>/<repo>/main/playlist.json`
を定期的にGETし、その内容を再生に使う想定。

## セットアップ手順

### 1. YouTube Data API キーの取得

1. https://console.cloud.google.com/ にアクセスし、Googleアカウントでログイン
2. 新規プロジェクトを作成(名前は何でもよい、例: `chiikawa-playlist`)
3. 左メニュー「APIとサービス」→「ライブラリ」を開く
4. 「YouTube Data API v3」を検索して選択し、「有効にする」をクリック
5. 「APIとサービス」→「認証情報」→「認証情報を作成」→「APIキー」を選択
6. 発行されたAPIキーをコピーしておく
   - 任意だが、「キーを制限」からAPI制限を「YouTube Data API v3」のみに絞っておくと安全

無料枠は1日10,000ユニット。`playlistItems.list` は1回1ユニットなので、
1日4回実行しても消費は4ユニット程度で全く問題にならない。

### 2. GitHubリポジトリの作成

1. GitHubで新しい**Public**リポジトリを作成(Privateだと通常のURLでは外部から読めないため必ずPublicにする)
2. このディレクトリの中身(`fetch_playlist.py`, `.github/workflows/update-playlist.yml`, `playlist.json`)をそのままpush

### 3. APIキーをGitHub Secretsに登録

1. リポジトリの「Settings」→「Secrets and variables」→「Actions」を開く
2. 「New repository secret」
   - Name: `YOUTUBE_API_KEY`
   - Value: 手順1で取得したAPIキー
3. 保存

### 4. 動作確認

1. リポジトリの「Actions」タブ→「Update Chiikawa Playlist」を選択
2. 「Run workflow」で手動実行し、正常に完了するか確認
3. 完了後、`playlist.json` の中身が更新されているか確認
4. `https://raw.githubusercontent.com/<user>/<repo>/main/playlist.json` にブラウザでアクセスし、
   JSONが正しく表示されることを確認

### 5. VRChat側の設定

- VRChat SDKの Control Panel → Security → Allowed URLs (String Loading) に
  `raw.githubusercontent.com` を追加する

## playlist.json のフォーマット

該当動画が見つかった場合:

```json
{
  "found": true,
  "title": "『ちいかわ』第xxx話「〇〇」<期間限定配信>",
  "videoId": "XXXXXXXXXXX",
  "url": "https://www.youtube.com/watch?v=XXXXXXXXXXX",
  "publishedAt": "2026-09-02T22:40:00Z"
}
```

見つからなかった場合は、前回の結果をそのまま維持する
(配信期間中に何度もActionsが走っても、既存の情報が消えないようにするため)。
一度も見つかったことがない場合のみ `{"found": false}` になる。
