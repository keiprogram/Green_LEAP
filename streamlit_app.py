import streamlit as st
import pandas as pd
import random

# ページ設定
st.set_page_config(page_title="緑リープ英単語テスト", layout="wide")

# タイトル
st.title("🌿 緑リープ英単語テスト")
st.markdown("Part1〜4 の緑リープ単語帳から出題します。範囲を選んで「テスト開始」を押してください。")

# 緑リープ用ファイルパス
FILE_PATHS = [
    "見出語・用例リスト(Part 1).xlsx",
    "見出語・用例リスト(Part 2).xlsx",
    "見出語・用例リスト(Part 3).xlsx",
    "見出語・用例リスト(Part 4).xlsx",
]

@st.cache_data
def load_data():
    dfs = []
    for fp in FILE_PATHS:
        df = pd.read_excel(fp)
        # 列名を文字列化・トリム
        df.columns = [str(c).strip() for c in df.columns]
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

# データ読み込み
df = load_data()

# デバッグ：列名確認
# st.write("Columns:", df.columns.tolist())

# 範囲設定（Group No. の最小・最大値で制限）
min_no = int(df["Group No."].min())
max_no = int(df["Group No."].max())
start = st.number_input("開始No.", min_value=min_no, max_value=max_no, value=min_no)
end   = st.number_input("終了No.", min_value=start, max_value=max_no, value=min(start+9, max_no))
qcount = st.slider("出題数", 1, 20, 5)

# モード選択
mode = st.radio("出題形式を選んでください", ("英語→日本語", "日本語→英語"))

# 抽出
quiz_df = df[(df["Group No."] >= start) & (df["Group No."] <= end)].reset_index(drop=True)

if st.button("テスト開始"):
    if quiz_df.empty:
        st.warning("指定範囲に単語がありません。")
    else:
        score = 0
        wrong = []
        sample_df = quiz_df.sample(n=min(qcount, len(quiz_df))).reset_index(drop=True)

        for i, row in sample_df.iterrows():
            q_text = row["単語"] if mode=="英語→日本語" else row["語の意味"]
            correct = row["語の意味"] if mode=="英語→日本語" else row["単語"]

            # 選択肢生成（正解＋3つランダム）
            choices = list(
                df[("語の意味" if mode=="英語→日本語" else "単語")].dropna().sample(3)
            )
            choices.append(correct)
            random.shuffle(choices)

            st.markdown(f"**Q{i+1}.** {q_text}")
            ans = st.radio("", choices, key=i)

            if ans == correct:
                st.success("✅ 正解！")
                score += 1
            else:
                st.error(f"❌ 不正解。正解は **{correct}** です。")
                wrong.append((q_text, correct))

            st.markdown("---")

        st.subheader(f"📊 スコア: {score} / {len(sample_df)}")
        if wrong:
            st.markdown("### ❗️ 間違えた問題")
            for q, c in wrong:
                st.markdown(f"- **{q}** → {c}")
