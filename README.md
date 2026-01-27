<div id="top"></div>

## 技術スタック
- **言語**: 
  - Python 3.11
- **GUI / UI**: 
  - [Kivy](https://kivy.org/) / [KivyMD](https://kivymd.readthedocs.io)（マテリアルデザインを用いたアプリUI）
- **データ分析 / 計算**:
  - [pandas](https://pandas.pydata.org)（データ解析・処理）
  - [NumPy](https://numpy.org)（数値計算）
- **データ可視化**:
  - [Matplotlib](https://matplotlib.org)（3Dプロット・グラフ描画）
  - [Plotly](https://plotly.com)（インタラクティブなグラフ）
- **API**:
  - [Open-Meteo](https://open-meteo.com)（気象データ取得）
  - [geopy](https://geopy.readthedocs.io)（Nominatimを用いたジオコーディング）
- **開発 / ビルドツール**
  - [Buildozer](https://developer.android.com/?hl=ja)（PythonのAndroidアプリパッケージ化ツール）
  - Docker / Ubuntu (Buildozer実行環境)
- **ネットワーク / その他**:
  - [Requests](https://requests.readthedocs.io)（HTTP通信）
  - certifi / ssl（セキュリティ通信）
  - threading（マルチスレッド処理）

## 対応プラットフォーム
- **Android**
- **Windows**

## 目次
1. [Headache Monitor](#headache-monitor)
2. [ディレクトリ構成](#ディレクトリ構成)
3. [インストール](#インストール)
4. [開発者向けセットアップ](#開発者向けセットアップ)

## Headache Monitor
頭痛と気象情報をモニターし相関分析することで頭痛予測をお手伝いします<br>
graph機能: 指定期間の気圧/湿度を取得しPlotlyでインタラクティブなグラフを作成<br>
log機能: 頭痛レベルを記録し気圧/気圧変化/湿度との相関を分析しMatplotlibでグラフによる可視化<br>
pythonのみでWindowsとAndroidの両プラットフォームで動作します

<img src="https://github.com/user-attachments/assets/60137e2b-9661-4fc9-9f14-e02c6a9a255f" width=90%>
<img src="https://github.com/user-attachments/assets/92534c6e-f387-440d-96f9-04d2f4b1b8f3" width=90%>

<p align="right">(<a href="#top">トップへ</a>)</p>

## ディレクトリ構成

<!-- Treeコマンドを使ってディレクトリ構成を記載 -->
```text
headache_monitor/
├── src/
│   ├── asset/
│   │   ├── my_layout.kv
│   │   └── NotoSansJP.ttf
│   ├── headache_log.py
│   ├── main.py
│   └── weather_graph.py
├── .gitignore
├── README.md
└── requirements.txt
```
<small>※log機能実行時に headache_analysis_data.csv 自動生成</small>
<p align="right">(<a href="#top">トップへ</a>)</p>

## インストール
- **Android**
  - [Releases](../../releases)から headache_monitor_android_vx.x.x.apk をダウンロード
- **Windows**
  - [Releases](../../releases)から headache_monitor_windows_vx.x.x.zip をダウンロード
  - main.exeを実行
<p align="right">(<a href="#top">トップへ</a>)</p>

## 開発者向けセットアップ
```bash
# リポジトリのクローン
git clone github.com

# 依存ライブラリのインストール
pip install -r requirements.txt

# 実行
python main.py
```
<p align="right">(<a href="#top">トップへ</a>)</p>
