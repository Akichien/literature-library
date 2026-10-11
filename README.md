# 文學佳作

高中中文寫作參考網站。按作文題目分類閱讀佳作，每篇顯示教師分數、內容大意、值得學習之處及有待改善之處。

學生網站：https://chiencl.github.io/literature-library/

## 新增文章或補分數

1. 在網站開啟「教師整理工具」，選擇現有文章修改，或填寫新文章。
2. 新題目直接填入「作文題目」即可；同題目文章會自動歸類。教師分數留空即顯示「未評分」。
3. 下載文章檔，前往 https://github.com/chiencl/literature-library/upload/main/content 上傳到 `content` 資料夾。
4. 點擊 **Commit changes** 儲存。GitHub Actions 會自動建置並更新網站，毋須 AI，也不用手動上傳網站檔案。
5. 修改已有文章時使用相同代號覆蓋；新增文章使用新的代號。發佈進度可在儲存庫的 Actions 查看。

原文只進行繁體轉換，原有詞句、標點、錯字及不清標記保留。首批 9 篇賞析為一次性 AI 參考，未經教師覆核；教師可修改評語並更改來源標記。

## 本機工具

`content/*.md` 是每篇獨立的文章檔，`web` 是網站版面，`tools/library.py` 匯入 Word 及建置 `dist`。自動發佈會安裝 OpenCC 統一繁體，處理「之後」「白髮」等詞語。Windows 本機未安裝 OpenCC 時可用內建轉換；建議安裝 OpenCC 以得到一致結果。

```powershell
python -X utf8 tools/library.py build
python -m http.server 8765 --bind 127.0.0.1 --directory dist
```

匯入新的 Word：

```powershell
python -X utf8 tools/library.py import '新佳作.docx' --topic '新的題目' --id new-topic-01 --label '佳作一'
```

一份 Word 有多篇時，先加 `--inspect` 查看段落索引，再用 `--starts '0,12,25'` 指定各篇起始段落。匯入工具不猜分篇，也不覆蓋現有文章。
