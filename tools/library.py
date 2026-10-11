"""無 AI、無第三方依賴的文章匯入及靜態網站建置工具。"""
import argparse
import ctypes
import json
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / '.site-tools'))
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

def traditional(text):
    try:
        from opencc import OpenCC
    except ImportError:
        pass
    else:
        return OpenCC('s2t').convert(text)
    if os.name == 'nt':
        fn = ctypes.windll.kernel32.LCMapStringEx
        fn.argtypes = [ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_wchar_p, ctypes.c_int, ctypes.c_wchar_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long]
        size = fn('zh-Hant', 0x04000000, text, len(text), None, 0, None, None, 0)
        if not size:
            raise ctypes.WinError()
        result = ctypes.create_unicode_buffer(size)
        if not fn('zh-Hant', 0x04000000, text, len(text), result, size, None, None, 0):
            raise ctypes.WinError()
        return result[:size]
    from opencc import OpenCC
    return OpenCC('s2t').convert(text)

def read_article(path):
    raw = path.read_text(encoding='utf-8')
    header, body = raw.split('\n+++\n', 1)
    data = json.loads(header.removeprefix('+++\n'))
    data['paragraphs'] = body.strip().split('\n\n')
    data['words'] = len(''.join(data['paragraphs']))
    return data

def write_article(path, data, paragraphs):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise ValueError(f'檔案已存在，請使用其他代號：{path}')
    path.write_text('+++\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n+++\n' + '\n\n'.join(paragraphs) + '\n', encoding='utf-8')

def build():
    articles = [read_article(p) for p in sorted((ROOT/'content').glob('*.md'))]
    for a in articles:
        for key in ('topic','label','summary','reviewSource'):
            a[key] = traditional(a.get(key,'')) if a.get(key) else ''
        for key in ('paragraphs','learn','improve'):
            a[key] = [traditional(s) for s in a.get(key,[])]
    ids = [a['id'] for a in articles]
    if len(ids) != len(set(ids)):
        raise ValueError('文章代號重複')
    for a in articles:
        if not all(a.get(k) for k in ('id', 'topic', 'label', 'paragraphs')):
            raise ValueError('文章缺少代號、題目、辨識名稱或全文')
        score = a.get('score')
        if score is not None and (not isinstance(score, (int,float)) or isinstance(score,bool) or score<0):
            raise ValueError('教師分數必須為非負數字或 null')
        if a.get('scoreMax') is not None and (a['scoreMax']<=0 or (score is not None and score>a['scoreMax'])):
            raise ValueError('滿分必須大於零，且不能小於分數')
    dist = ROOT/'dist'
    dist.mkdir(exist_ok=True)
    payload = json.dumps(articles, ensure_ascii=False).replace('<','\\u003c')
    (dist/'data.js').write_text('window.ARTICLES = '+payload+';\n',encoding='utf-8')
    for p in (ROOT/'web').iterdir():
        if p.is_file():
            (dist/p.name).write_bytes(p.read_bytes())
    print(f'建置完成：{len(articles)} 篇文章，{len(set(a["topic"] for a in articles))} 個題目')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('build')
    imp = sub.add_parser('import')
    imp.add_argument('docx', type=Path)
    imp.add_argument('--topic',required=True)
    imp.add_argument('--id',required=True)
    imp.add_argument('--label',default='')
    imp.add_argument('--starts',default='0',help='多篇文章的起始段落索引，以逗號分隔；預設整份 Word 一篇')
    imp.add_argument('--inspect',action='store_true')
    args = parser.parse_args()
    if args.command == 'build':
        build(); return
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*',args.id):
        parser.error('代號只可使用小寫英文字母、數字及連字號')
    with zipfile.ZipFile(args.docx) as z:
        root = ET.fromstring(z.read('word/document.xml'))
    if root.findall('.//w:tbl',NS):
        parser.error('此 Word 包含表格，請先將文章整理成一般段落，避免漏掉內容')
    ps = [''.join(t.text or '' for t in p.findall('.//w:t',NS)) for p in root.findall('.//w:body/w:p',NS)]
    if args.inspect:
        for i,p in enumerate(ps): print(f'{i}: {p[:80]}')
        return
    starts = [int(s) for s in args.starts.split(',')]
    if not ps or starts[0]!=0 or starts!=sorted(set(starts)) or starts[-1]>=len(ps):
        parser.error('分篇索引須從 0 開始，遞增且不可超過段落數')
    paths = [ROOT/'content'/f'{args.id}{"-"+str(i+1).zfill(2) if len(starts)>1 else ""}.md' for i in range(len(starts))]
    if any(p.exists() for p in paths): parser.error('已有相同代號的文章，取消匯入以保護現有內容')
    for i,(start,end,path) in enumerate(zip(starts,starts[1:]+[len(ps)],paths)):
        data = dict(id=path.stem,topic=traditional(args.topic),label=traditional(args.label or f'佳作 {i+1:02}'),score=None,scoreMax=None,summary='',learn=[],improve=[],reviewSource='待補充',source=args.docx.name)
        write_article(path,data,[traditional(p) for p in ps[start:end] if p])
    print(f'已匯入 {len(paths)} 篇；請補充內容大意與評語，再執行 build。')

if __name__ == '__main__': main()
