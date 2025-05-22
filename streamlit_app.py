import streamlit as st
import pandas as pd
import random

# タイトルと説明
st.set_page_config(page_title="緑リープ暗記アプリ", layout="wide")
st.title("🌿 緑リープ英単語テスト")
st.markdown("Part 1〜4の単語から出題されます。範囲を選んでテストを開始してください。")

# アップロード済みファイルのパス
FILE_PATHS = [
    "リープベーシック見出語・用例リスト(Part 1).xlsx",
    "リープベーシック見出語・用例リスト(Part 2).xlsx",
    "リープベーシック見出語・用例リスト(Part 3).xlsx",
    "リープベーシック見出語・用例リスト(Part 4).xlsx"
]

@st.cache_data
def load_data():
    dfs = []
    for file in FILE_PATHS:
        df = pd.read_excel(file)
        df.columns = [str(c).strip() for c in df.columns]  # 列名の空白除去
        dfs.append(df)
    df_all = pd.concat(dfs, ignore_index=True)
    return df_all

# データ読み込み
df = load_data()

# 列名確認（デバッグ用）
# st.write("列名:", df.columns.tolist())

# 出題範囲設定（Group No. に基づく）
min_no = int(df["Group No."].min())
max_no = int(df["Group No."].max())
start = st.number_input("開始No.", min_value=min_no, max_value=max_no, value=min_no)
end = st.number_input("終了No.", min_value=start, max_value=max_no, value=min(start+9, max_no))
question_count = st.slider("出題数", min_value=1, max_value=20, value=5)

# 出題データ抽出
df_range = df[(df["Group No."] >= start) & (df["Group No."] <= end)].reset_index(drop=True)

if st.button("テスト開始"):
    if df_range.empty:
        st.warning("この範囲には単語が存在しません。")
    else:
        quiz_data = df_range.sample(n=min(question_count, len(df_range))).reset_index(drop=True)
        score = 0

        for i, row in quiz_data.iterrows():
            st.markdown(f"### Q{i+1}: {row['語の意味']} に当てはまる英単語は？")
            user_input = st.text_input(f"あなたの答え（Q{i+1}）", key=f"input_{i}")

            if user_input:
                correct = row["単語"].strip().lower()
                if user_input.strip().lower() == correct:
                    st.success("正解！")
                    score += 1
                else:
                    st.error(f"不正解。正解は **{correct}** です。")

        st.markdown("---")
        st.subheader(f"✅ 正解数: {score} / {len(quiz_data)}")
