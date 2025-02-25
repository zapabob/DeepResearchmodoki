import pytest
from playwright.sync_api import Page, expect
import os
import json
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

def test_research_workflow(page: Page):
    # フロントエンドにアクセス
    page.goto("http://localhost:3000")
    
    # タイトルの確認
    expect(page.get_by_text("Web Deep Research")).to_be_visible()
    
    # 検索フォームの入力
    page.fill('input[name="query"]', "人工知能の最新動向")
    page.click('text="深層検索を有効にする"')
    
    # フィルターの選択
    page.click('text="academic"')
    page.click('text="news"')
    
    # 検索の実行
    page.click('text="検索開始"')
    
    # ローディング表示の確認
    expect(page.get_by_text("検索中...")).to_be_visible()
    
    # 結果の表示を待機
    page.wait_for_selector('text="分析結果"')
    
    # 結果の各セクションを確認
    expect(page.get_by_text("要約")).to_be_visible()
    expect(page.get_by_text("キーワード")).to_be_visible()
    expect(page.get_by_text("感情分析")).to_be_visible()
    expect(page.get_by_text("主要な洞察")).to_be_visible()
    
    # 知識グラフの表示を確認
    expect(page.get_by_text("知識グラフ")).to_be_visible()
    
    # 検索結果の表示を確認
    expect(page.get_by_text("検索結果")).to_be_visible()
    
    # スクリーンショットの保存
    page.screenshot(path="test-results/research-workflow.png")

def test_error_handling(page: Page):
    # フロントエンドにアクセス
    page.goto("http://localhost:3000")
    
    # 空のクエリで検索
    page.click('text="検索開始"')
    
    # エラーメッセージの確認
    expect(page.get_by_text("検索クエリが必要です")).to_be_visible()
    
    # 無効なクエリで検索
    page.fill('input[name="query"]', " " * 10)
    page.click('text="検索開始"')
    
    # エラーメッセージの確認
    expect(page.get_by_text("有効な検索クエリを入力してください")).to_be_visible()

def test_responsive_design(page: Page):
    # モバイルビューポートの設定
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto("http://localhost:3000")
    
    # モバイル表示の確認
    expect(page.get_by_text("Web Deep Research")).to_be_visible()
    
    # タブレットビューポートの設定
    page.set_viewport_size({"width": 768, "height": 1024})
    
    # タブレット表示の確認
    expect(page.get_by_text("Web Deep Research")).to_be_visible()
    
    # デスクトップビューポートの設定
    page.set_viewport_size({"width": 1280, "height": 800})
    
    # デスクトップ表示の確認
    expect(page.get_by_text("Web Deep Research")).to_be_visible()

@pytest.fixture(autouse=True)
def setup_teardown(page: Page):
    # テスト前の準備
    os.makedirs("test-results", exist_ok=True)
    
    yield
    
    # テスト後のクリーンアップ
    if page.url != "about:blank":
        # ローカルストレージのクリア
        page.evaluate("window.localStorage.clear()")
        # クッキーのクリア
        page.context.clear_cookies() 