import streamlit as st
import pandas as pd
import numpy as np
import glob

# アプリ設定
st.set_page_config(page_title="English Vocabulary Test", page_icon="📝")

# カスタムCSS
st.markdown("""
<style>
body { font-family: 'Arial', sans-serif; background-color: #f5f5f5; color: #333; }
.choice-btn { background-color: #6c757d; color: white; border: none; border-radius: 5px; padding: 10px 20px; margin: 5px; font-weight: bold; cursor: pointer; }
.choice-btn:hover { background-color: #495057; }
</style>
""", unsafe_allow_html=True)

# データ読み込み（Part1〜4）
@st.cache_data
def load_data():
    # part1.xlsx, part2.xlsx, part3.xlsx, part4.xlsxを自動検出
    paths = glob.glob('part*.xlsx')
    dfs = []
    for fp in sorted(paths):
        df = pd.read_excel(fp)
        # 列数が3列以上か確認して先頭3列のみ使用
        df = df.iloc[:, :3]
        df.columns = ['No.', '単語', '語の意味']
        dfs.append(df)
    if not dfs:
        st.error("単語帳ファイルが見つかりません。part1.xlsx〜part4.xlsxを配置してください。")
        return pd.DataFrame(columns=['No.', '単語', '語の意味'])
    return pd.concat(dfs, ignore_index=True)

words_df = load_data()

# UI設定
st.title("English Vocabulary Test")
st.caption("Part1〜4 のアップロード済みExcelで学ぶ英単語テストアプリ")

# テスト形式選択
test_type = st.sidebar.radio(
    "テスト形式を選択", ["英語→日本語", "日本語→英語"]
)

# 範囲指定 (No.1〜No.100形式)
if not words_df.empty:
    max_no = int(words_df['No.'].max())
    ranges = [(i, min(i+99, max_no)) for i in range(1, max_no+1, 100)]
    labels = [f"No.{s}〜No.{e}" for s,e in ranges]
    selected = st.sidebar.selectbox("出題範囲", labels)
    selected_range = ranges[labels.index(selected)]
else:
    selected_range = (1,0)

# 出題数選択
num_questions = st.sidebar.slider("出題数", 1, 50, 10)

# フィルタリング
filtered = words_df[(words_df['No.'] >= selected_range[0]) & (words_df['No.'] <= selected_range[1])]

# テスト開始
if st.sidebar.button("テスト開始"):
    st.session_state.questions = filtered.sample(n=min(num_questions, len(filtered))).reset_index(drop=True)
    st.session_state.current = 0
    st.session_state.correct = 0
    st.session_state.wrongs = []

# 回答処理
def answer(opt):
    q = st.session_state.questions.iloc[st.session_state.current]
    correct = q['語の意味'] if test_type=='英語→日本語' else q['単語']
    if opt == correct:
        st.session_state.correct += 1
    else:
        st.session_state.wrongs.append((q['No.'], q['単語'], q['語の意味']))
    st.session_state.current += 1

# 出題
if 'questions' in st.session_state and st.session_state.current < len(st.session_state.questions):
    q = st.session_state.questions.iloc[st.session_state.current]
    prompt = q['単語'] if test_type=='英語→日本語' else q['語の意味']
    ans_col = '語の意味' if test_type=='英語→日本語' else '単語'
    pool = filtered[ans_col].drop_duplicates()
    choices = list(pool.sample(min(3, len(pool)))) + [q[ans_col]]
    np.random.shuffle(choices)

    st.subheader(f"問題 {st.session_state.current+1} / {len(st.session_state.questions)}")
    st.write(prompt)
    for c in choices:
        if st.button(c, key=f"opt_{st.session_state.current}_{c}"):
            answer(c)

# 結果表示
elif 'questions' in st.session_state:
    total = len(st.session_state.questions)
    st.success(f"テスト終了！ 正解数: {st.session_state.correct}/{total}")
    st.progress(st.session_state.correct/total)
    if st.session_state.wrongs:
        st.subheader("間違えた問題一覧")
        df_wrong = pd.DataFrame(st.session_state.wrongs, columns=['No.', '単語', '語の意味'])
        st.table(df_wrong)
    else:
        st.write("全問正解！おめでとうございます！")
